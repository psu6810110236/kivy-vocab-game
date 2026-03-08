from kivy.uix.image import Image
from kivy.core.window import Window

class Ghost(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = "assets/images/gostss.png"
        self.size_hint = (None, None)
        self.size = (300, 300)

        self.start_x = Window.width + 100    
        self.end_x = 80
        self.x = self.start_x
        
        self.is_paused = False

    def sync_position(self, current_time, max_time):
        # ฟังก์ชันให้ main.py จับผีวางตามสัดส่วนเวลาเป๊ะๆ
        if self.is_paused or max_time <= 0:
            return
        
        progress = current_time / max_time
        progress = max(0.0, min(1.0, progress))
        
        self.x = self.end_x + (self.start_x - self.end_x) * progress

    def reset(self):
        self.x = self.start_x