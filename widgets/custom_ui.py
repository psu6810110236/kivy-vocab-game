from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
import os

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
        
        # อนิเมชันลอยขึ้นและจางหาย
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
        # กำหนดว่าแต่ละท่ามีกี่รูป (ถ้าอนาคตมี 3 รูปก็มาแก้เลขตรงนี้ได้)
        self.max_frames = {'idle': 2, 'happy': 2, 'scared': 2} 
        
        # เปลี่ยนรูปทุกๆ 0.2 วินาที (ปรับความเร็วตรงนี้ได้)
        Clock.schedule_interval(self.update_frame, 0.2)

    def update_frame(self, dt):
        if self.state == 'idle':
            speed = 0.9   # ท่ายืนปกติ สลับรูปทุก 0.5 วิ
        elif self.state == 'happy':
            speed = 0.2   # <--- ท่าดีใจ ปรับให้ช้าลง มองทันแน่นอน
        else:
            speed = 0.15  # ท่าตกใจ ปรับให้สลับเร็วๆ รัวๆ
            
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
