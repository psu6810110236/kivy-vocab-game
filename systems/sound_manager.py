from kivy.core.audio import SoundLoader

class SoundManager:
    def __init__(self):
        self.correct = SoundLoader.load("assets/sound/correct.wav")
        self.wrong = SoundLoader.load("assets/sound/wrong.wav")
        self.gameover = SoundLoader.load("assets/sound/gameover.wav")
        self.click = SoundLoader.load("assets/sound/click_start_botton.mp3")  # 👈 เพิ่มตรงนี้
        
        # ปรับความดังได้
        if self.click:
            self.click.volume = 0.5

    def play_correct(self):
        if self.correct:
            self.correct.stop()
            self.correct.play()

    def play_wrong(self):
        if self.wrong:
            self.wrong.stop()
            self.wrong.play()

    def play_gameover(self):
        if self.gameover:
            self.gameover.stop()
            self.gameover.play()

    def play_click(self):   # 👈 เพิ่มฟังก์ชันนี้
        if self.click:
            self.click.stop()   # กันเสียงซ้อน
            self.click.play()