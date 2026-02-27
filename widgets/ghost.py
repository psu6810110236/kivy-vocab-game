from kivy.uix.image import Image
from kivy.clock import Clock

class Ghost(Image):
    def __init__(self, on_hit_callback, travel_time=16, **kwargs):
        super().__init__(**kwargs)
        self.source = "assets/images/ghost.png"
        self.size_hint = (None, None)
        self.size = (120, 120)

        self.start_x = 900
        self.end_x = 0
        self.pos = (self.start_x, 100)

        self.travel_time = travel_time  # เวลาที่ใช้เดินถึง Scooby
        self.elapsed_time = 0

        self.on_hit_callback = on_hit_callback
        Clock.schedule_interval(self.update, 1/60)

    def update(self, dt):
        self.elapsed_time += dt
        progress = self.elapsed_time / self.travel_time

        # เคลื่อนที่ตามสัดส่วนเวลา
        self.x = self.start_x - (self.start_x - self.end_x) * progress

        if progress >= 1:
            self.on_hit_callback()
            self.reset()

    def reset(self):
        self.elapsed_time = 0
        self.x = self.start_x