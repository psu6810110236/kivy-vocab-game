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
from kivy.properties import ListProperty, NumericProperty, StringProperty


Window.size = (1920, 1080)
Window.minimum_width = 1920
Window.minimum_height = 1080

LabelBase.register(name='EngFont', fn_regular='assets/fonts/english_font.ttf')
LabelBase.register(name='ThaiFont', fn_regular='assets/fonts/thai_font.ttf')

# ตั้งให้ฟอนต์ไทยเป็นฟอนต์หลักของแอปเผื่อลืมใส่ font_name
LabelBase.register(DEFAULT_FONT, 'assets/fonts/english_font.ttf')

class ImageButton(ButtonBehavior, Image):
    pass

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
        anim = Animation(y=self.pos[1] + dp(100), opacity=0, duration=1.0, transition='out_quad')
        anim.bind(on_complete=self.remove_me)
        anim.start(self)

    def remove_me(self, *args):
        if self.parent:
            self.parent.remove_widget(self)

class SmoothButton(Button):
    bg_color = ListProperty([0.5, 0.5, 0.5, 1])  
    radius = ListProperty([25]) 
    shadow_color = ListProperty([0, 0, 0, 0.3])  

class AnimatedScooby(Image):
    state = StringProperty('idle')
    frame = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_frames = {'idle': 2, 'happy': 2, 'scared': 2} 
        Clock.schedule_interval(self.update_frame, 0.2)

    def update_frame(self, dt):
        if self.state == 'idle':
            speed = 0.9
        elif self.state == 'happy':
            speed = 0.2
        else:
            speed = 0.15
            
        Clock.unschedule(self.update_frame)
        Clock.schedule_once(self.update_frame, speed)

        self.frame += 1
        if self.frame > self.max_frames.get(self.state, 1):
            self.frame = 1
        
        file_path = f'assets/images/scooby_{self.state}_{self.frame}.png'
        if os.path.exists(file_path):
            self.source = file_path

    def change_state(self, new_state, duration=1.0):
        self.state = new_state
        self.frame = 1
        Clock.unschedule(self.reset_to_idle)
        if duration > 0:
            Clock.schedule_once(self.reset_to_idle, duration)

    def reset_to_idle(self, dt=None):
        self.state = 'idle'
        self.frame = 1

# --- ส่วนของ UI หน้าจอทั้งหมด (ย่อมาจากไฟล์เดิมของคุณ) ---
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
                app.root.current = 'start_menu'

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

