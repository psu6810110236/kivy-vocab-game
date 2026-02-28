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
from kivy.properties import ListProperty  
from kivy.factory import Factory
from kivy.uix.widget import Widget 
import random
from widgets.ghost import Ghost
# ✅ ใช้ไฟล์ฟอนต์ตัวหนาที่มีอยู่ในโฟลเดอร์
LabelBase.register(DEFAULT_FONT, 'LEELAUIB.TTF') 
from kivy.uix.image import Image
# ==========================================
# 1. สร้าง Class SmoothButton (ปุ่มขอบโค้ง)
# ==========================================
class SmoothButton(Button):
    bg_color = ListProperty([0.5, 0.5, 0.5, 1])  
    radius = ListProperty([25]) 
    shadow_color = ListProperty([0, 0, 0, 0.3])  

# --- 🎨 โหลดสไตล์ UI พิเศษ ---
Builder.load_string('''
<SmoothButton>:
    background_color: 0,0,0,0  
    background_normal: ''

    canvas.before:
        # วาดเงาปุ่ม
        Color:
            rgba: self.shadow_color
        RoundedRectangle:
            size: self.size
            pos: self.pos[0] + 3, self.pos[1] - 5  
            radius: self.radius

        # วาดพื้นหลังปุ่ม
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
''')

from systems.sound_manager import SoundManager
from systems.hp_system import HPSystem
from systems.game_logic import GameLogic 

class MainLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.on_resize)
        # =======================
        # ใส่ Scooby (ตัวละครหลัก)
        # =======================
        self.scooby = Image(
            source="assets/images/scooby.png",
            size_hint=(None, None),
            size=(260, 260),
            pos=(40, 40)
        )
        self.add_widget(self.scooby)
        # --- 🖼️ จัดการภาพพื้นหลัง Scooby-Doo ---
        with self.canvas.before:
            Color(1, 1, 1, 1)  
            self.bg_rect = Rectangle(source='assets/images/bg_scooby_doo.png', size=self.size, pos=self.pos)
            
            Color(0, 0, 0, 0.4) 
            self.overlay_rect = Rectangle(size=self.size, pos=self.pos)
            
        self.bind(size=self._update_bg, pos=self._update_bg)

        self.sound = SoundManager()
        self.hp = HPSystem(max_hp=3)
        self.logic = GameLogic(self.hp)

        self.time_left = 16.0  
        self.time_speed = 1.00  
        Clock.schedule_interval(self.update_timer, 0.10) 

        self.vocab_list = [
            {"thai": "แมว", "english": "cat"}, {"thai": "หมา", "english": "dog"},
            {"thai": "นก", "english": "bird"}, {"thai": "แอปเปิ้ล", "english": "apple"},
            {"thai": "โรงเรียน", "english": "school"}, {"thai": "มด", "english": "ant"},
            {"thai": "หมี", "english": "bear"}, {"thai": "วัว", "english": "cow"},
            {"thai": "เป็ด", "english": "duck"}, {"thai": "ช้าง", "english": "elephant"},
            {"thai": "ปลา", "english": "fish"}, {"thai": "แพะ", "english": "goat"},
            {"thai": "ม้า", "english": "horse"}, {"thai": "กิ้งก่า", "english": "iguana"},
            {"thai": "แมงกะพรุน", "english": "jellyfish"}, {"thai": "จิงโจ้", "english": "kangaroo"},
            {"thai": "สิงโต", "english": "lion"}, {"thai": "ลิง", "english": "monkey"},
            {"thai": "รังนก", "english": "nest"}, {"thai": "นกฮูก", "english": "owl"},
            {"thai": "หมู", "english": "pig"}, {"thai": "นกกระทา", "english": "quail"},
            {"thai": "กระต่าย", "english": "rabbit"}, {"thai": "งู", "english": "snake"},
            {"thai": "เสือ", "english": "tiger"}, {"thai": "ร่ม", "english": "umbrella"},
            {"thai": "รถตู้", "english": "van"}, {"thai": "ปลาวาฬ", "english": "whale"},
            {"thai": "ไซโลโฟน", "english": "xylophone"}, {"thai": "จามรี", "english": "yak"},
            {"thai": "ม้าลาย", "english": "zebra"}, {"thai": "เด็กผู้ชาย", "english": "boy"},
            {"thai": "เด็กผู้หญิง", "english": "girl"}, {"thai": "ผู้ชาย", "english": "man"},
            {"thai": "ผู้หญิง", "english": "woman"}, {"thai": "หนังสือ", "english": "book"},
            {"thai": "ปากกา", "english": "pen"}, {"thai": "ดินสอ", "english": "pencil"},
            {"thai": "ยางลบ", "english": "eraser"}, {"thai": "ไม้บรรทัด", "english": "ruler"},
            {"thai": "โต๊ะเรียน", "english": "desk"}, {"thai": "เก้าอี้", "english": "chair"},
            {"thai": "โต๊ะ", "english": "table"}, {"thai": "ประตู", "english": "door"},
            {"thai": "หน้าต่าง", "english": "window"}, {"thai": "เตียง", "english": "bed"},
            {"thai": "ห้อง", "english": "room"}, {"thai": "บ้าน", "english": "house"},
            {"thai": "หลังคา", "english": "roof"}, {"thai": "กำแพง", "english": "wall"},
            {"thai": "พระอาทิตย์", "english": "sun"}, {"thai": "พระจันทร์", "english": "moon"},
            {"thai": "ดาว", "english": "star"}, {"thai": "ท้องฟ้า", "english": "sky"},
            {"thai": "เมฆ", "english": "cloud"}, {"thai": "ฝน", "english": "rain"},
            {"thai": "หิมะ", "english": "snow"}, {"thai": "ลม", "english": "wind"},
            {"thai": "ไฟ", "english": "fire"}, {"thai": "น้ำ", "english": "water"},
            {"thai": "ต้นไม้", "english": "tree"}, {"thai": "ดอกไม้", "english": "flower"},
            {"thai": "หญ้า", "english": "grass"}, {"thai": "ใบไม้", "english": "leaf"},
            {"thai": "ราก", "english": "root"}, {"thai": "สีแดง", "english": "red"},
            {"thai": "สีเขียว", "english": "green"}, {"thai": "สีน้ำเงิน", "english": "blue"},
            {"thai": "สีเหลือง", "english": "yellow"}, {"thai": "สีดำ", "english": "black"},
            {"thai": "สีขาว", "english": "white"}, {"thai": "สีส้ม", "english": "orange"},
            {"thai": "สีชมพู", "english": "pink"}, {"thai": "สีม่วง", "english": "purple"},
            {"thai": "สีน้ำตาล", "english": "brown"}, {"thai": "สีเทา", "english": "gray"},
            {"thai": "หนึ่ง", "english": "one"}, {"thai": "สอง", "english": "two"},
            {"thai": "สาม", "english": "three"}, {"thai": "สี่", "english": "four"},
            {"thai": "ห้า", "english": "five"}, {"thai": "หก", "english": "six"},
            {"thai": "เจ็ด", "english": "seven"}, {"thai": "แปด", "english": "eight"},
            {"thai": "เก้า", "english": "nine"}, {"thai": "สิบ", "english": "ten"},
            {"thai": "กิน", "english": "eat"}, {"thai": "ดื่ม", "english": "drink"},
            {"thai": "นอน", "english": "sleep"}, {"thai": "วิ่ง", "english": "run"},
            {"thai": "เดิน", "english": "walk"}, {"thai": "กระโดด", "english": "jump"},
            {"thai": "ว่ายน้ำ", "english": "swim"}, {"thai": "บิน", "english": "fly"},
            {"thai": "อ่าน", "english": "read"}, {"thai": "เขียน", "english": "write"},
            {"thai": "พูด", "english": "speak"}, {"thai": "ฟัง", "english": "listen"},
            {"thai": "เล่น", "english": "play"}, {"thai": "ทำงาน", "english": "work"}
        ]
        self.current_word = random.choice(self.vocab_list)

        # ==========================================
        # สร้างกล่องหลัก (vbox) 
        # ==========================================
        vbox = BoxLayout(orientation="vertical", spacing=25, padding=35, size_hint=(1, 1))

        # ส่วนที่ 0: หลอดเวลา 
        time_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.15))
        self.time_label = Label(text=f"Time: {int(self.time_left)}s", font_size='34sp', bold=True, color=(1, 0.6, 0.2, 1))
        self.time_bar = ProgressBar(max=60, value=self.time_left, size_hint=(0.8, 1), pos_hint={'center_x': 0.5})
        time_layout.add_widget(self.time_label)
        time_layout.add_widget(self.time_bar)
        vbox.add_widget(time_layout)

        # ส่วนที่ 1: แถบสถานะ (เอา Emoji ออกเพื่อแก้บั๊กกล่องสี่เหลี่ยม)
        status_card = Factory.CardBox(size_hint=(0.92, 0.15), padding=12, pos_hint={'center_x': 0.5})
        self.hp_label = Label(text=f"Snacks: {self.hp.current_hp}/{self.hp.max_hp}", font_size='26sp', color=(0.9, 0.6, 0.3, 1), bold=True)
        self.score_label = Label(text=f"Score: {self.logic.score}", font_size='26sp', color=(0.3, 0.9, 0.9, 1), bold=True)
        self.combo_label = Label(text=f"Combo: x{self.logic.combo_multiplier}", font_size='26sp', color=(0.7, 1, 0.3, 1), bold=True)
        status_card.add_widget(self.hp_label)
        status_card.add_widget(self.score_label)
        status_card.add_widget(self.combo_label)
        vbox.add_widget(status_card)

        # ส่วนที่ 2: พื้นที่ทายคำศัพท์
        game_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.5), spacing=15)
        
        # 2.1 คำใบ้ภาษาไทย
        self.word_label = Label(text=f"ปริศนา: {self.current_word['thai']}", font_size='50sp', bold=True, color=(1, 1, 1, 1), size_hint=(1, 0.25))
        
        # 2.2 ✅ สร้างตัวแปรเส้นใต้สำหรับคำใบ้จำนวนอักษร
        ans_len = len(self.current_word['english'])
        underscores = ' '.join(['_'] * ans_len)  # สร้างเส้นใต้ เช่น _ _ _
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
        
        submit_btn = Factory.SmoothButton(
            text="SOLVE MYSTERY!", 
            font_size='30sp',         
            bold=True,
            size_hint=(0.52, None),  
            height='90sp',           
            pos_hint={'center_x': 0.5},
            bg_color=(0.55, 0.9, 0.2, 1), 
            color=(0.1, 0.2, 0.05, 1) 
        )
        submit_btn.bind(on_press=self.check_answer)
        
        game_layout.add_widget(self.word_label)
        game_layout.add_widget(self.underscore_label) # ✅ นำเส้นใต้มาแสดงใต้คำศัพท์ไทย
        game_layout.add_widget(self.answer_input)
        game_layout.add_widget(submit_btn)
        
        game_layout.add_widget(Widget(size_hint=(1, 0.05))) 
        vbox.add_widget(game_layout)

        # ส่วนที่ 3: ร้านค้าแลกแต้ม (เอา Emoji ออก)
        shop_layout = BoxLayout(size_hint=(0.98, None), height='80sp', spacing=18, pos_hint={'center_x': 0.5})
        
        buy_life_btn = Factory.SmoothButton(text="+1 Snack (50)", font_size='22sp', bg_color=(0.8, 0.5, 0.3, 1), bold=True) 
        buy_life_btn.bind(on_press=self.buy_life)
        
        hint_btn = Factory.SmoothButton(text="Hint (20)", font_size='22sp', bg_color=(0.2, 0.8, 0.8, 1), bold=True) 
        hint_btn.bind(on_press=self.get_hint)

        slow_time_btn = Factory.SmoothButton(text="Escape! (30)", font_size='22sp', bg_color=(0.6, 0.3, 0.7, 1), bold=True) 
        slow_time_btn.bind(on_press=self.buy_slow_time)
        
        shop_layout.add_widget(buy_life_btn)
        shop_layout.add_widget(hint_btn)
        shop_layout.add_widget(slow_time_btn)
        vbox.add_widget(shop_layout)

        # ส่วนที่ 4: ปุ่มสำหรับ Test 
        test_layout = BoxLayout(size_hint=(0.7, None), height='60sp', spacing=18, pos_hint={'center_x': 0.5})
        test_add_btn = Factory.SmoothButton(text="[Test] +10 Score", font_size='18sp', bg_color=(0.3, 0.6, 0.3, 1)) 
        test_add_btn.bind(on_press=self.test_add_score)
        
        test_reduce_btn = Factory.SmoothButton(text="[Test] -10 Score", font_size='18sp', bg_color=(0.7, 0.3, 0.3, 1)) 
        test_reduce_btn.bind(on_press=self.test_reduce_score)
        
        test_layout.add_widget(test_add_btn)
        test_layout.add_widget(test_reduce_btn)
        vbox.add_widget(test_layout)

        self.add_widget(vbox)
        # --- Enemy System (Ghost) ---
        self.ghost = Ghost(on_hit_callback=self.on_ghost_hit)
        self.add_widget(self.ghost)

        Clock.schedule_once(self.setup_ghost_position, 0)
        self.ghost.end_x = self.scooby.x + 40
        self.ghost.y = self.scooby.y
    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
        self.overlay_rect.pos = instance.pos
        self.overlay_rect.size = instance.size

    def update_timer(self, dt):
    # ถ้าเกมจบแล้วก็หยุดนับ
        if self.hp.is_dead():
            return False  

        # เวลาใช้แค่บอกว่าผีจะถึงในกี่วินาที
        self.time_speed += 0.001 
        self.time_left -= (self.time_speed * 0.1)

        # ไม่ต้องทำอะไรเมื่อเวลา = 0
        # เพราะดาเมจจะเกิดตอนผีชน (on_ghost_hit) เท่านั้น
        if self.time_left <= 0:
            self.time_left = 16.0 
            self.time_speed = 1.0 # แค่ค้างไว้เฉย ๆ

        self.time_label.text = f"Time: {int(self.time_left)}s (Speed: {self.time_speed:.2f}x)"
        self.time_bar.value = self.time_left
    def update_ui(self):
        self.hp_label.text = f"Snacks: {self.hp.current_hp}/{self.hp.max_hp}"
        self.score_label.text = f"Score: {self.logic.score}"
        self.combo_label.text = f"Combo: x{self.logic.combo_multiplier}"
        self.word_label.text = f"ปริศนา: {self.current_word['thai']}"
        
        # ✅ อัปเดตจำนวนเส้นใต้เมื่อเปลี่ยนคำศัพท์ใหม่
        ans_len = len(self.current_word['english'])
        underscores = ' '.join(['_'] * ans_len)
        self.underscore_label.text = underscores

    def next_word(self):
        self.current_word = random.choice(self.vocab_list)
        self.answer_input.text = ""
        self.update_ui()

    def check_answer(self, instance):
        if self.hp.is_dead() or self.time_left <= 0:
            return  

        user_ans = self.answer_input.text.strip().lower() 
        correct_ans = self.current_word["english"].lower()
        
        if is_correct := self.logic.check_answer(user_ans, correct_ans):
            self.sound.play_correct()
            self.time_left = 16.0
            self.time_speed = 1.0
            self.ghost.reset()
            if self.time_left > self.time_bar.max:
                self.time_bar.max = self.time_left
            self.time_bar.value = self.time_left
            self.next_word()
        else:
            self.answer_input.text = "" 
            if self.time_speed > 1.0:
                self.time_speed = 1.0 
            self.update_ui()
            
            if self.hp.is_dead():
                self.sound.play_gameover()
                self.word_label.text = "RUH-ROH! GAME OVER!" 
                self.underscore_label.text = "" # ซ่อนเส้นใต้เมื่อแพ้
                self.word_label.color = (1, 0.3, 0.1, 1)
                self.answer_input.disabled = True 

    def buy_life(self, instance):
        if self.logic.buy_life(cost=50):
            self.update_ui()

    def get_hint(self, instance):
        hint = self.logic.get_hint(self.current_word["english"], cost=20)
        if hint:
            self.answer_input.text = hint
            self.update_ui()

    def buy_slow_time(self, instance):
        cost = 30
        if self.logic.score >= cost:
            if self.time_speed > 0.5: 
                self.logic.score -= cost
                self.time_speed -= 0.1  
                self.update_ui()
            else:
                pass
        else:
            pass

    def test_add_score(self, instance):
        self.logic.score += 10
        self.update_ui()

    def test_reduce_score(self, instance):
        self.logic.score -= 10
        if self.logic.score < 0:
            self.logic.score = 0
        self.update_ui()
    
    def on_ghost_hit(self):
        if self.hp.is_dead() or self.time_left <= 0:
            return

        self.hp.take_damage()
        self.sound.play_wrong()
        self.update_ui()
        self.ghost.is_paused = True
        Clock.schedule_once(self.reset_ghost_after_hit, 1.0)

        if self.hp.is_dead():
            self.sound.play_gameover()
            self.word_label.text = "GAME OVER!"
            self.answer_input.disabled = True
    
    def setup_ghost_position(self, dt):
    # ให้ผีเริ่มนอกขอบขวาของหน้าจอเสมอ
        self.ghost.start_x = self.width + 100
        self.ghost.x = self.ghost.start_x

        # เป้าหมายคือ Scooby
        self.ghost.end_x = self.scooby.x + 40
        self.ghost.y = self.scooby.y
    def on_resize(self, *args):
    # อัปเดตตำแหน่งเกิดผีทุกครั้งที่ขยายจอ
        self.ghost.start_x = self.width + 100
        self.ghost.x = self.ghost.start_x
    def reset_ghost_after_hit(self, dt):
        self.ghost.reset()
        self.ghost.is_paused = False
class VocabGameApp(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    VocabGameApp().run()