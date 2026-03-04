from unittest import loader
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty 
from kivy.factory import Factory
from kivy.uix.widget import Widget 
import random
from kivy.metrics import dp
from kivy.core.audio import SoundLoader
from widgets.ghost import Ghost
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window 
from kivy.uix.behaviors import ButtonBehavior
import json
from kivy.uix.spinner import Spinner

Window.minimum_width = 360
Window.minimum_height = 640

# ใช้ไฟล์ฟอนต์ตัวหนาที่มีอยู่ในโฟลเดอร์
LabelBase.register(DEFAULT_FONT, 'LEELAUIB.TTF') 

class ImageButton(ButtonBehavior, Image):
    pass

# ==========================================
# 1. สร้าง Class SmoothButton (ปุ่มขอบโค้ง)
# ==========================================
class SmoothButton(Button):
    bg_color = ListProperty([0.5, 0.5, 0.5, 1])  
    radius = ListProperty([25]) 
    shadow_color = ListProperty([0, 0, 0, 0.3])  

# --- โหลดสไตล์ UI พิเศษ ---
Builder.load_string('''
<SmoothButton>:
    background_color: 0,0,0,0  
    background_normal: ''

    canvas.before:
        Color:
            rgba: self.shadow_color
        RoundedRectangle:
            size: self.size
            pos: self.pos[0] + 3, self.pos[1] - 5  
            radius: self.radius

        Color:
            rgba: self.bg_color if self.state == 'normal' else [c * 0.9 for c in self.bg_color] 
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: self.radius  

<CardBox@BoxLayout>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0.6 
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [20]

<MainMenuScreen>:
    FloatLayout:
        Image:
            source: 'assets/images/menu_bg.png'
            allow_stretch: True
            keep_ratio: False
            size_hint: 1, 1

        # START
        Button:
            text: ''
            size_hint: 0.19, 0.10
            pos_hint: {'center_x': 0.5, 'center_y': 0.31}
            background_normal: ''
            background_color: 0,0,0,0
            on_release:
                app.sound.play_click()
                app.root.current = 'select_level'

        # OPTIONS
        Button:
            text: ''
            size_hint: 0.18, 0.09
            pos_hint: {'center_x': 0.5, 'center_y': 0.19}
            background_normal: ''
            background_color: 0,0,0,0
            on_release:
                app.sound.play_click()
                app.go_to_options('main_menu')
            
        # EXIT
        Button:
            text: ''
            size_hint: 0.18, 0.09
            pos_hint: {'center_x': 0.5, 'center_y': 0.08}
            background_normal: ''
            background_color: 0,0,0,0
            on_release:
                app.sound.play_click()
                app.stop()

<OptionsScreen>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'assets/images/bg_scooby_doo.png'
        Color:
            rgba: 0, 0, 0, 0.7
        Rectangle:
            pos: self.pos
            size: self.size
            
    BoxLayout:
        orientation: 'vertical'
        padding: [100, 50, 100, 50]
        spacing: 30
        
        Label:
            text: 'การตั้งค่า (Options)'
            font_size: '50sp'
            font_name: 'LEELAUIB.TTF'
            color: 1, 0.8, 0.2, 1
            size_hint_y: 0.3
            bold: True
        
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.3
            size_hint_x: 0.8
            pos_hint: {'center_x': 0.5}
            spacing: 20
            
            SmoothButton:
                text: '-'
                font_size: '50sp'
                size_hint_x: 0.2
                bg_color: 0.8, 0.3, 0.3, 1
                on_release: 
                    app.sound.play_click()
                    app.change_volume(-0.1)
                
            Label:
                text: f'ระดับเสียงดนตรี: {int(app.volume_level * 100)}%'
                font_size: '35sp'
                font_name: 'LEELAUIB.TTF'
                size_hint_x: 0.6
                
            SmoothButton:
                text: '+'
                font_size: '50sp'
                size_hint_x: 0.2
                bg_color: 0.2, 0.7, 0.3, 1
                on_release: 
                    app.sound.play_click()
                    app.change_volume(0.1)
        
        Widget:
            size_hint_y: 0.1
        
        SmoothButton:
            text: 'กลับ (Back)'
            font_size: '30sp'
            font_name: 'LEELAUIB.TTF'
            size_hint_y: None
            height: '80sp'
            size_hint_x: 0.5
            pos_hint: {'center_x': 0.5}
            bg_color: 0.5, 0.5, 0.5, 1
            on_release: 
                app.sound.play_click()
                app.back_from_options()
        
        Widget:
            size_hint_y: 0.3

<SelectLevelScreen>:
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.2, 1
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'assets/images/bg_scooby_doo.png'
        Color:
            rgba: 0, 0, 0, 0.7
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: 50
        spacing: 30
        
        Label:
            text: 'เลือกหมวดหมู่และระดับ'
            font_size: '45sp'
            font_name: 'LEELAUIB.TTF'
            color: 1, 0.8, 0.2, 1
            size_hint_y: 0.3
            bold: True
            
        BoxLayout:
            orientation: 'horizontal'
            spacing: 20
            size_hint_y: 0.2
            Label:
                text: 'หมวดหมู่:'
                font_size: '30sp'
                font_name: 'LEELAUIB.TTF'
            Spinner:
                id: category_spinner
                text: 'สัตว์และธรรมชาติ'
                values: ['สัตว์และธรรมชาติ', 'ชีวิตประจำวัน', 'วิทยาศาสตร์ ไอที และวิศวกรรม']
                font_name: 'LEELAUIB.TTF'
                font_size: '22sp'
                background_color: 0.2, 0.6, 0.8, 1

        BoxLayout:
            orientation: 'horizontal'
            spacing: 20
            size_hint_y: 0.2
            Label:
                text: 'ความยาก:'
                font_size: '30sp'
                font_name: 'LEELAUIB.TTF'
            Spinner:
                id: level_spinner
                text: '1'
                values: ['1', '2', '3', '4', '5']
                font_name: 'LEELAUIB.TTF'
                font_size: '24sp'
                background_color: 0.8, 0.4, 0.2, 1
        
        Widget:
            size_hint_y: 0.1
            
        BoxLayout:
            size_hint_y: 0.2
            spacing: 20
            SmoothButton:
                text: 'กลับ (Back)'
                bg_color: 0.5, 0.5, 0.5, 1
                font_name: 'LEELAUIB.TTF'
                font_size: '25sp'
                on_release: 
                    app.sound.play_click()
                    app.root.current = 'main_menu'
            SmoothButton:
                text: 'เริ่มเกม (Start)'
                bg_color: 0.2, 0.8, 0.2, 1
                font_name: 'LEELAUIB.TTF'
                font_size: '25sp'
                on_release: 
                    app.sound.play_click()
                    app.start_game_with_settings(category_spinner.text, level_spinner.text)
''')