<GameStartMenuScreen>:
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'assets/images/start_menu_bg.png' 
    FloatLayout:
        Label:
            id: underscore_label
            text: "_ _ _ _ _" 
            font_size: '35sp'
            font_name: 'LEELAUIB.TTF' 
            color: (0,0,0,1)
            outline_width: 2
            outline_color: (0, 0, 0, 1)
            bold: True
            size_hint: (None, None)
            pos_hint: {'center_x': 0.506, 'top': 0.665} 
        BoxLayout:
            orientation: 'vertical'
            size_hint: (0.6, 0.28) 
            pos_hint: {'center_x': 0.512, 'center_y': 0.515} 
            spacing: dp(10)
            Label:
                text: ""
                font_size: '26sp'
                color: (0.2, 0.1, 0, 1) 
                bold: True
            Button:
                text: "Animals & Nature"
                font_size: '23sp'
                background_color: (0, 0, 0, 0) 
                color: (0.3, 0.15, 0, 1)
                on_release: root.select_category("Animals & Nature")
            Button:
                text: "Daily Life"
                font_size: '23sp'
                background_color: (0, 0, 0, 0)
                color: (0.3, 0.15, 0, 1)
                on_release: root.select_category("Daily Life")
            Button:
                text: "Science & IT"
                font_size: '23sp'
                background_color: (0, 0, 0, 0)
                color: (0.3, 0.15, 0, 1)
                on_release: root.select_category("Science, IT & Engineering")
        BoxLayout:
            orientation: 'horizontal'
            size_hint: (0.32, 0.15)
            pos_hint: {'center_x': 0.516, 'center_y': 0.28} 
            Button:
                background_color: (0, 0, 0, 0) 
                on_release: root.select_difficulty(1)
                Label:
                    id: diff_1_label
                    text: "1"
                    font_size: '45sp'
                    font_name: 'LEELAUIB.TTF'
                    color: (1, 1, 1, 1)
                    center: self.parent.center 
            Button:
                background_color: (0, 0, 0, 0)
                on_release: root.select_difficulty(2)
                Label:
                    id: diff_2_label
                    text: "2"
                    font_size: '45sp'
                    font_name: 'LEELAUIB.TTF'
                    color: (1, 1, 1, 1)
                    center: self.parent.center
            Button:
                background_color: (0, 0, 0, 0)
                on_release: root.select_difficulty(3)
                Label:
                    id: diff_3_label
                    text: "3"
                    font_size: '45sp'
                    font_name: 'LEELAUIB.TTF'
                    color: (1, 1, 1, 1)
                    center: self.parent.center
            Button:
                background_color: (0, 0, 0, 0)
                on_release: root.select_difficulty(4)
                Label:
                    id: diff_4_label
                    text: "4"
                    font_size: '45sp'
                    font_name: 'LEELAUIB.TTF'
                    color: (1, 1, 1, 1)
                    center: self.parent.center
            Button:
                background_color: (0, 0, 0, 0)
                on_release: root.select_difficulty(5)
                Label:
                    id: diff_5_label
                    text: "5"
                    font_size: '45sp'
                    font_name: 'LEELAUIB.TTF'
                    color: (1, 1, 1, 1)
                    center: self.parent.center
        Button:
            text: "" 
            background_normal: '' 
            background_color: (0, 0, 0, 0) 
            size_hint: (0.16, 0.08) 
            pos_hint: {'center_x': 0.395, 'center_y': 0.11} 
            on_release: 
                app.sound.play_click()
                app.root.current = 'main_menu'
        Button:
            text: "" 
            background_normal: ''
            background_color: (0, 0, 0, 0) 
            size_hint: (0.2, 0.1) 
            pos_hint: {'center_x': 0.62, 'center_y': 0.11} 
            on_release: root.start_game()

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
    Label:
        id: level_label
        text: "ด่าน: 1"
        font_size: '28sp'
        font_name: 'LEELAUIB.TTF'
        bold: True
        color: 1, 0.85, 0.1, 1
        outline_width: 2
        outline_color: 0, 0, 0, 1
        size_hint: None, None
        size: self.texture_size
        pos_hint: {'center_x': 0.511, 'top': 0.98}
    AnimatedScooby:
        id: scooby
        source: "assets/images/scooby_idle_1.png"
        size_hint: None, None
        size: dp(310), dp(310)
        pos_hint: {'x': 0.05, 'y': 0.30}
    FloatLayout:
        size_hint: 1, 0.15
        pos_hint: {'top': 0.98}
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
    BoxLayout:
        orientation: 'vertical'
        size_hint: 1, None
        height: dp(150) 
        pos_hint: {'center_x': 0.496, 'y': 0.615}
        spacing: dp(-40)
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
    BoxLayout:
        orientation: 'vertical'
        size_hint: 0.95, None  
        height: dp(230)        
        pos_hint: {'center_x': 0.5, 'y': 0.07}
        spacing: dp(40)
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
                background_color: 0, 0, 0, 0 
                foreground_color: 1, 1, 1, 1  
                hint_text_color: 1, 1, 1, 0.5 
                cursor_color: 0.2, 0.6, 1, 1
                padding: [10, 15]
                on_text_validate: root.check_answer(self)
            SmoothButton:
                text: ""
                font_name: 'LEELAUIB.TTF'
                font_size: '25sp' 
                bold: True
                size_hint_x: 0.35
                bg_color: 0, 0, 0, 0 
                shadow_color: 0, 0, 0, 0
                color: 1, 1, 1, 1
                on_release: root.check_answer(self)
        GridLayout:
            cols: 2
            spacing: dp(10)
            size_hint_y: None
            height: dp(140)
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
            CardBox:
                orientation: 'vertical'
                padding: dp(5)
                Label:
                    text: "Type fast, ghost is coming!"
                    font_size: '15sp'
                    font_name: 'LEELAUIB.TTF'
                    color: 1, 1, 1, 0.5
                    bold: True
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

