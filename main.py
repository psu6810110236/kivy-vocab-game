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

Window.minimum_width = 360
Window.minimum_height = 640
# ✅ ใช้ไฟล์ฟอนต์ตัวหนาที่มีอยู่ในโฟลเดอร์
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

# --- 🎨 โหลดสไตล์ UI พิเศษ ---
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
            on_release: app.start_game_from_menu()

        # OPTIONS
        Button:
            text: ''
            size_hint: 0.18, 0.09
            pos_hint: {'center_x': 0.5, 'center_y': 0.19}
            background_normal: ''
            background_color: 0,0,0,0
            on_release: app.go_to_options('main_menu')

        # EXIT
        Button:
            text: ''
            size_hint: 0.18, 0.09
            pos_hint: {'center_x': 0.5, 'center_y': 0.08}
            background_normal: ''
            background_color: 0,0,0,0
            on_release: app.stop()

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
                on_release: app.change_volume(-0.1)
                
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
                on_release: app.change_volume(0.1)
        
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
            on_release: app.back_from_options()
        
        Widget:
            size_hint_y: 0.3
''')

# ==========================================
# 2. จัดการหน้าจอต่างๆ (แก้ไขปัญหาพิมพ์ไม่ได้ตรงนี้)
# ==========================================
class MainMenuScreen(Screen):
    pass

class OptionsScreen(Screen):
    pass

class GameScreen(Screen):
    def on_enter(self, *args):
        for child in self.children:
            if isinstance(child, MainLayout):
                child.on_screen_enter()
                child.start_game()   # ✅ เริ่มเกมตอนเข้าหน้านี้
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

        self.sound = SoundManager()
        self.hp = HPSystem(max_hp=3)
        self.logic = GameLogic(self.hp)

        self.time_left = 16.0  
        self.time_speed = 1.00  
       

        # ✅ เพิ่มคำศัพท์จัดเต็มกว่า 100 คำ ครอบคลุมหลายหมวดหมู่
        self.vocab_list = [
            # สัตว์
            {"thai": "แมว", "english": "cat"}, {"thai": "หมา", "english": "dog"},
            {"thai": "นก", "english": "bird"}, {"thai": "มด", "english": "ant"},
            {"thai": "หมู", "english": "pig"}, {"thai": "วัว", "english": "cow"},
            {"thai": "ช้าง", "english": "elephant"}, {"thai": "ลิง", "english": "monkey"},
            {"thai": "เสือ", "english": "tiger"}, {"thai": "สิงโต", "english": "lion"},
            {"thai": "หมี", "english": "bear"}, {"thai": "งู", "english": "snake"},
            {"thai": "กระต่าย", "english": "rabbit"}, {"thai": "ปลา", "english": "fish"},
            {"thai": "เป็ด", "english": "duck"}, {"thai": "ไก่", "english": "chicken"},
            {"thai": "ม้า", "english": "horse"}, {"thai": "แกะ", "english": "sheep"},
            # สิ่งของ / โรงเรียน
            {"thai": "แอปเปิ้ล", "english": "apple"}, {"thai": "โรงเรียน", "english": "school"},
            {"thai": "เก้าอี้", "english": "chair"}, {"thai": "โต๊ะ", "english": "table"},
            {"thai": "หนังสือ", "english": "book"}, {"thai": "ปากกา", "english": "pen"},
            {"thai": "ดินสอ", "english": "pencil"}, {"thai": "ไม้บรรทัด", "english": "ruler"},
            {"thai": "ยางลบ", "english": "eraser"}, {"thai": "กระเป๋า", "english": "bag"},
            {"thai": "โทรศัพท์", "english": "phone"}, {"thai": "นาฬิกา", "english": "clock"},
            {"thai": "ประตู", "english": "door"}, {"thai": "หน้าต่าง", "english": "window"},
            {"thai": "เตียง", "english": "bed"}, {"thai": "ห้อง", "english": "room"},
            {"thai": "บ้าน", "english": "house"},
            # ธรรมชาติ
            {"thai": "พระอาทิตย์", "english": "sun"}, {"thai": "พระจันทร์", "english": "moon"},
            {"thai": "ดาว", "english": "star"}, {"thai": "ท้องฟ้า", "english": "sky"},
            {"thai": "เมฆ", "english": "cloud"}, {"thai": "ฝน", "english": "rain"},
            {"thai": "ลม", "english": "wind"}, {"thai": "ไฟ", "english": "fire"},
            {"thai": "น้ำ", "english": "water"}, {"thai": "ต้นไม้", "english": "tree"},
            {"thai": "ดอกไม้", "english": "flower"}, {"thai": "หญ้า", "english": "grass"},
            {"thai": "ใบไม้", "english": "leaf"}, {"thai": "ภูเขา", "english": "mountain"},
            {"thai": "แม่น้ำ", "english": "river"},
            # ร่างกาย
            {"thai": "หัว", "english": "head"}, {"thai": "ตา", "english": "eye"},
            {"thai": "หู", "english": "ear"}, {"thai": "จมูก", "english": "nose"},
            {"thai": "ปาก", "english": "mouth"}, {"thai": "ฟัน", "english": "tooth"},
            {"thai": "มือ", "english": "hand"}, {"thai": "แขน", "english": "arm"},
            {"thai": "ขา", "english": "leg"}, {"thai": "เท้า", "english": "foot"},
            {"thai": "ผม", "english": "hair"},
            # สี
            {"thai": "สีแดง", "english": "red"}, {"thai": "สีน้ำเงิน", "english": "blue"},
            {"thai": "สีเขียว", "english": "green"}, {"thai": "สีเหลือง", "english": "yellow"},
            {"thai": "สีดำ", "english": "black"}, {"thai": "สีขาว", "english": "white"},
            {"thai": "สีชมพู", "english": "pink"}, {"thai": "สีส้ม", "english": "orange"},
            {"thai": "สีม่วง", "english": "purple"}, {"thai": "สีน้ำตาล", "english": "brown"},
            # อาหาร
            {"thai": "ข้าว", "english": "rice"}, {"thai": "ขนมปัง", "english": "bread"},
            {"thai": "นม", "english": "milk"}, {"thai": "ไข่", "english": "egg"},
            {"thai": "เนื้อสัตว์", "english": "meat"}, {"thai": "เค้ก", "english": "cake"},
            {"thai": "น้ำตาล", "english": "sugar"}, {"thai": "เกลือ", "english": "salt"},
            # คำกริยา (Verbs)
            {"thai": "วิ่ง", "english": "run"}, {"thai": "เดิน", "english": "walk"},
            {"thai": "กระโดด", "english": "jump"}, {"thai": "นอน", "english": "sleep"},
            {"thai": "กิน", "english": "eat"}, {"thai": "ดื่ม", "english": "drink"},
            {"thai": "อ่าน", "english": "read"}, {"thai": "เขียน", "english": "write"},
            {"thai": "ฟัง", "english": "listen"}, {"thai": "พูด", "english": "speak"},
            {"thai": "เล่น", "english": "play"},
            # คำคุณศัพท์ (Adjectives)
            {"thai": "ใหญ่", "english": "big"}, {"thai": "เล็ก", "english": "small"},
            {"thai": "สูง", "english": "tall"}, {"thai": "สั้น", "english": "short"},
            {"thai": "ยาว", "english": "long"}, {"thai": "เร็ว", "english": "fast"},
            {"thai": "ช้า", "english": "slow"}, {"thai": "ดี", "english": "good"},
            {"thai": "แย่", "english": "bad"}, {"thai": "ร้อน", "english": "hot"},
            {"thai": "เย็น", "english": "cold"}
        ]
        self.current_word = random.choice(self.vocab_list)

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
        game_layout.add_widget(self.underscore_label) 
        game_layout.add_widget(self.answer_input)
        game_layout.add_widget(submit_btn)
        
        game_layout.add_widget(Widget(size_hint=(1, 0.05))) 
        vbox.add_widget(game_layout)

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
        self.add_widget(self.ghost)

        Clock.schedule_once(self.setup_ghost_position, 0)
        self.ghost.end_x = self.scooby.x + 40
        self.ghost.y = self.scooby.y

        # ==========================================
        # 3. แก้ไข Pause Overlay (เลื่อนหลบไปนอกจอก่อน)
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

    def on_screen_enter(self):
        Clock.schedule_once(lambda dt: self._force_focus(), 0.1)

    def _force_focus(self):
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
            self.pause_overlay.opacity = 1
            self.pause_overlay.disabled = False
            self.pause_overlay.pos_hint = {'center_x': 0.5, 'center_y': 0.5} 
            self.answer_input.disabled = True
            self.ghost.is_paused = True 
        else:
            self.pause_overlay.opacity = 0
            self.pause_overlay.disabled = True
            self.pause_overlay.pos_hint = {'y': 10} 
            self.answer_input.disabled = False
            self.answer_input.focus = True
            self.ghost.is_paused = False

    def _update_pause_bg(self, instance, value):
        self.pause_bg.pos = instance.pos
        self.pause_bg.size = instance.size

    def go_to_options_from_pause(self, instance):
        App.get_running_app().go_to_options('game_screen')

    def quit_to_main_menu(self, instance):
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
        self.word_label.color = (1, 1, 1, 1)
        self.next_word() 

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
        self.time_left -= (self.time_speed * 0.1)
        if self.time_left <= 0:
            self.time_left = 0
        self.time_label.text = f"Time: {int(self.time_left)}s (Speed: {self.time_speed:.2f}x)"
        self.time_bar.value = self.time_left

    def update_ui(self):
        self.hp_label.text = f"Snacks: {self.hp.current_hp}/{self.hp.max_hp}"
        self.score_label.text = f"Score: {self.logic.score}"
        self.combo_label.text = f"Combo: x{self.logic.combo_multiplier}"
        self.word_label.text = f"ปริศนา: {self.current_word['thai']}"
        ans_len = len(self.current_word['english'])
        underscores = ' '.join(['_'] * ans_len)
        self.underscore_label.text = underscores

    def next_word(self):
        self.current_word = random.choice(self.vocab_list)
        self.answer_input.text = ""
        self.update_ui()

    def check_answer(self, instance):
        if self.hp.is_dead() or self.time_left <= 0 or self.is_paused:
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
                self.underscore_label.text = "" 
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
        self.sound.play_wrong()
        self.ghost.is_paused = True
        self.answer_input.text = ""
        self.answer_input.disabled = True 
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
        self.answer_input.focus = True
        self.time_left = 16.0
        self.time_speed = 1.0
        self.time_bar.value = self.time_left

    def start_game(self):
        if self.game_started:
            return

        self.game_started = True
        self.time_left = 16.0
        self.time_speed = 1.0

        self.timer_event = Clock.schedule_interval(self.update_timer, 0.10)

        self.ghost.reset()
        self.ghost.is_paused = False

class VocabGameApp(App):
    volume_level = NumericProperty(0.3) 
    bg_music = None
    previous_screen = 'main_menu' 

    def build(self):
        self.bg_music = SoundLoader.load("assets/music/theme.mp3") 
        if self.bg_music:
            self.bg_music.loop = True
            self.bg_music.volume = self.volume_level
            self.bg_music.play()
        else:
            print("ไม่สามารถโหลดไฟล์เสียงได้ ตรวจสอบ Path ไฟล์อีกครั้ง")

        sm = ScreenManager()
        
        menu_screen = MainMenuScreen(name='main_menu')
        options_screen = OptionsScreen(name='options_screen')
        game_screen = GameScreen(name='game_screen')
        
        game_layout = MainLayout()
        game_screen.add_widget(game_layout)
        
        sm.add_widget(menu_screen)
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

    def start_game_from_menu(self):
        self.root.current = 'game_screen'

        game_screen = self.root.get_screen('game_screen')
        for child in game_screen.children:
            if isinstance(child, MainLayout):
                child.reset_entire_game()
                child.start_game()

if __name__ == "__main__":
    VocabGameApp().run()