# ==========================================
# 2. จัดการหน้าจอต่างๆ 
# ==========================================

class MainMenuScreen(Screen):
    pass

class OptionsScreen(Screen):
    pass

class SelectLevelScreen(Screen): 
    pass

class GameScreen(Screen):
    def on_enter(self, *args):
        for child in self.children:
            if isinstance(child, MainLayout):
                child.on_screen_enter()
                
from systems.sound_manager import SoundManager
from systems.hp_system import HPSystem
from systems.game_logic import GameLogic 

class MainLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_started = False
        self.timer_event = None
        self.bind(size=self.on_resize)
        
        self.is_paused = False 
        Window.bind(on_keyboard=self._on_keyboard)
        
        self.vocab_pool = []
        self.total_words_in_level = 0
        self.current_word = {"thai": "กำลังโหลด...", "english": "loading"}

        self.scooby = Image(
            source="assets/images/scooby.png",
            size_hint=(None, None),
            size=(260, 260),
            pos=(40, 40)
        )
        self.add_widget(self.scooby)
        
        with self.canvas.before:
            Color(1, 1, 1, 1)  
            self.bg_rect = Rectangle(source='assets/images/bg_scooby_doo.png', size=self.size, pos=self.pos)
            Color(0, 0, 0, 0.4) 
            self.overlay_rect = Rectangle(size=self.size, pos=self.pos)
            
        self.bind(size=self._update_bg, pos=self._update_bg)

        self.sound = App.get_running_app().sound
        self.hp = HPSystem(max_hp=3)
        self.logic = GameLogic(self.hp)

        self.time_left = 16.0  
        self.time_speed = 1.00  

        # ==========================================
        # การสร้างหน้าจอ UI วางไว้ใน __init__ ให้ถูกต้อง
        # ==========================================
        vbox = BoxLayout(orientation="vertical", spacing=25, padding=35, size_hint=(1, 1))

        time_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.15))
        self.time_label = Label(text=f"Time: {int(self.time_left)}s", font_size='34sp', bold=True, color=(1, 0.6, 0.2, 1))
        self.time_bar = ProgressBar(max=60, value=self.time_left, size_hint=(0.8, 1), pos_hint={'center_x': 0.5})
        time_layout.add_widget(self.time_label)
        time_layout.add_widget(self.time_bar)
        vbox.add_widget(time_layout)

        status_card = Factory.CardBox(size_hint=(0.92, 0.15), padding=12, pos_hint={'center_x': 0.5})
        self.hp_label = Label(text=f"Snacks: {self.hp.current_hp}/{self.hp.max_hp}", font_size='26sp', color=(0.9, 0.6, 0.3, 1), bold=True)
        self.score_label = Label(text=f"Score: {self.logic.score}", font_size='26sp', color=(0.3, 0.9, 0.9, 1), bold=True)
        self.combo_label = Label(text=f"Combo: x{self.logic.combo_multiplier}", font_size='26sp', color=(0.7, 1, 0.3, 1), bold=True)
        status_card.add_widget(self.hp_label)
        status_card.add_widget(self.score_label)
        status_card.add_widget(self.combo_label)
        vbox.add_widget(status_card)

        game_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.5), spacing=15)
        self.word_label = Label(text=f"ปริศนา: {self.current_word['thai']}", font_size='50sp', bold=True, color=(1, 1, 1, 1), size_hint=(1, 0.25))
        
        ans_len = len(self.current_word['english'])
        underscores = ' '.join(['_'] * ans_len)  
        self.underscore_label = Label(text=underscores, font_size='60sp', bold=True, color=(1, 0.8, 0.2, 1), size_hint=(1, 0.15))
        
        self.answer_input = TextInput(
            hint_text="พิมพ์คำแปล...", 
            multiline=False, 
            font_size='36sp',        
            halign="center",
            size_hint=(0.7, None),   
            height='90sp',           
            pos_hint={'center_x': 0.5}, 
            background_color=(0.95, 0.95, 0.95, 0.9),
            padding=[10, 20] 
        )
        self.answer_input.bind(on_text_validate=self.check_answer) 
        
        self.submit_btn = Factory.SmoothButton(
            text="SOLVE MYSTERY!", 
            font_size='30sp',        
            bold=True,
            size_hint=(0.52, None),  
            height='90sp',           
            pos_hint={'center_x': 0.5},
            bg_color=(0.55, 0.9, 0.2, 1), 
            color=(0.1, 0.2, 0.05, 1) 
        )
        self.submit_btn.bind(on_press=self.check_answer)
        
        game_layout.add_widget(self.word_label)
        game_layout.add_widget(self.underscore_label) 
        game_layout.add_widget(self.answer_input)
        game_layout.add_widget(self.submit_btn)
        
        game_layout.add_widget(Widget(size_hint=(1, 0.05))) 
        vbox.add_widget(game_layout)

        # ==========================================
        # ร้านค้าสกิล
        # ==========================================
        shop_layout = BoxLayout(size_hint=(0.98, None), height='130sp', spacing=15, pos_hint={'center_x': 0.5})
        
        skill1_box = Factory.CardBox(orientation='vertical', padding=10, spacing=5)
        btn_heal = ImageButton(source='assets/images/add_score.png', size_hint=(1, 0.65), allow_stretch=True)
        btn_heal.bind(on_release=lambda x: [self.sound.play_click(), self.buy_life(x)])
        lbl_heal = Label(text="เพิ่มเลือด\n 50 SCORE", font_size='18sp', bold=True, halign='center', valign='middle', size_hint=(1, 0.35), color=(1, 0.8, 0.2, 1))
        lbl_heal.bind(size=lbl_heal.setter('text_size')) 
        skill1_box.add_widget(btn_heal)
        skill1_box.add_widget(lbl_heal)

        skill2_box = Factory.CardBox(orientation='vertical', padding=10, spacing=5)
        btn_hint = ImageButton(source='assets/images/hint.png', size_hint=(1, 0.65), allow_stretch=True)
        btn_hint.bind(on_release=lambda x: [self.sound.play_click(), self.get_hint(x)])
        lbl_hint = Label(text="คำใบ้\n 20 SCORE", font_size='18sp', bold=True, halign='center', valign='middle', size_hint=(1, 0.35), color=(0.4, 0.9, 1, 1))
        lbl_hint.bind(size=lbl_hint.setter('text_size'))
        skill2_box.add_widget(btn_hint)
        skill2_box.add_widget(lbl_hint)

        skill3_box = Factory.CardBox(orientation='vertical', padding=10, spacing=5)
        btn_slow = ImageButton(source='assets/images/escape.png', size_hint=(1, 0.65), allow_stretch=True)
        btn_slow.bind(on_release=lambda x: [self.sound.play_click(), self.buy_slow_time(x)])
        lbl_slow = Label(text="หนีผี! \n 30 SCORE", font_size='18sp', bold=True, halign='center', valign='middle', size_hint=(1, 0.35), color=(0.8, 0.5, 1, 1))
        lbl_slow.bind(size=lbl_slow.setter('text_size'))
        skill3_box.add_widget(btn_slow)
        skill3_box.add_widget(lbl_slow)

        shop_layout.add_widget(skill1_box)
        shop_layout.add_widget(skill2_box)
        shop_layout.add_widget(skill3_box)
        vbox.add_widget(shop_layout)

        test_layout = BoxLayout(size_hint=(0.9, None), height='60sp', spacing=18, pos_hint={'center_x': 0.5})
        test_add_btn = Factory.SmoothButton(text="[Test] +10 Score", font_size='18sp', bg_color=(0.3, 0.6, 0.3, 1)) 
        test_add_btn.bind(on_press=self.test_add_score)
        test_reduce_btn = Factory.SmoothButton(text="[Test] -10 Score", font_size='18sp', bg_color=(0.7, 0.3, 0.3, 1)) 
        test_reduce_btn.bind(on_press=self.test_reduce_score)

        test_layout.add_widget(test_add_btn)
        test_layout.add_widget(test_reduce_btn)
        vbox.add_widget(test_layout)

        self.add_widget(vbox)

        self.ghost = Ghost(on_hit_callback=self.on_ghost_hit)
        self.ghost.is_paused = True
        self.add_widget(self.ghost)

        Clock.schedule_once(self.setup_ghost_position, 0)
        self.ghost.end_x = self.scooby.x + 40
        self.ghost.y = self.scooby.y

        # ==========================================
        # Pause Overlay 
        # ==========================================
        self.pause_overlay = FloatLayout(size_hint=(1, 1), opacity=0, pos_hint={'y': 10})
        self.pause_overlay.disabled = True
        
        with self.pause_overlay.canvas.before:
            Color(0, 0, 0, 0.75) 
            self.pause_bg = Rectangle(size=self.size, pos=self.pos)
        self.pause_overlay.bind(size=self._update_pause_bg, pos=self._update_pause_bg)

        pause_box = BoxLayout(orientation='vertical', size_hint=(0.4, 0.6), pos_hint={'center_x': 0.5, 'center_y': 0.5}, spacing=20)
        
        pause_label = Label(text="GAME PAUSED", font_size='50sp', bold=True, color=(1, 0.8, 0.2, 1), size_hint_y=0.4)
        
        resume_btn = Factory.SmoothButton(text="เล่นต่อ (Resume)", font_size='26sp', bg_color=(0.2, 0.7, 0.3, 1), size_hint_y=0.2)
        resume_btn.bind(on_release=lambda x: self.toggle_pause())
        
        options_btn = Factory.SmoothButton(text="ตั้งค่า (Options)", font_size='26sp', bg_color=(0.2, 0.5, 0.8, 1), size_hint_y=0.2)
        options_btn.bind(on_release=self.go_to_options_from_pause)
        
        quit_btn = Factory.SmoothButton(text="ออกไปเมนูหลัก (Exit)", font_size='26sp', bg_color=(0.8, 0.2, 0.2, 1), size_hint_y=0.2)
        quit_btn.bind(on_release=self.quit_to_main_menu)

        pause_box.add_widget(pause_label)
        pause_box.add_widget(resume_btn)
        pause_box.add_widget(options_btn)
        pause_box.add_widget(quit_btn)
        
        self.pause_overlay.add_widget(pause_box)
        self.add_widget(self.pause_overlay)

    def load_vocabulary(self, category_name, level):
        """อ่านไฟล์ JSON แปลงหมวดหมู่ และโหลดลง pool"""
        cat_map = {
            'สัตว์และธรรมชาติ': 'nature',
            'ชีวิตประจำวัน': 'daily',
            'วิทยาศาสตร์ ไอที และวิศวกรรม': 'science_it'
        }
        json_key = cat_map.get(category_name, 'daily')
        
        try:
            with open('vocab_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # โหลดคำศัพท์ทั้งหมดของหมวดและระดับนั้นๆ
            self.vocab_pool = list(data[json_key][str(level)])
            self.total_words_in_level = len(self.vocab_pool)
            
            # สลับตำแหน่งคำศัพท์
            random.shuffle(self.vocab_pool)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            self.vocab_pool = [{"thai": "ข้อผิดพลาดไฟล์", "english": "error"}]

    def next_word(self):
        if not self.vocab_pool:
            # ล็อคปุ่มและช่องพิมพ์เพื่อป้องกันบัคปั๊มคะแนน
            self.answer_input.disabled = True
            self.submit_btn.disabled = True 
            self.ghost.is_paused = True
            self.word_label.color = (0.2, 1, 0.2, 1)

            # [FEATURE] เช็คว่าด่านปัจจุบันน้อยกว่า 5 ไหม ถ้าใช่ให้ไปด่านต่อไป
            if hasattr(self, 'current_level') and self.current_level < 5:
                self.word_label.text = f"เคลียร์ด่าน {self.current_level}! เตรียมลุย..."
                self.underscore_label.text = f"คะแนนสะสม: {self.logic.score}"
                
                # หน่วงเวลาให้ผู้เล่นพักหายใจ 2.5 วินาที ก่อนเรียกฟังก์ชันข้ามด่าน
                Clock.schedule_once(self.go_to_next_level, 2.5)
            else:
                self.word_label.text = "ยินดีด้วย! คุณเคลียร์ทุกด่านแล้ว!"
                self.underscore_label.text = f"คะแนนสูงสุด: {self.logic.score}"
                if self.timer_event:
                    self.timer_event.cancel()
                    self.timer_event = None
                Clock.schedule_once(self.return_to_main_menu_auto, 5.0)
            return
            
        self.current_word = self.vocab_pool.pop()
        self.answer_input.text = ""
        self.update_ui()
    
    def go_to_next_level(self, dt):
        # เพิ่มระดับด่านขึ้น 1
        self.current_level += 1
        
        # โหลดคำศัพท์ของด่านใหม่ในหมวดหมู่เดิม
        self.load_vocabulary(self.current_category, str(self.current_level))
        
        # รีเซ็ตเวลา ความเร็ว และสีข้อความ (แต่ไม่รีเซ็ตคะแนนและเลือด)
        self.time_left = 16.0
        self.time_speed = 1.0 + (self.current_level * 0.1) # ด่าน 2 สปีดเริ่มที่ 1.2, ด่าน 5 เริ่มที่ 1.5
        self.time_bar.max = 60
        self.hp.current_hp = self.hp.max_hp
        self.word_label.color = (1, 1, 1, 1) 
        
        # จับผีกลับไปจุดเริ่มต้นและปล่อยเดิน
        self.ghost.reset()
        self.ghost.is_paused = False
        
        # ปลดล็อคปุ่มและช่องพิมพ์ให้เริ่มเล่นต่อ
        self.answer_input.disabled = False
        self.submit_btn.disabled = False
        self.answer_input.focus = True
        
        # ดึงคำศัพท์คำแรกของด่านใหม่มาแสดง
        self.next_word()
        self.update_ui()

    def return_to_main_menu_auto(self, dt):
        # รีเซ็ตค่าตัวแปรทั้งหมดให้พร้อมสำหรับการเริ่มเกมรอบหน้า
        self.reset_entire_game()
        
        # สั่งเปลี่ยนหน้าจอกลับไปที่หน้า main_menu
        if self.parent and hasattr(self.parent, 'manager'):
            self.parent.manager.current = 'main_menu'

    def on_screen_enter(self):
        Clock.schedule_once(lambda dt: self._force_focus(), 0.1)

    def _force_focus(self):
        if self.is_paused or getattr(self.ghost, 'is_paused', False) or self.hp.is_dead():
            return
            
        if not self.vocab_pool: 
            return
        self.answer_input.disabled = False
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
            self.answer_input.text = ""
            self.pause_overlay.opacity = 1
            self.pause_overlay.disabled = False
            self.pause_overlay.pos_hint = {'center_x': 0.5, 'center_y': 0.5} 
            self.answer_input.disabled = True
            self.submit_btn.disabled = True
            self.ghost.is_paused = True 
        else:
            self.pause_overlay.opacity = 0
            self.pause_overlay.disabled = True
            self.pause_overlay.pos_hint = {'y': 10} 
            self.answer_input.disabled = False
            self.submit_btn.disabled = False
            self.answer_input.focus = True
            self.ghost.is_paused = False

    def _update_pause_bg(self, instance, value):
        self.sound.play_click()
        self.pause_bg.pos = instance.pos
        self.pause_bg.size = instance.size

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

        self.game_started = False
        self.hp = HPSystem(max_hp=3)
        self.logic = GameLogic(self.hp)
        self.time_left = 16.0
        self.time_speed = 1.00
        self.time_bar.max = 60
        self.ghost.reset()
        self.ghost.is_paused = False
        self.answer_input.disabled = False
        self.submit_btn.disabled = False
        self.word_label.color = (1, 1, 1, 1)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
        self.overlay_rect.pos = instance.pos
        self.overlay_rect.size = instance.size

    def update_timer(self, dt):
        if self.parent and hasattr(self.parent, 'manager') and self.parent.manager.current != 'game_screen':
            return
        if self.is_paused or self.hp.is_dead() or getattr(self.ghost, 'is_paused', False):
            return 
        if not self.game_started:
            return
        self.time_speed += 0.001 
        if self.time_speed > 3.0: # ลิมิตความเร็วสูงสุดไว้ที่ 3 เท่า
            self.time_speed = 3.0
        self.time_left -= (self.time_speed * 0.1)
        if self.time_left <= 0:
            self.time_left = 0
        self.time_label.text = f"Time: {int(self.time_left)}s (Speed: {self.time_speed:.2f}x)"
        self.time_bar.value = self.time_left

    def update_ui(self):
        self.hp_label.text = f"Snacks: {self.hp.current_hp}/{self.hp.max_hp}"
        self.score_label.text = f"Score: {self.logic.score}"
        self.combo_label.text = f"Combo: x{self.logic.combo_multiplier}"
        lvl = getattr(self, 'current_level', 1)
        self.word_label.text = f"[ด่าน {lvl}] ปริศนา: {self.current_word['thai']}"
        english_word = self.current_word['english']
        underscores_list = []
        for char in english_word:
            if char == ' ':
                underscores_list.append('   ') # ถ้าเป็นช่องว่าง ให้เว้นช่องให้กว้างหน่อย
            else:
                underscores_list.append('_')   # ถ้าเป็นตัวอักษร ให้ใส่ขีดล่าง
                
        self.underscore_label.text = ' '.join(underscores_list)

    def check_answer(self, instance):
        if self.hp.is_dead() or self.time_left <= 0 or self.is_paused:
            return  
        user_ans = self.answer_input.text.strip().lower() 
        if not user_ans: # เพิ่ม 2 บรรทัดนี้: ถ้าว่างเปล่าให้เด้งออกไปเลย ไม่ตรวจ
            return
        correct_ans = self.current_word["english"].lower()
        is_correct = self.logic.check_answer(user_ans, correct_ans)
        if is_correct:
            self.sound.play_correct()
            self.time_left = 16.0
            self.ghost.reset()
            if self.time_left > self.time_bar.max:
                self.time_bar.max = self.time_left
            self.time_bar.value = self.time_left
            self.next_word()
            Clock.schedule_once(lambda dt: self._force_focus(), 0.1)
        else:
            self.answer_input.text = "" 
            if self.time_speed > 1.0:
                self.time_speed = 1.0 
            self.update_ui()
            if self.hp.is_dead():
                self.sound.play_gameover()
                self.word_label.text = "RUH-ROH! GAME OVER!" 
                self.underscore_label.text = "" 
                self.word_label.color = (1, 0.3, 0.1, 1)
                self.answer_input.disabled = True 
                Clock.schedule_once(lambda dt: self._force_focus(), 0.1)
                self.word_label.color = (1, 0.3, 0.3, 1) 
                Clock.schedule_once(lambda dt: setattr(self.word_label, 'color', (1, 1, 1, 1)), 0.5)

    def buy_life(self, instance):
        # เช็คว่าเลือดปัจจุบันน้อยกว่าเลือดสูงสุดหรือเปล่า
        if self.hp.current_hp < self.hp.max_hp:
            if self.logic.buy_life(cost=50):
                self.update_ui()

    def get_hint(self, instance):
        hint = self.logic.get_hint(self.current_word["english"], cost=20)
        if hint:
            self.answer_input.text = hint
            self.update_ui()

    def buy_slow_time(self, instance):
        cost = 30
        
        # เช็คว่าคะแนนพอซื้อหรือไม่
        if self.logic.score >= cost:
            self.logic.score -= cost
            
            # [FIX] 1. ผลักผีกลับไปที่จุดเริ่มต้น (หนีผีได้จริงๆ แล้ว!)
            if hasattr(self, 'ghost'):
                self.ghost.reset()
                self.ghost.is_paused = False
            
            # [FIX] 2. รีเซ็ตความเร็วเวลาให้ช้าลงแบบเห็นผลชัดเจน (เซ็ตกลับไปเป็น 0.75 เลย)
            self.time_speed = 0.75 
            
            # [FIX] 3. แถมโบนัสต่อเวลาให้ผู้เล่นตั้งหลักอีก 5 วินาที
            self.time_left += 5.0
            if self.time_left > 16.0:  # ป้องกันเวลาล้นหลอด
                self.time_left = 16.0
            self.time_bar.value = self.time_left
            
            self.update_ui()

    def test_add_score(self, instance):
        self.logic.score += 10
        self.update_ui()

    def test_reduce_score(self, instance):
        self.logic.score -= 10
        if self.logic.score < 0:
            self.logic.score = 0
        self.update_ui()
    
    def on_ghost_hit(self):
        if self.hp.is_dead() or getattr(self.ghost, 'is_paused', False) or self.is_paused:
            return
        self.time_left = 0
        self.hp.take_damage()
        self.logic.combo_multiplier = 1
        self.sound.play_wrong()
        self.ghost.is_paused = True
        self.answer_input.text = ""
        self.answer_input.disabled = True 
        self.submit_btn.disabled = True
        self.update_ui()
        if self.hp.is_dead():
            self.sound.play_gameover()
            self.word_label.text = "GAME OVER!"
            self.underscore_label.text = ""
            self.answer_input.disabled = True
        else:
            Clock.schedule_once(self.reset_ghost_after_hit, 2.0)
    
    def setup_ghost_position(self, dt):
        self.ghost.start_x = self.width + 100
        self.ghost.x = self.ghost.start_x
        self.ghost.end_x = self.scooby.x + 40
        self.ghost.y = self.scooby.y

    def on_resize(self, *args):
        self.ghost.start_x = self.width + 100
        self.ghost.x = self.ghost.start_x

    def reset_ghost_after_hit(self, dt):
        if self.hp.is_dead() or self.is_paused:
            return
        self.ghost.reset()
        self.ghost.is_paused = False
        self.next_word()
        self.answer_input.disabled = False
        self.submit_btn.disabled = False
        self.answer_input.focus = True
        self.answer_input.focus = True
        self.time_left = 16.0
        self.time_speed = 1.0
        self.time_bar.value = self.time_left

    def start_game(self, category, level):
        # รีเซ็ตค่าและโหลดคำศัพท์ตามโหมดที่เลือก
        self.current_category = category
        self.current_level = int(level)
        self.load_vocabulary(category, level)

        self.game_started = True
        self.time_left = 16.0
        self.time_speed = 1.0
        self.logic.score = 0
        self.logic.combo_multiplier = 1
        self.hp.current_hp = self.hp.max_hp
        
        # เริ่ม Timer
        if self.timer_event:
            self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer, 0.1)
        
        # ปล่อยผี!
        self.ghost.reset()
        self.ghost.is_paused = False
        self.answer_input.disabled = False
        if hasattr(self, 'submit_btn'):
            self.submit_btn.disabled = False
        self.next_word()
        self.update_ui()

