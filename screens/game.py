from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.app import App
from kivy.properties import ListProperty
from kivy.animation import Animation
from kivy.metrics import dp, sp
import json
import random
import os

from widgets.ghost import Ghost
from systems.sound_manager import SoundManager
from systems.hp_system import HPSystem
from systems.game_logic import GameLogic
from widgets.custom_ui import FloatingText

class GameScreen(Screen):
    def on_enter(self, *args):
        app = App.get_running_app()
        app.sound.play_game_bgm()

        for child in self.children:
            if isinstance(child, MainLayout):
                child.on_screen_enter()

class MainLayout(FloatLayout):
    flash_color = ListProperty([1, 0, 0, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_started = False
        self.timer_event = None
        self.spooky_timer = None
        
        self.is_paused = False 
        Window.bind(on_keyboard=self._on_keyboard)
        
        self.vocab_pool = []
        self.total_words_in_level = 0
        self.current_word = {"thai": "กำลังโหลด...", "english": "loading"}

        self.sound = App.get_running_app().sound
        self.hp = HPSystem(max_hp=3)
        self.logic = GameLogic(self.hp)

        self.time_left = 16.0  
        self.time_speed = 1.00  

        

        Clock.schedule_once(self.setup_ghost_position, 0)
        self.bind(size=self.on_resize)
        Clock.schedule_interval(self.idle_animations, 1.0)

    def on_kv_post(self, base_widget):
        # ฟังก์ชันนี้จะทำงานอัตโนมัติเมื่อ Kivy โหลด UI จากไฟล์ .kv เสร็จแล้ว
        self.time_label = self.ids.time_label
        self.time_bar = self.ids.time_bar
        self.hp_label = self.ids.hp_label
        self.score_label = self.ids.score_label
        self.combo_label = self.ids.combo_label
        self.word_label = self.ids.word_label
        self.underscore_label = self.ids.underscore_label
        self.level_label = self.ids.level_label
        self.answer_input = self.ids.answer_input
        self.scooby = self.ids.scooby
        self.pause_overlay = self.ids.pause_overlay

        # ผูกฟังก์ชันเพื่อดักข้อความเวลาพิมพ์
        self.answer_input.bind(text=self.on_text_change)
        
        # เพิ่มตัวแปรสำหรับติดตามสถานะการพิมพ์
        self._is_changing_word = False
        self._last_text_value = ""

        self.ghost = Ghost()
        self.ghost.is_paused = True
        self.add_widget(self.ghost)
        
        # จัดลำดับชั้นของหน้าต่าง Pause ให้อยู่บนสุด
        self.remove_widget(self.pause_overlay)
        self.add_widget(self.pause_overlay)
        
    def on_text_change(self, instance, value):
        # ถ้ากำลังเปลี่ยนคำศัพท์ ให้ข้ามการประมวลผล
        if getattr(self, '_is_changing_word', False):
            return
        
        # ตรวจสอบว่ามีคำศัพท์ปัจจุบันหรือไม่
        if not getattr(self, 'current_word', None):
            return
        
        english_word = self.current_word.get('english', '')
        if english_word == 'loading' or not english_word:
            return
        
        # ป้องกันการพิมพ์เกินความยาวของคำศัพท์
        max_length = len(english_word.replace(' ', ''))  # นับเฉพาะตัวอักษร ไม่รวมช่องว่าง
        if len(value) > max_length:
            # ตัดข้อความให้เหลือเฉพาะจำนวนที่อนุญาต
            value = value[:max_length]
            # อัปเดตค่าใน TextInput โดยตรง (แต่ต้องระวัง recursion)
            self._is_changing_word = True
            instance.text = value
            self._is_changing_word = False
            return
        
        # เล่นเสียงพิมพ์เฉพาะตอนที่พิมพ์จริง (ไม่ใช่ตอนลบ)
        if len(value) > len(getattr(self, '_last_text_value', '')):
            self.sound.play_typing_sound()
        self._last_text_value = value
        
        # สร้างการแสดงผล underscore ที่ปลอดภัย
        display_chars = []
        typed_idx = 0
        
        for char in english_word:
            if char == ' ':
                # แสดงช่องว่างที่กว้างขึ้นสำหรับความสวยงาม
                display_chars.append('   ')
            else:
                # ข้ามช่องว่างในคำที่พิมพ์ (เพราะเรานับเฉพาะตัวอักษร)
                while typed_idx < len(value) and value[typed_idx] == ' ':
                    typed_idx += 1
                    
                if typed_idx < len(value):
                    display_chars.append(value[typed_idx].upper())
                    typed_idx += 1
                else:
                    display_chars.append('_')
                    
        self.underscore_label.text = ' '.join(display_chars)
        
        # เปลี่ยนสีตามสถานะการพิมพ์
        if len(value.strip()) > 0:
            self.underscore_label.color = (0.4, 0.9, 1, 1)  # สีฟ้าเมื่อกำลังพิมพ์
        else:
            self.underscore_label.color = (1, 0.8, 0.2, 1)  # สีส้มเมื่อยังไม่ได้พิมพ์

    def safe_clear_input(self):
        """ฟังก์ชันสำหรับลบข้อความในช่องพิมพ์อย่างปลอดภัย"""
        self._is_changing_word = True
        self.answer_input.text = ""
        self._last_text_value = ""
        self._is_changing_word = False
        
        # รีเซ็ต underscore label ด้วย
        if hasattr(self, 'current_word') and self.current_word:
            english_word = self.current_word.get('english', '')
            if english_word and english_word != 'loading':
                display_chars = []
                for char in english_word:
                    if char == ' ':
                        display_chars.append('   ')
                    else:
                        display_chars.append('_')
                self.underscore_label.text = ' '.join(display_chars)
                self.underscore_label.color = (1, 0.8, 0.2, 1) 

    def save_highscore(self):
        highscore = 0
        try:
            if os.path.exists('highscore.json'):
                with open('highscore.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    highscore = data.get('highscore', 0)
        except Exception as e:
            print(f"Error loading highscore: {e}")

        if self.logic.score > highscore:
            try:
                with open('highscore.json', 'w', encoding='utf-8') as f:
                    json.dump({'highscore': self.logic.score}, f)
            except Exception as e:
                print(f"Error saving highscore: {e}")

    def try_spooky_event(self, dt):
        if self.is_paused or self.hp.is_dead() or not self.game_started:
            return
            
        if random.random() <= 0.20:
            event = random.choice(['thunder', 'poltergeist', 'jump_scare'])
            
            if event == 'thunder':
                self.sound.play_thunder()
                self.flash_color = [1, 1, 1, 0.9] 
                
                anim = Animation(flash_color=[0, 0, 0, 0.95], duration=0.1) + Animation(flash_color=[0, 0, 0, 0], duration=0.6)
                anim.start(self)
                
                # --- ส่วนที่แก้ใหม่ ---
                if not getattr(self, 'is_shaking', False):
                    self.is_shaking = True
                    og_pos = (self.x, self.y)
                    shake = Animation(pos=(og_pos[0]-25, og_pos[1]+25), duration=0.05) + \
                            Animation(pos=(og_pos[0]+25, og_pos[1]-25), duration=0.05) + \
                            Animation(pos=(og_pos[0]-15, og_pos[1]-15), duration=0.05) + \
                            Animation(pos=og_pos, duration=0.05)
                    
                    def reset_thunder_shake(*args):
                        self.pos = og_pos
                        self.is_shaking = False
                        
                    shake.bind(on_complete=reset_thunder_shake)
                    shake.start(self)
                
            elif event == 'poltergeist':
                self.word_label.color = (1, 1, 0.5, 1) 
                self.sound.play_poltergeist()
                # --- เปลี่ยนจากการเขย่าแกน X มาเป็นการกระพริบ (Opacity) แทน ---
                word_flicker = Animation(opacity=0.2, duration=0.05) + Animation(opacity=1, duration=0.05)
                word_flicker.repeat = True
                word_flicker.start(self.word_label)
                
                input_flicker = Animation(opacity=0.2, duration=0.05) + Animation(opacity=1, duration=0.05)
                input_flicker.repeat = True
                input_flicker.start(self.answer_input)
                
                def stop_poltergeist(*args):
                    Animation.cancel_all(self.word_label, 'opacity')
                    Animation.cancel_all(self.answer_input, 'opacity')
                    self.word_label.opacity = 1
                    self.answer_input.opacity = 1
                    self.word_label.color = (1, 1, 1, 1) 
                    
                Clock.schedule_once(stop_poltergeist, 2.0)
                
            elif event == 'jump_scare':
                scary_texts = ["BEHIND YOU!", "I SEE YOU...", "BOO!!", "ระวังข้างหลัง!!"]
                scary_label = Label(
                    text=random.choice(scary_texts),
                    font_size='80sp',
                    font_name='LEELAUIB.TTF',
                    bold=True,
                    color=(1, 0, 0, 1),
                    outline_width=4,
                    outline_color=(0, 0, 0, 1),
                    pos_hint={'center_x': 0.5, 'center_y': 0.5},
                    size_hint=(None, None)
                )
                self.add_widget(scary_label)
                self.sound.play_jumpscare()
                anim = Animation(font_size=sp(160), opacity=0, duration=0.8, transition='out_expo')
                anim.bind(on_complete=lambda *args: self.remove_widget(scary_label))
                anim.start(scary_label)

    def idle_animations(self, dt):
        if not self.is_paused and not getattr(self.ghost, 'is_paused', True):
            
            # --- แก้ไขของ Scooby ---
            # ใช้การอ้างอิงจากตำแหน่งดั้งเดิม (ยึดตามที่ตั้งไว้ใน KV ว่า pos_hint: {'y': 0.30})
            base_scooby_y = self.height * 0.30  
            anim = Animation(y=base_scooby_y + dp(10), duration=0.5) + Animation(y=base_scooby_y, duration=0.5)
            anim.start(self.scooby)

            # --- แก้ไขของผี ---
            # ใช้การอ้างอิงจากตำแหน่งดั้งเดิมที่เราตั้งไว้ใน setup_ghost_position
            base_ghost_y = base_scooby_y - dp(10) 
            g_anim = Animation(y=base_ghost_y + dp(20), duration=0.5) + Animation(y=base_ghost_y, duration=0.5)
            g_anim.start(self.ghost)

    def trigger_screen_shake(self):
        # เช็คว่าถ้าจอกำลังสั่นอยู่ ให้ข้ามไปเลย จะได้ไม่จำตำแหน่งผิด
        if getattr(self, 'is_shaking', False):
            return
            
        self.is_shaking = True
        og_pos = (self.x, self.y) # จำตำแหน่งดั้งเดิม
        
        anim = Animation(pos=(og_pos[0]-15, og_pos[1]+15), duration=0.05) + \
               Animation(pos=(og_pos[0]+15, og_pos[1]-15), duration=0.05) + \
               Animation(pos=og_pos, duration=0.05)
               
        # เมื่อสั่นจบ บังคับให้หน้าจอกลับมาจุดเดิมเป๊ะๆ พร้อมคืนค่าสถานะ
        def reset_shake(*args):
            self.pos = og_pos
            self.is_shaking = False
            
        anim.bind(on_complete=reset_shake)
        anim.start(self)

    def flash_screen(self, color=(1, 0, 0, 0.5)):
        self.flash_color = color
        anim = Animation(flash_color=[color[0], color[1], color[2], 0], duration=0.5)
        anim.start(self)

    def pop_combo_text(self):
        anim = Animation(font_size=sp(35), color=(1, 1, 0, 1), duration=0.1) + \
               Animation(font_size=sp(24), color=(0.7, 1, 0.3, 1), duration=0.2)
        anim.start(self.combo_label)

    def pop_score_text(self):
        anim = Animation(color=(1, 1, 1, 1), duration=0.1) + Animation(color=(0.3, 0.9, 0.9, 1), duration=0.3)
        anim.start(self.score_label)

    def animate_word_in(self):
        self.word_label.opacity = 0
        Animation(opacity=1, duration=0.3, transition='out_quad').start(self.word_label)

    def load_vocabulary(self, category_name, level):
        cat_map = {
            'Animals & Nature': 'nature',
            'Daily Life': 'daily',
            'Science, IT & Engineering': 'science_it'
        }
        json_key = cat_map.get(category_name, 'daily')
        
        try:
            with open('vocab_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.vocab_pool = list(data[json_key][str(level)])
            self.total_words_in_level = len(self.vocab_pool)
            random.shuffle(self.vocab_pool)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            self.vocab_pool = [{"thai": "ข้อผิดพลาดไฟล์", "english": "error"}]

    def next_word(self):
        if not self.vocab_pool:
            self.answer_input.disabled = True
            self.ghost.is_paused = True
            self.word_label.color = (0.2, 1, 0.2, 1)

            if hasattr(self, 'current_level') and self.current_level < 5:
                self.word_label.text = f"เคลียร์ด่าน {self.current_level}! เตรียมลุย..."
                self.underscore_label.text = f"คะแนนสะสม: {self.logic.score}"
                
                Animation(font_size=sp(60), duration=0.5, transition='out_bounce').start(self.word_label)
                Clock.schedule_once(self.go_to_next_level, 2.5)
            else:
                self.word_label.text = "ยินดีด้วย! คุณเคลียร์ทุกด่านแล้ว!"
                self.underscore_label.text = f"คะแนนสูงสุด: {self.logic.score}"
                
                self.save_highscore()
                
                Animation(font_size=sp(60), duration=0.5, transition='out_bounce').start(self.word_label)
                
                if self.timer_event:
                    self.timer_event.cancel()
                    self.timer_event = None
                Clock.schedule_once(self.return_to_main_menu_auto, 5.0)
            return
            
        self.current_word = self.vocab_pool.pop()
        self.safe_clear_input()
        self.update_ui()
        self.animate_word_in() 
    
    def go_to_next_level(self, dt):
        self.current_level += 1
        self.word_label.font_size = '45sp' 
        self.load_vocabulary(self.current_category, str(self.current_level))
        self.time_left = 16.0
        self.time_speed = 1.0 + (self.current_level * 0.1) 
        self.time_bar.max = 16.0
        self.hp.current_hp = self.hp.max_hp
        self.word_label.color = (1, 1, 1, 1) 
        self.ghost.reset()
        self.ghost.is_paused = False
        self.scooby.reset_to_idle()
        self.answer_input.disabled = False
        self.next_word()
        self.update_ui()
        Clock.schedule_once(self._force_focus, 0.3)

    def return_to_main_menu_auto(self, dt):
        self.reset_entire_game()
        if self.parent and hasattr(self.parent, 'manager'):
            self.parent.manager.current = 'main_menu'

    def on_screen_enter(self):
        Clock.schedule_once(lambda dt: self._force_focus(), 0.1)

    def _force_focus(self, dt=None):
        # ตรวจสอบว่าเกมไม่ได้หยุด หรือตายอยู่
        if self.is_paused or self.hp.is_dead():
            return
            
        # ถ้าไม่มีคำศัพท์เหลือแล้ว (จบด่าน) ก็ไม่ต้อง Focus
        if not self.vocab_pool and not getattr(self, 'current_word', None): 
            return

        # เปิดใช้งาน และย้ำ Focus (False แล้วค่อย True)
        self.answer_input.disabled = False
        self.answer_input.focus = False
        self.answer_input.focus = True

    def _on_keyboard(self, window, key, scancode, codepoint, modifier):
        if self.parent and hasattr(self.parent, 'manager') and self.parent.manager.current == 'game_screen':
            if key == 27:  
                self.toggle_pause()
                return True
        return False

    def toggle_pause(self):
        if self.hp.is_dead():
            return 

        self.is_paused = not self.is_paused
        if self.is_paused:
            self.safe_clear_input()
            Animation(opacity=1, duration=0.2).start(self.pause_overlay)
            self.pause_overlay.disabled = False
            self.pause_overlay.pos_hint = {'center_x': 0.5, 'center_y': 0.5} 
            self.answer_input.disabled = True
            self.ghost.is_paused = True 
        else:
            anim = Animation(opacity=0, duration=0.2)
            anim.bind(on_complete=lambda *args: setattr(self.pause_overlay, 'pos_hint', {'y': 10}))
            anim.start(self.pause_overlay)
            self.pause_overlay.disabled = True
            self.answer_input.disabled = False
            self.answer_input.focus = True
            self.ghost.is_paused = False

    def go_to_options_from_pause(self, instance):
        self.sound.play_click()
        App.get_running_app().go_to_options('game_screen')

    def quit_to_main_menu(self, instance):
        self.sound.play_click()
        self.toggle_pause() 
        self.reset_entire_game() 
        if self.parent and hasattr(self.parent, 'manager'):
            self.parent.manager.current = 'main_menu'

    def reset_entire_game(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
            self.scooby.reset_to_idle()
        if getattr(self, 'spooky_timer', None):
            self.spooky_timer.cancel()
            self.spooky_timer = None

        self.game_started = False
        self.hp = HPSystem(max_hp=3)
        self.logic = GameLogic(self.hp)
        self.time_left = 16.0
        self.time_speed = 1.00
        self.time_bar.max = 16.0
        self.ghost.reset()
        self.ghost.is_paused = True
        self.answer_input.disabled = False
        self.word_label.color = (1, 1, 1, 1)

    def update_timer(self, dt):
        if self.parent and hasattr(self.parent, 'manager') and self.parent.manager.current != 'game_screen':
            return
        if self.is_paused or self.hp.is_dead() or getattr(self.ghost, 'is_paused', False):
            return 
        if not self.game_started:
            return
            
        self.time_speed += 0.01 * dt 
        if self.time_speed > 3.0: 
            self.time_speed = 3.0
            
        self.time_left -= (self.time_speed * dt)
        
        # 1. ผีเดินเนียนๆ 60 เฟรมต่อวิ
        self.ghost.sync_position(max(0.0, self.time_left), 16.0)
        
        if self.time_left <= 0:
            self.time_left = 0
            self.on_ghost_hit() 
            return
            
        if self.time_left > 10:
            t_color = (0.2, 1, 0.2, 1) 
        elif self.time_left > 4:
            t_color = (1, 0.6, 0.2, 1) 
        else:
            t_color = (1, 0.2, 0.2, 1) 
            
        # 2. ✅ จุดแก้กระตุก! อัปเดต Text เฉพาะตอนที่ตัวเลขวินาทีเปลี่ยนเท่านั้น
        new_time_text = f"Time: {int(self.time_left)}s"
        if self.time_label.text != new_time_text:
            self.time_label.text = new_time_text
            self.time_label.color = t_color
            
        # หลอด Progress bar เลื่อนได้ลื่นๆ ไม่มีปัญหา
        self.time_bar.value = self.time_left

    def update_ui(self):
        self.hp_label.text = f"Snacks: {self.hp.current_hp}/{self.hp.max_hp}"
        self.score_label.text = f"Score: {self.logic.score}"
        self.combo_label.text = f"Combo: x{self.logic.combo_multiplier}"
        lvl = getattr(self, 'current_level', 1)
        self.level_label.text = f"STAGE {lvl}"
        self.word_label.text = f"{self.current_word['thai']}"
        
        self.on_text_change(self.answer_input, self.answer_input.text)

    def check_answer(self, instance):
        if self.hp.is_dead() or self.time_left <= 0 or self.is_paused:
            return  
        user_ans = self.answer_input.text.strip().lower() 
        if not user_ans: 
            return
            
        correct_ans = self.current_word["english"].lower()
        old_score = self.logic.score
        is_correct = self.logic.check_answer(user_ans, correct_ans)
        
        if is_correct:
            self.sound.play_correct()
            self.scooby.change_state('happy', duration=1.0)
            speed_bonus = 0
            rating_text = ""
            r_color = (1, 1, 1, 1)
            
            if self.time_left >= 10:
                speed_bonus = 30
                rating_text = "PERFECT!"
                r_color = (1, 0.8, 0.1, 1) 
            elif self.time_left >= 5:
                speed_bonus = 15
                rating_text = "GREAT!"
                r_color = (0.2, 1, 0.2, 1) 
            else:
                speed_bonus = 5
                rating_text = "GOOD!"
                r_color = (0.4, 0.9, 1, 1) 
                
            self.logic.score += speed_bonus 
            
            self.add_widget(FloatingText(rating_text, (self.center_x - dp(60), self.answer_input.y + dp(60)), color=r_color))
            
            score_diff = self.logic.score - old_score
            self.add_widget(FloatingText(f"+{score_diff} Score", (self.score_label.x, self.score_label.y)))
            self.pop_combo_text()
            self.pop_score_text()
            
            if self.logic.combo_multiplier >= 3:
                self.flash_screen((1, 0.85, 0.1, 0.6))
                self.add_widget(FloatingText("🔥 FEVER! 🔥", (self.center_x - dp(75), self.center_y), color=(1, 0.85, 0.1, 1)))
                anim = Animation(color=(1, 0.85, 0.1, 1), duration=0.1) + Animation(color=(1, 1, 1, 1), duration=0.2)
            else:
                anim = Animation(color=(0.2, 1, 0.2, 1), duration=0.1) + Animation(color=(1, 1, 1, 1), duration=0.2)
                
            anim.start(self.word_label)
            
            self.time_left = 16.0
            self.ghost.reset()
            if self.time_left > self.time_bar.max:
                self.time_bar.max = self.time_left
            self.time_bar.value = self.time_left
            self.next_word()
            Clock.schedule_once(lambda dt: self._force_focus(), 0.1)
            
        else:
            self.sound.play_wrong_answer()
            self.safe_clear_input() 
            
            anim_shake = Animation(x=self.answer_input.x-10, duration=0.05) + Animation(x=self.answer_input.x+10, duration=0.05) + Animation(x=self.answer_input.x, duration=0.05)
            anim_shake.start(self.answer_input)
            
            self.add_widget(FloatingText("MISS!", (self.center_x - dp(40), self.answer_input.y + dp(60)), color=(1, 0.2, 0.2, 1)))
            
            self.logic.combo_multiplier = 1
            
            if self.time_speed > 1.0:
                self.time_speed = 1.0 
            self.update_ui()
            
            # --- เพิ่มบรรทัดนี้ เพื่อให้เคอร์เซอร์กลับมาที่ช่องพิมพ์ทันที ---
            Clock.schedule_once(lambda dt: self._force_focus(), 0.1)
            # -----------------------------------------------------
            
            if self.hp.is_dead():
                self.trigger_game_over()

    def buy_life(self, instance):
        if self.hp.current_hp < self.hp.max_hp:
            if self.logic.score >= 50:
                self.logic.buy_life(cost=50)
                anim_heal = Animation(font_size=sp(30), color=(0,1,0,1), duration=0.1) + Animation(font_size=sp(24), color=(0.9, 0.6, 0.3, 1), duration=0.2)
                anim_heal.start(self.hp_label)
                self.update_ui()
            else:
                self.flash_shop_error()

    def get_hint(self, instance):
        if self.logic.score >= 20:
            hint = self.logic.get_hint(self.current_word["english"], cost=20)
            if hint:
                self.answer_input.text = hint
                self.update_ui()
        else:
            self.flash_shop_error()

    def buy_slow_time(self, instance):
        cost = 30
        if self.logic.score >= cost:
            self.logic.score -= cost
            if hasattr(self, 'ghost'):
                
                self.ghost.is_paused = False
            
            self.time_speed = 0.75 
            self.time_left += 5.0
            if self.time_left > 16.0:  
                self.time_left = 16.0
            self.time_bar.value = self.time_left
            
            self.flash_screen((0, 0.5, 1, 0.4))
            self.update_ui()
        else:
            self.flash_shop_error()
            
    def flash_shop_error(self):
        self.sound.play_noscore() 
        anim = Animation(color=(1, 0, 0, 1), duration=0.1) + Animation(color=(0.3, 0.9, 0.9, 1), duration=0.1)
        anim.start(self.score_label)
    
    def on_ghost_hit(self):
        if self.hp.is_dead() or getattr(self.ghost, 'is_paused', False) or self.is_paused:
            return
        self.time_left = 0
        self.hp.take_damage()
        self.scooby.change_state('scared', duration=2.5)
        self.trigger_screen_shake()
        self.flash_screen((1, 0, 0, 0.5))
        self.add_widget(FloatingText("-1 HP!", (self.hp_label.x, self.hp_label.y), color=(1,0,0,1)))
        
        self.logic.combo_multiplier = 1
        self.sound.play_wrong()
        self.ghost.is_paused = True
        self.safe_clear_input()
        self.answer_input.disabled = True 
        self.update_ui()
        
        # ✅ เพิ่มระบบเฉลยคำศัพท์ตรงนี้
        correct_ans = self.current_word.get("english", "")
        # จัดตัวอักษรให้มีช่องว่าง (เช่น A P P L E) จะได้เนียนไปกับช่องว่างเดิม
        spaced_ans = " ".join(list(correct_ans.upper()))
        self.underscore_label.text = spaced_ans
        self.underscore_label.color = (1, 0.2, 0.2, 1) # เปลี่ยนเป็นสีแดงให้รู้ว่าเฉลย
        
        if self.hp.is_dead():
            # ถ้าเลือดหมด ให้โชว์เฉลยค้างไว้ 1.5 วินาที ก่อนจะเด้งหน้า GAME OVER
            Clock.schedule_once(lambda dt: self.trigger_game_over(), 1.5)
        else:
            # ถ้าเลือดยังเหลือ ให้โชว์เฉลยค้างไว้ 2 วินาที แล้วเริ่มคำศัพท์ใหม่
            Clock.schedule_once(self.reset_ghost_after_hit, 2.0)
            
    def trigger_game_over(self):
        self.sound.play_gameover()
        
        self.word_label.text = "GAME OVER!"
        self.word_label.color = (1, 0.2, 0.2, 1)  
        
        anim_gameover = Animation(font_size=sp(70), transition='out_elastic', duration=0.8)
        anim_gameover.start(self.word_label)
        
        self.underscore_label.text = f"คะแนนสุดท้าย: {self.logic.score}"
        self.underscore_label.color = (1, 0.8, 0.2, 1) 
        
        self.answer_input.disabled = True
        self.flash_screen((0.5, 0, 0, 0.7)) 
        
        self.save_highscore()
        
        if getattr(self, 'timer_event', None):
            self.timer_event.cancel()
            self.timer_event = None
            
        if getattr(self, 'spooky_timer', None):
            self.spooky_timer.cancel()
            self.spooky_timer = None
            
        Clock.schedule_once(self.return_to_main_menu_auto, 5.0) 
    
    # ----------------------------------------------------------------------
    # บังคับขนาดผี (self.ghost) ให้เท่ากับ Scooby แบบเป๊ะๆ และล็อคตำแหน่งให้อยู่แกน Y เดียวกัน
    # ----------------------------------------------------------------------
    def setup_ghost_position(self, dt):
        self.ghost.size_hint = (None, None)
        self.ghost.pos_hint = {}
        # 1. ปรับขนาดผี (กว้าง, สูง) ตรงนี้ปรับตัวเลขให้เข้ากับสัดส่วนภาพผีได้เลยครับ
        self.ghost.size = (dp(300), dp(300)) 
        
        self.ghost.start_x = self.width + 50
        if not self.game_started:
            self.ghost.x = self.ghost.start_x
            
        self.ghost.end_x = self.scooby.right - dp(10)
        
        # 2. ปรับระดับความสูง (Y) ของผี
        # ถ้าภาพผีดู "จมดิน" ให้บวกเพิ่ม เช่น self.scooby.y + dp(20)
        # ถ้าภาพผีดู "ลอยไป" ให้ลบออก เช่น self.scooby.y - dp(20)
        base_scooby_y = self.height * 0.30
        self.ghost.y = base_scooby_y - dp(10)
    def on_resize(self, *args):
        self.setup_ghost_position(0)

    def reset_ghost_after_hit(self, dt):
        if self.hp.is_dead() or self.is_paused:
            return
        self.ghost.reset()
        Animation.cancel_all(self.ghost, 'y') 
        self.setup_ghost_position(0)
        self.ghost.is_paused = False
        self.next_word()
        self.answer_input.disabled = False
        self.answer_input.focus = True
        self.time_left = 16.0
        self.time_speed = 1.0
        self.time_bar.value = self.time_left
        Clock.schedule_once(self._force_focus, 0.2)
    def start_game(self, category, level):
        self.current_category = category
        self.current_level = int(level)
        self.word_label.font_size = '45sp' 
        self.load_vocabulary(category, level)

        self.game_started = True
        self.time_left = 16.0
        self.time_speed = 1.0
        self.logic.score = 0
        self.logic.combo_multiplier = 1
        self.hp.current_hp = self.hp.max_hp
        
        if getattr(self, 'timer_event', None):
            self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer, 1/60.0)
        
        if getattr(self, 'spooky_timer', None):
            self.spooky_timer.cancel()
        self.spooky_timer = Clock.schedule_interval(self.try_spooky_event, 2.0)
        
        self.ghost.reset()
        Animation.cancel_all(self.ghost, 'y')
        self.setup_ghost_position(0)
        self.ghost.is_paused = False
        self.answer_input.disabled = False
        
        self.next_word()
        self.update_ui()
        Clock.schedule_once(self._force_focus, 0.3)
