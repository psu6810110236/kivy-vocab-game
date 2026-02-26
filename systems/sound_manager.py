from kivy.core.audio import SoundLoader

class SoundManager:
    def __init__(self):
        self.correct = SoundLoader.load("assets/correct.wav")
        self.wrong = SoundLoader.load("assets/wrong.wav")
        self.gameover = SoundLoader.load("assets/gameover.wav")
    def play_correct(self):
        if self.correct:
            self.correct.play()

    def play_wrong(self):
        if self.wrong:
            self.wrong.play()

    def play_gameover(self):
        if self.gameover:
            self.gameover.play()