class VocabGameApp(App):
    volume_level = NumericProperty(0.3) 
    bg_music = None
    previous_screen = 'main_menu' 
    
    def use_add_score(self):
        pass

    def use_hint(self):
        pass

    def use_escape(self):
        pass

    def build(self):
        self.sound = SoundManager()
        self.bg_music = SoundLoader.load("assets/sound/music/theme.mp3")
        if self.bg_music:
            self.bg_music.loop = True
            self.bg_music.volume = self.volume_level
            self.bg_music.play()

        sm = ScreenManager()
        
        menu_screen = MainMenuScreen(name='main_menu')
        options_screen = OptionsScreen(name='options_screen')
        select_level_screen = SelectLevelScreen(name='select_level') 
        game_screen = GameScreen(name='game_screen')
        
        game_layout = MainLayout()
        game_screen.add_widget(game_layout)
        
        sm.add_widget(menu_screen)
        sm.add_widget(select_level_screen) 
        sm.add_widget(options_screen)
        sm.add_widget(game_screen)
        
        return sm

    def change_volume(self, change):
        new_vol = self.volume_level + change
        self.volume_level = max(0.0, min(1.0, new_vol)) 
        
        if self.bg_music:
            self.bg_music.volume = self.volume_level

    def go_to_options(self, from_screen):
        self.previous_screen = from_screen
        self.root.current = 'options_screen'

    def back_from_options(self):
        self.root.current = self.previous_screen

    def start_game_with_settings(self, category, level):
        self.root.current = 'game_screen'
        game_screen = self.root.get_screen('game_screen')
        for child in game_screen.children:
            if isinstance(child, MainLayout):
                child.reset_entire_game() 
                child.start_game(category, level)

if __name__ == "__main__":
    VocabGameApp().run()