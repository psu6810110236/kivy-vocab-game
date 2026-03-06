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
from kivy.metrics import dp, sp
from kivy.core.audio import SoundLoader
from widgets.ghost import Ghost
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window 
from kivy.uix.behaviors import ButtonBehavior
import json
from kivy.uix.spinner import Spinner
from kivy.animation import Animation
import os

Window.minimum_width = 360
Window.minimum_height = 640

# ใช้ไฟล์ฟอนต์ตัวหนาที่มีอยู่ในโฟลเดอร์
LabelBase.register(DEFAULT_FONT, 'LEELAUIB.TTF') 

class ImageButton(ButtonBehavior, Image):
    pass

# ==========================================
# คลาสสำหรับเอฟเฟกต์อักษรลอย (Floating Text)
# ==========================================
class FloatingText(Label):
    def __init__(self, text, start_pos, color=(1, 1, 0, 1), **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = '30sp'
        self.bold = True
        self.color = color
        self.size_hint = (None, None)
        self.pos = start_pos
        self.outline_width = 2
        self.outline_color = (0, 0, 0, 1)
        
        # อนิเมชันลอยขึ้นและจางหาย
        anim = Animation(y=self.pos[1] + dp(100), opacity=0, duration=1.0, transition='out_quad')
        anim.bind(on_complete=self.remove_me)
        anim.start(self)

    def remove_me(self, *args):
        if self.parent:
            self.parent.remove_widget(self)

# ==========================================
# สร้าง Class SmoothButton (ปุ่มขอบโค้ง)
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
            rgba: 0, 0, 0, 0.65  
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

        Button:
            text: ''
            size_hint: 0.19, 0.10
            pos_hint: {'center_x': 0.5, 'center_y': 0.31}
            background_normal: ''
            background_color: 0,0,0,0
            on_release:
                app.sound.play_click()
                app.root.current = 'select_level'

        Button:
            text: ''
            size_hint: 0.18, 0.09
            pos_hint: {'center_x': 0.5, 'center_y': 0.19}
            background_normal: ''
            background_color: 0,0,0,0
            on_release:
                app.sound.play_click()
                app.go_to_options('main_menu')
            
        Button:
            text: ''
            size_hint: 0.18, 0.09
            pos_hint: {'center_x': 0.5, 'center_y': 0.08}
            background_normal: ''
            background_color: 0,0,0,0
            on_release:
                app.sound.play_click()
                app.stop()

        # --- กล่องแสดงสถิติคะแนนสูงสุด (มุมขวาล่าง) ---
        CardBox:
            size_hint: None, None
            size: dp(220), dp(60)
            pos_hint: {'right': 0.95, 'y': 0.03} 
            padding: dp(10)
            
            Label:
                id: highscore_label
                text: '🏆 Highscore: 0'
                font_size: '22sp'
                font_name: 'LEELAUIB.TTF'
                color: 1, 0.85, 0.1, 1
                bold: True
                outline_width: 2
                outline_color: 0.3, 0.1, 0.4, 1

<OptionsScreen>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'assets/images/bg_scooby_doo.png'
        Color:
            rgba: 0.15, 0.05, 0.25, 0.85
        Rectangle:
            pos: self.pos
            size: self.size
            
    FloatLayout:
        CardBox:
            orientation: 'vertical'
            size_hint: 0.85, 0.55
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            padding: dp(30)
            spacing: dp(20)
            
            Label:
                text: 'Settings'
                font_size: '45sp'
                font_name: 'LEELAUIB.TTF'
                color: 0.6, 0.8, 0.2, 1
                size_hint_y: 0.3
                bold: True
                outline_width: 3
                outline_color: 0.2, 0.05, 0.3, 1
            
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: 0.3
                size_hint_x: 0.9
                pos_hint: {'center_x': 0.5}
                spacing: 20
                
                SmoothButton:
                    text: '-'
                    font_size: '50sp'
                    size_hint_x: 0.25
                    bg_color: 0.9, 0.4, 0.1, 1
                    radius: [20]
                    on_release: 
                        app.sound.play_click()
                        app.change_volume(-0.1)
                    
                Label:
                    text: f'Music: {int(app.volume_level * 100)}%'
                    font_size: '28sp'
                    font_name: 'LEELAUIB.TTF'
                    size_hint_x: 0.5
                    color: 1, 1, 1, 1
                    outline_width: 2
                    outline_color: 0, 0, 0, 1
                    
                SmoothButton:
                    text: '+'
                    font_size: '50sp'
                    size_hint_x: 0.25
                    bg_color: 0.6, 0.8, 0.2, 1
                    radius: [20]
                    on_release: 
                        app.sound.play_click()
                        app.change_volume(0.1)
            
            Widget:
                size_hint_y: 0.1
            
            SmoothButton:
                text: 'Back'
                font_size: '28sp'
                font_name: 'LEELAUIB.TTF'
                size_hint_y: None
                height: '70sp'
                size_hint_x: 0.6
                pos_hint: {'center_x': 0.5}
                bg_color: 0.5, 0.2, 0.6, 1
                radius: [25]
                on_release: 
                    app.sound.play_click()
                    app.back_from_options()
            
            Widget:
                size_hint_y: 0.1

<SelectLevelScreen>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'assets/images/menu_bg.png' 
        Color:
            rgba: 0, 0, 0, 0.5 
        Rectangle:
            pos: self.pos
            size: self.size

    FloatLayout:
        BoxLayout:
            orientation: 'vertical'
            size_hint: 0.85, 0.65
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            padding: dp(20)
            spacing: dp(15)
            
            canvas.before:
                Color:
                    rgba: 0.15, 0.05, 0.25, 0.9 
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [25]
                Color:
                    rgba: 0.6, 0.8, 0.2, 1 
                Line:
                    rounded_rectangle: [self.x, self.y, self.width, self.height, 25]
                    width: 2.5

            Label:
                text: 'Select Category & Level'
                font_size: '35sp'
                font_name: 'LEELAUIB.TTF'
                color: 0.6, 0.8, 0.2, 1
                size_hint_y: 0.2
                bold: True
                outline_width: 3
                outline_color: 0.2, 0.05, 0.3, 1
                
            BoxLayout:
                orientation: 'vertical'
                spacing: dp(5)
                size_hint_y: 0.55
                
                Label:
                    text: 'Category'
                    font_size: '22sp'
                    font_name: 'LEELAUIB.TTF'
                    size_hint_y: 0.4
                    color: 1, 1, 1, 1
                    outline_width: 2
                    outline_color: 0, 0, 0, 1
                    
                Spinner:
                    id: category_spinner
                    text: 'Animals & Nature'
                    values: ['Animals & Nature', 'Daily Life', 'Science, IT & Engineering']
                    font_name: 'LEELAUIB.TTF'
                    font_size: '20sp'
                    size_hint_y: 0.6
                    background_normal: ''
                    background_color: 0.9, 0.5, 0.1, 1 
                    color: 0, 0, 0, 1
                    
                Widget:
                    size_hint_y: 0.1
                    
                Label:
                    text: 'Level'
                    font_size: '22sp'
                    font_name: 'LEELAUIB.TTF'
                    size_hint_y: 0.4
                    color: 1, 1, 1, 1
                    outline_width: 2
                    outline_color: 0, 0, 0, 1
                    
                Spinner:
                    id: level_spinner
                    text: '1'
                    values: ['1', '2', '3', '4', '5']
                    font_name: 'LEELAUIB.TTF'
                    font_size: '20sp'
                    size_hint_y: 0.6
                    background_normal: ''
                    background_color: 0.5, 0.2, 0.6, 1 
                    color: 1, 1, 1, 1
            
            Widget:
                size_hint_y: 0.05
                
            BoxLayout:
                size_hint_y: 0.25
                spacing: dp(15)
                
                SmoothButton:
                    text: 'Back'
                    bg_color: 0.9, 0.4, 0.1, 1
                    font_name: 'LEELAUIB.TTF'
                    font_size: '22sp'
                    radius: [20]
                    on_release: 
                        app.sound.play_click()
                        app.root.current = 'main_menu'
                        
                SmoothButton:
                    text: 'Start Game'
                    bg_color: 0.6, 0.8, 0.2, 1 
                    color: 0.1, 0.2, 0.05, 1
                    font_name: 'LEELAUIB.TTF'
                    font_size: '22sp'
                    bold: True
                    radius: [20]
                    on_release: 
                        app.sound.play_click()
                        app.start_game_with_settings(category_spinner.text, level_spinner.text)

# ==========================================
# เค้าโครง MainLayout โฉมใหม่ (ลดความอึดอัด + อธิบายสกิล)
# ==========================================
<MainLayout>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            source: 'assets/images/bg_scooby_doo.png'
            size: self.size
            pos: self.pos
        Color:
            rgba: 0, 0, 0, 0.25 
        Rectangle:
            size: self.size
            pos: self.pos

    canvas.after:
        Color:
            rgba: root.flash_color
        Rectangle:
            size: self.size
            pos: self.pos

    # ---------------------------
    # ตัวละครหลัก (Scooby) ฝั่งซ้าย
    # ---------------------------
    Image:
        id: scooby
        source: "assets/images/scooby.png"
        size_hint: None, None
        size: dp(310), dp(310) # ปรับขนาดให้พอดี ไม่บัง UI ล่าง
        pos_hint: {'x': 0.05, 'y': 0.30} 

    # ---------------------------
    # UI สเตตัสด้านบน
    # ---------------------------
    FloatLayout:
        size_hint: 1, 0.15
        pos_hint: {'top': 0.98}

        # เปลี่ยนจาก CardBox เป็น BoxLayout เพื่อเอาพื้นหลังออก
        BoxLayout: 
            size_hint: 0.35, 0.5 
            pos_hint: {'x': 0.13, 'top': 0.7}
            padding: dp(5)
            Label:
                id: score_label
                text: "Score: 0"
                font_size: '22sp' 
                bold: True
                color: 0.3, 0.9, 0.9, 1
                outline_width: 2
                outline_color: 0, 0, 0, 1

        # เปลี่ยนจาก CardBox เป็น BoxLayout เช่นกัน
        BoxLayout: 
            size_hint: 0.35, 0.5 
            pos_hint: {'center_x': 0.7, 'top': 0.7}
            padding: dp(5)
            Label:
                id: hp_label
                text: "Snacks: 3/3"
                font_size: '22sp' 
                bold: True
                color: 0.9, 0.6, 0.3, 1
                outline_width: 2
                outline_color: 0, 0, 0, 1
                    
        SmoothButton:
            text: "II"
            font_size: '26sp'
            font_name: 'LEELAUIB.TTF'
            bold: True
            size_hint: None, None
            size: dp(50), dp(50) 
            pos_hint: {'right': 0.95, 'top': 0.9}
            bg_color: 0.8, 0.2, 0.2, 1
            radius: [10]
            on_release: root.toggle_pause()

        ProgressBar:
            id: time_bar
            max: 16
            value: 16
            size_hint: 0.6, None
            height: dp(15) 
            pos_hint: {'center_x': 0.5, 'top': 0.2}
            
        # ================================
        # แถบแสดง Time และ Combo ตรงกลาง
        # ================================
        BoxLayout:
            orientation: 'horizontal'
            size_hint: 0.6, None
            height: dp(40)
            pos_hint: {'center_x': 0.5, 'top': 0.15}
            
            Label:
                id: time_label
                text: "Time: 16s"
                font_size: '24sp' 
                bold: True
                color: 0.2, 1, 0.2, 1
                outline_width: 2
                outline_color: 0, 0, 0, 1
                halign: 'left'
                valign: 'middle'
                text_size: self.size
                    
            Label:
                id: combo_label
                text: "Combo: x1"
                font_size: '24sp' 
                bold: True
                color: 0.7, 1, 0.3, 1
                outline_width: 2
                outline_color: 0, 0, 0, 1
                halign: 'right'
                valign: 'middle'
                text_size: self.size

    # ---------------------------
    # UI ตรงกลาง (คำศัพท์) 
    # ---------------------------
    BoxLayout:
        orientation: 'vertical'
        size_hint: 1, None
        height: dp(150) 
        pos_hint: {'center_x': 0.5, 'y': 0.55} # ปรับให้มีพื้นที่หายใจตรงกลางมากขึ้น
        spacing: dp(0)
        Label:
            id: word_label
            text: "Loading..."
            font_size: '20sp' 
            font_name: 'LEELAUIB.TTF'
            bold: True
            outline_width: 3
            outline_color: 0, 0, 0, 1
        Label:
            id: underscore_label
            text: "_ _ _ _"
            font_size: '35sp' 
            color: 1, 0.8, 0.2, 1
            bold: True
            outline_width: 2
            outline_color: 0, 0, 0, 1
        

    # ---------------------------
    # UI ด้านล่าง (จัดใหม่ให้มีพื้นที่ และอธิบายสกิลด้านข้าง)
    # ---------------------------
    BoxLayout:
        orientation: 'vertical'
        size_hint: 0.95, None  
        height: dp(230)        
        pos_hint: {'center_x': 0.5, 'y': 0.01} 
        spacing: dp(15)

        # แถว 1: ช่องใส่คำตอบ + ปุ่มส่งคำตอบ
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(70)
            spacing: dp(15)

            TextInput:
                id: answer_input
                hint_text: "Type translation..."
                multiline: False
                font_size: '30sp' 
                font_name: 'LEELAUIB.TTF'
                halign: "center"
                background_color: 0, 0, 0, 0  # พื้นหลังโปร่งใส
                foreground_color: 1, 1, 1, 1   # สีตัวอักษรตอนพิมพ์ (สีขาว)
                hint_text_color: 1, 1, 1, 0.5 # สีตัวอักษรคำใบ้ (ขาวจางๆ)
                cursor_color: 0.2, 0.6, 1, 1
                padding: [10, 15]
                on_text_validate: root.check_answer(self)
                # --- ลบ canvas.before เดิมที่วาด RoundedRectangle และ Line ออก ---

            SmoothButton:
                text: "Submit"
                font_name: 'LEELAUIB.TTF'
                font_size: '25sp' 
                bold: True
                size_hint_x: 0.35
                # --- ตั้งค่าสีพื้นหลังและเงาให้เป็น 0 (โปร่งใส) ---
                bg_color: 0, 0, 0, 0 
                shadow_color: 0, 0, 0, 0
                # --- ปรับสีข้อความให้เด่น (ตัวอย่างสีเขียวอ่อน) ---
                color: 1, 1, 1, 1
                on_release: root.check_answer(self)

        # แถว 2: สกิล (จัดเป็น 2 คอลัมน์ จะได้เขียนอธิบายข้างๆ ได้)
        GridLayout:
            cols: 2
            spacing: dp(10)
            size_hint_y: None
            height: dp(140)
            
            # สกิล 1: เพิ่มเลือด
            CardBox:
                orientation: 'horizontal'
                padding: dp(10)
                spacing: dp(10)
                ImageButton:
                    source: 'assets/images/add_score.png'
                    size_hint_x: 0.4
                    allow_stretch: True
                    on_release: app.sound.play_click(); root.buy_life(self)
                BoxLayout:
                    orientation: 'vertical'
                    Label:
                        text: "Heal"
                        font_size: '20sp'
                        font_name: 'LEELAUIB.TTF'
                        color: 0.2, 1, 0.2, 1
                        bold: True
                        text_size: self.size
                        halign: 'left'
                        valign: 'bottom'
                    Label:
                        text: "50 Pt"
                        font_size: '16sp'
                        font_name: 'LEELAUIB.TTF'
                        color: 1, 0.8, 0.2, 1
                        text_size: self.size
                        halign: 'left'
                        valign: 'top'

            # สกิล 2: คำใบ้
            CardBox:
                orientation: 'horizontal'
                padding: dp(10)
                spacing: dp(10)
                ImageButton:
                    source: 'assets/images/hint.png'
                    size_hint_x: 0.4
                    allow_stretch: True
                    on_release: app.sound.play_click(); root.get_hint(self)
                BoxLayout:
                    orientation: 'vertical'
                    Label:
                        text: "Hint"
                        font_size: '20sp'
                        font_name: 'LEELAUIB.TTF'
                        color: 0.4, 0.9, 1, 1
                        bold: True
                        text_size: self.size
                        halign: 'left'
                        valign: 'bottom'
                    Label:
                        text: "20 Pt"
                        font_size: '16sp'
                        font_name: 'LEELAUIB.TTF'
                        color: 1, 0.8, 0.2, 1
                        text_size: self.size
                        halign: 'left'
                        valign: 'top'

            # สกิล 3: หนีผี
            CardBox:
                orientation: 'horizontal'
                padding: dp(10)
                spacing: dp(10)
                ImageButton:
                    source: 'assets/images/escape.png'
                    size_hint_x: 0.4
                    allow_stretch: True
                    on_release: app.sound.play_click(); root.buy_slow_time(self)
                BoxLayout:
                    orientation: 'vertical'
                    Label:
                        text: "Reset Ghost"
                        font_size: '20sp'
                        font_name: 'LEELAUIB.TTF'
                        color: 0.8, 0.5, 1, 1
                        bold: True
                        text_size: self.size
                        halign: 'left'
                        valign: 'bottom'
                    Label:
                        text: "30 Pt"
                        font_size: '16sp'
                        font_name: 'LEELAUIB.TTF'
                        color: 1, 0.8, 0.2, 1
                        text_size: self.size
                        halign: 'left'
                        valign: 'top'
                        
            # ช่องว่างเพื่อให้ Grid สมดุล (สามารถใส่ข้อความให้กำลังใจได้)
            CardBox:
                orientation: 'vertical'
                padding: dp(5)
                Label:
                    text: "Type fast, ghost is coming!"
                    font_size: '15sp'
                    font_name: 'LEELAUIB.TTF'
                    color: 1, 1, 1, 0.5
                    bold: True

    # ---------------------------
    # หน้าจอ Pause
    # ---------------------------
    FloatLayout:
        id: pause_overlay
        opacity: 0
        disabled: True
        pos_hint: {'y': 10}
        canvas.before:
            Color:
                rgba: 0.1, 0.05, 0.15, 0.85
            Rectangle:
                size: self.size
                pos: self.pos
                
        CardBox:
            orientation: 'vertical'
            size_hint: 0.85, 0.6
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            padding: dp(25)
            spacing: dp(20)
            
            Label:
                text: "GAME PAUSED"
                font_size: '45sp'
                font_name: 'LEELAUIB.TTF'
                bold: True
                color: 1, 0.85, 0.1, 1
                outline_width: 3
                outline_color: 0.3, 0.1, 0.4, 1
                size_hint_y: 0.35
                
            BoxLayout:
                orientation: 'vertical'
                spacing: dp(15)
                size_hint_y: 0.65
                size_hint_x: 0.9
                pos_hint: {'center_x': 0.5}
                
                SmoothButton:
                    text: "Resume"
                    font_name: 'LEELAUIB.TTF'
                    font_size: '24sp'
                    bg_color: 0.55, 0.9, 0.2, 1
                    color: 0.1, 0.2, 0.05, 1
                    radius: [25]
                    on_release: root.toggle_pause()
                    
                SmoothButton:
                    text: "Options"
                    font_name: 'LEELAUIB.TTF'
                    font_size: '24sp'
                    bg_color: 0.9, 0.5, 0.1, 1
                    color: 1, 1, 1, 1
                    radius: [25]
                    on_release: root.go_to_options_from_pause(self)
                    
                SmoothButton:
                    text: "Main Menu"
                    font_name: 'LEELAUIB.TTF'
                    font_size: '24sp'
                    bg_color: 0.8, 0.2, 0.3, 1
                    color: 1, 1, 1, 1
                    radius: [25]
                    on_release: root.quit_to_main_menu(self)
''')
# ==========================================
# 2. จัดการหน้าจอต่างๆ 
# ==========================================

class MainMenuScreen(Screen):
    def on_enter(self, *args):
        app = App.get_running_app()
        app.sound.play_menu_bgm()
        self.update_highscore()

    def update_highscore(self):
        highscore = 0
        try:
            if os.path.exists('highscore.json'):
                with open('highscore.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    highscore = data.get('highscore', 0)
        except Exception as e:
            print(f"Error loading highscore: {e}")
        
        self.ids.highscore_label.text = f'🏆 สูงสุด: {highscore}'

class OptionsScreen(Screen):
    pass

class SelectLevelScreen(Screen): 
    pass

class GameScreen(Screen):
    def on_enter(self, *args):
        app = App.get_running_app()
        app.sound.play_game_bgm()

        for child in self.children:
            if isinstance(child, MainLayout):
                child.on_screen_enter()
                
from systems.sound_manager import SoundManager
from systems.hp_system import HPSystem
from systems.game_logic import GameLogic 

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

        self.time_label = self.ids.time_label
        self.time_bar = self.ids.time_bar
        self.hp_label = self.ids.hp_label
        self.score_label = self.ids.score_label
        self.combo_label = self.ids.combo_label
        self.word_label = self.ids.word_label
        self.underscore_label = self.ids.underscore_label
        self.answer_input = self.ids.answer_input
        self.scooby = self.ids.scooby
        self.pause_overlay = self.ids.pause_overlay

        # ผูกฟังก์ชันเพื่อดักข้อความเวลาพิมพ์
        self.answer_input.bind(text=self.on_text_change)

        self.ghost = Ghost(on_hit_callback=self.on_ghost_hit)
        self.ghost.is_paused = True
        self.add_widget(self.ghost)
        self.remove_widget(self.pause_overlay)
        self.add_widget(self.pause_overlay)
        Clock.schedule_once(self.setup_ghost_position, 0)
        self.bind(size=self.on_resize)
        Clock.schedule_interval(self.idle_animations, 1.0)

    def on_text_change(self, instance, value):
        if not getattr(self, 'current_word', None):
            return
        english_word = self.current_word.get('english', '')
        if english_word == 'loading' or not english_word:
            return
            
        display_chars = []
        typed_idx = 0
        
        for char in english_word:
            if char == ' ':
                display_chars.append('   ')
            else:
                if typed_idx < len(value):
                    display_chars.append(value[typed_idx].upper())
                    typed_idx += 1
                else:
                    display_chars.append('_')
                    
        self.underscore_label.text = ' '.join(display_chars)
        
        if len(value) > 0:
            self.underscore_label.color = (0.4, 0.9, 1, 1) 
        else:
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
                self.flash_color = [1, 1, 1, 0.9] 
                anim = Animation(flash_color=[0, 0, 0, 0.95], duration=0.1) + Animation(flash_color=[0, 0, 0, 0], duration=0.6)
                anim.start(self)
                
                og_pos = self.pos
                shake = Animation(pos=(og_pos[0]-25, og_pos[1]+25), duration=0.05) + \
                        Animation(pos=(og_pos[0]+25, og_pos[1]-25), duration=0.05) + \
                        Animation(pos=(og_pos[0]-15, og_pos[1]-15), duration=0.05) + \
                        Animation(pos=og_pos, duration=0.05)
                shake.start(self)
                
            elif event == 'poltergeist':
                self.word_label.color = (1, 0.2, 0.2, 1) 
                
                og_word_x = self.word_label.x
                word_shake = Animation(x=og_word_x - dp(20), duration=0.05) + Animation(x=og_word_x + dp(20), duration=0.05)
                word_shake.repeat = True
                word_shake.start(self.word_label)
                
                og_input_x = self.answer_input.x
                input_shake = Animation(x=og_input_x + dp(15), duration=0.05) + Animation(x=og_input_x - dp(15), duration=0.05)
                input_shake.repeat = True
                input_shake.start(self.answer_input)
                
                def stop_poltergeist(*args):
                    Animation.cancel_all(self.word_label, 'x')
                    Animation.cancel_all(self.answer_input, 'x')
                    self.word_label.x = og_word_x
                    self.answer_input.x = og_input_x
                    self.word_label.color = (1, 1, 1, 1) 
                    
                Clock.schedule_once(stop_poltergeist, 1.5)
                
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
                
                anim = Animation(font_size=sp(160), opacity=0, duration=0.8, transition='out_expo')
                anim.bind(on_complete=lambda *args: self.remove_widget(scary_label))
                anim.start(scary_label)

    def idle_animations(self, dt):
        if not self.is_paused and not getattr(self.ghost, 'is_paused', True):
            anim = Animation(y=self.scooby.y + 10, duration=0.5) + Animation(y=self.scooby.y, duration=0.5)
            anim.start(self.scooby)
            g_anim = Animation(y=self.ghost.y + 20, duration=0.5) + Animation(y=self.ghost.y, duration=0.5)
            g_anim.start(self.ghost)

    def trigger_screen_shake(self):
        og_pos = self.pos
        anim = Animation(pos=(og_pos[0]-15, og_pos[1]+15), duration=0.05) + \
               Animation(pos=(og_pos[0]+15, og_pos[1]-15), duration=0.05) + \
               Animation(pos=og_pos, duration=0.05)
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
        self.word_label.x = -self.width
        Animation(x=0, duration=0.3, transition='out_bounce').start(self.word_label)

    def load_vocabulary(self, category_name, level):
        cat_map = {
            'สัตว์และธรรมชาติ': 'nature',
            'ชีวิตประจำวัน': 'daily',
            'วิทยาศาสตร์ ไอที และวิศวกรรม': 'science_it'
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
        self.answer_input.text = ""
        self.update_ui()
        self.animate_word_in() 
    
    def go_to_next_level(self, dt):
        self.current_level += 1
        self.word_label.font_size = '45sp' 
        self.load_vocabulary(self.current_category, str(self.current_level))
        self.time_left = 16.0
        self.time_speed = 1.0 + (self.current_level * 0.1) 
        self.time_bar.max = 60
        self.hp.current_hp = self.hp.max_hp
        self.word_label.color = (1, 1, 1, 1) 
        self.ghost.reset()
        self.ghost.is_paused = False
        self.answer_input.disabled = False
        self.answer_input.focus = True
        self.next_word()
        self.update_ui()

    def return_to_main_menu_auto(self, dt):
        self.reset_entire_game()
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
            
        if getattr(self, 'spooky_timer', None):
            self.spooky_timer.cancel()
            self.spooky_timer = None

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

    def update_timer(self, dt):
        if self.parent and hasattr(self.parent, 'manager') and self.parent.manager.current != 'game_screen':
            return
        if self.is_paused or self.hp.is_dead() or getattr(self.ghost, 'is_paused', False):
            return 
        if not self.game_started:
            return
        self.time_speed += 0.001 
        if self.time_speed > 3.0: 
            self.time_speed = 3.0
        self.time_left -= (self.time_speed * 0.1)
        if self.time_left <= 0:
            self.time_left = 0
            
        if self.time_left > 10:
            t_color = (0.2, 1, 0.2, 1) 
        elif self.time_left > 4:
            t_color = (1, 0.6, 0.2, 1) 
        else:
            t_color = (1, 0.2, 0.2, 1) 
            
        self.time_label.color = t_color
        self.time_label.text = f"Time: {int(self.time_left)}s"
        
        Animation(value=self.time_left, duration=0.1).start(self.time_bar)

    def update_ui(self):
        self.hp_label.text = f"Snacks: {self.hp.current_hp}/{self.hp.max_hp}"
        self.score_label.text = f"Score: {self.logic.score}"
        self.combo_label.text = f"Combo: x{self.logic.combo_multiplier}"
        lvl = getattr(self, 'current_level', 1)
        self.word_label.text = f"[ด่าน {lvl}] {self.current_word['thai']}"
        
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
            self.answer_input.text = "" 
            
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
                self.ghost.reset()
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
        self.sound.play_wrong() 
        anim = Animation(color=(1, 0, 0, 1), duration=0.1) + Animation(color=(0.3, 0.9, 0.9, 1), duration=0.1)
        anim.start(self.score_label)
    
    def on_ghost_hit(self):
        if self.hp.is_dead() or getattr(self.ghost, 'is_paused', False) or self.is_paused:
            return
        self.time_left = 0
        self.hp.take_damage()
        
        self.trigger_screen_shake()
        self.flash_screen((1, 0, 0, 0.5))
        self.add_widget(FloatingText("-1 HP!", (self.hp_label.x, self.hp_label.y), color=(1,0,0,1)))
        
        self.logic.combo_multiplier = 1
        self.sound.play_wrong()
        self.ghost.is_paused = True
        self.answer_input.text = ""
        self.answer_input.disabled = True 
        self.update_ui()
        
        if self.hp.is_dead():
            self.trigger_game_over()
        else:
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
        
        # 1. ปรับขนาดผี (กว้าง, สูง) ตรงนี้ปรับตัวเลขให้เข้ากับสัดส่วนภาพผีได้เลยครับ
        self.ghost.size = (dp(450), dp(450)) 
        
        self.ghost.start_x = self.width + 50
        if not self.game_started:
            self.ghost.x = self.ghost.start_x
            
        self.ghost.end_x = self.scooby.right + dp(10)
        
        # 2. ปรับระดับความสูง (Y) ของผี
        # ถ้าภาพผีดู "จมดิน" ให้บวกเพิ่ม เช่น self.scooby.y + dp(20)
        # ถ้าภาพผีดู "ลอยไป" ให้ลบออก เช่น self.scooby.y - dp(20)
        self.ghost.y = self.scooby.y + dp(180)

    def on_resize(self, *args):
        self.setup_ghost_position(0)

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
        self.timer_event = Clock.schedule_interval(self.update_timer, 0.1)
        
        if getattr(self, 'spooky_timer', None):
            self.spooky_timer.cancel()
        self.spooky_timer = Clock.schedule_interval(self.try_spooky_event, 2.0)
        
        self.ghost.reset()
        self.ghost.is_paused = False
        self.answer_input.disabled = False
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
        self.sound.play_menu_bgm()

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

        if self.sound.menu_bgm:
            self.sound.menu_bgm.volume = self.volume_level
        if self.sound.game_bgm:
            self.sound.game_bgm.volume = self.volume_level

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