class MainMenuScreen(Screen):
    def on_enter(self, *args):
        app = App.get_running_app()
        app.sound.play_menu_bgm()
        self.update_highscore()

    def update_highscore(self):
        highscore = 0
        try:
            # --- แก้ Path ไปที่โฟลเดอร์ data/ ---
            if os.path.exists('data/highscore.json'):
                with open('data/highscore.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    highscore = data.get('highscore', 0)
        except Exception as e:
            print(f"Error loading highscore: {e}")
        self.ids.highscore_label.text = f'🏆 สูงสุด: {highscore}'

class OptionsScreen(Screen):
    pass

class GameStartMenuScreen(Screen):
    selected_category = None
    selected_difficulty = None

    def select_category(self, category_name):
        self.selected_category = category_name
        self.ids.underscore_label.text = f"{category_name}"
        self.ids.underscore_label.color = (0.2, 1, 0.2, 1)

    def select_difficulty(self, diff_level):
        self.selected_difficulty = diff_level
        default_color = (1, 1, 1, 1)
        selected_color = (1, 0.6, 0.2, 1)

        self.ids.diff_1_label.color = default_color
        self.ids.diff_2_label.color = default_color
        self.ids.diff_3_label.color = default_color
        self.ids.diff_4_label.color = default_color
        self.ids.diff_5_label.color = default_color

        if diff_level == 1: self.ids.diff_1_label.color = selected_color
        elif diff_level == 2: self.ids.diff_2_label.color = selected_color
        elif diff_level == 3: self.ids.diff_3_label.color = selected_color
        elif diff_level == 4: self.ids.diff_4_label.color = selected_color
        elif diff_level == 5: self.ids.diff_5_label.color = selected_color

    def start_game(self):
        if self.selected_category and self.selected_difficulty:
            app = App.get_running_app()
            app.sound.play_click()
            app.start_game_with_settings(self.selected_category, str(self.selected_difficulty))
        else:
            app = App.get_running_app()
            app.sound.play_noscore()
            anim = Animation(color=(1, 0, 0, 1), duration=0.1) + Animation(color=(1, 1, 1, 1), duration=0.1)
            anim.start(self.ids.underscore_label)

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
        self.level_label = self.ids.level_label
        self.answer_input = self.ids.answer_input
        self.scooby = self.ids.scooby
        self.pause_overlay = self.ids.pause_overlay

        self.answer_input.bind(text=self.on_text_change)

        self.ghost = Ghost()
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
        
        if value != "":
            self.sound.play_typing_sound()
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
            # --- แก้ Path ไปที่โฟลเดอร์ data/ ---
            if os.path.exists('data/highscore.json'):
                with open('data/highscore.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    highscore = data.get('highscore', 0)
        except Exception as e:
            print(f"Error loading highscore: {e}")

        if self.logic.score > highscore:
            try:
                # --- แก้ Path ไปที่โฟลเดอร์ data/ ---
                with open('data/highscore.json', 'w', encoding='utf-8') as f:
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
            base_scooby_y = self.height * 0.30  
            anim = Animation(y=base_scooby_y + dp(10), duration=0.5) + Animation(y=base_scooby_y, duration=0.5)
            anim.start(self.scooby)
            base_ghost_y = base_scooby_y - dp(10) 
            g_anim = Animation(y=base_ghost_y + dp(20), duration=0.5) + Animation(y=base_ghost_y, duration=0.5)
            g_anim.start(self.ghost)

    def trigger_screen_shake(self):
        if getattr(self, 'is_shaking', False):
            return
        self.is_shaking = True
        og_pos = (self.x, self.y) 
        anim = Animation(pos=(og_pos[0]-15, og_pos[1]+15), duration=0.05) + \
               Animation(pos=(og_pos[0]+15, og_pos[1]-15), duration=0.05) + \
               Animation(pos=og_pos, duration=0.05)
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
            # --- แก้ Path ไปที่โฟลเดอร์ data/ ---
            with open('data/vocab_data.json', 'r', encoding='utf-8') as f:
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
        if self.is_paused or self.hp.is_dead():
            return
        if not self.vocab_pool and not getattr(self, 'current_word', None): 
            return
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
            
        new_time_text = f"Time: {int(self.time_left)}s"
        if self.time_label.text != new_time_text:
            self.time_label.text = new_time_text
            self.time_label.color = t_color
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
            if self.time_left >= 10:
                speed_bonus = 30; rating_text = "PERFECT!"; r_color = (1, 0.8, 0.1, 1) 
            elif self.time_left >= 5:
                speed_bonus = 15; rating_text = "GREAT!"; r_color = (0.2, 1, 0.2, 1) 
            else:
                speed_bonus = 5; rating_text = "GOOD!"; r_color = (0.4, 0.9, 1, 1) 
                
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
            self.answer_input.text = "" 
            anim_shake = Animation(x=self.answer_input.x-10, duration=0.05) + Animation(x=self.answer_input.x+10, duration=0.05) + Animation(x=self.answer_input.x, duration=0.05)
            anim_shake.start(self.answer_input)
            self.add_widget(FloatingText("MISS!", (self.center_x - dp(40), self.answer_input.y + dp(60)), color=(1, 0.2, 0.2, 1)))
            self.logic.combo_multiplier = 1
            if self.time_speed > 1.0: self.time_speed = 1.0 
            self.update_ui()
            Clock.schedule_once(lambda dt: self._force_focus(), 0.1)
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
        self.answer_input.text = ""
        self.answer_input.disabled = True 
        self.update_ui()
        
        correct_ans = self.current_word.get("english", "")
        spaced_ans = " ".join(list(correct_ans.upper()))
        self.underscore_label.text = spaced_ans
        self.underscore_label.color = (1, 0.2, 0.2, 1) 
        
        if self.hp.is_dead():
            Clock.schedule_once(lambda dt: self.trigger_game_over(), 1.5)
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
    
    def setup_ghost_position(self, dt):
        self.ghost.size_hint = (None, None)
        self.ghost.pos_hint = {}
        self.ghost.size = (dp(300), dp(300)) 
        self.ghost.start_x = self.width + 50
        if not self.game_started:
            self.ghost.x = self.ghost.start_x
        self.ghost.end_x = self.scooby.right - dp(10)
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

class VocabGameApp(App):
    volume_level = NumericProperty(0.3) 
    bg_music = None
    previous_screen = 'main_menu' 

    def build(self):
        self.sound = SoundManager()
        self.sound.play_menu_bgm()

        sm = ScreenManager()
        
        menu_screen = MainMenuScreen(name='main_menu')
        options_screen = OptionsScreen(name='options_screen')
        start_menu_screen = GameStartMenuScreen(name='start_menu') 
        game_screen = GameScreen(name='game_screen')
        
        game_layout = MainLayout()
        game_screen.add_widget(game_layout)
        
        sm.add_widget(menu_screen)
        sm.add_widget(start_menu_screen) 
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