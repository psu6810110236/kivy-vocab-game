from kivy.uix.image import Image
from kivy.clock import Clock

class Ghost(Image):
    def __init__(self, on_hit_callback, **kwargs):
        super().__init__(**kwargs)
        self.source = "assets/images/ghost.png"  # ใส่รูปทีหลังได้
        self.size_hint = (None, None)
        self.size = (120, 120)

        self.start_x = 900   # เริ่มขวา
        self.pos = (self.start_x, 100)

        self.speed = 2.0
        self.on_hit_callback = on_hit_callback

        Clock.schedule_interval(self.update, 1/60)

    def update(self, dt):
        self.x -= self.speed

        # ชนผู้เล่น (ซ้ายสุด)
        if self.x <= 0:
            self.on_hit_callback()
            self.reset()

    def reset(self):
        self.x = self.start_x