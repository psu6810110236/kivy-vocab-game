from kivy.core.audio import SoundLoader

class SoundManager:
    def __init__(self):
        self.correct = SoundLoader.load("assets/sound/correct.wav")
        self.wrong = SoundLoader.load("assets/sound/wrong.wav")
        self.gameover = SoundLoader.load("assets/sound/gameover.wav")
        self.click = SoundLoader.load("assets/sound/click_start_botton.mp3")  # 👈 เพิ่มตรงนี้
        self.menu_bgm = SoundLoader.load('assets/sound/music/menu_theme.mp3')
        self.game_bgm = SoundLoader.load('assets/sound/music/theme.mp3')
        
        # 2. ตั้งค่าระดับเสียงและการวนลูป (Loop)
        if self.menu_bgm:
            self.menu_bgm.volume = 0.3
            self.menu_bgm.loop = True
            
        if self.game_bgm:
            self.game_bgm.volume = 0.3
            self.game_bgm.loop = True
        
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

    def play_menu_bgm(self):
        """หยุดเพลงเกมแล้วเล่นเพลงเมนู"""
        if self.game_bgm and self.game_bgm.state == 'play':
            self.game_bgm.stop()
        if self.menu_bgm and self.menu_bgm.state != 'play':
            self.menu_bgm.play()

    def play_game_bgm(self):
        """หยุดเพลงเมนูแล้วเล่นเพลงเกม"""
        if self.menu_bgm and self.menu_bgm.state == 'play':
            self.menu_bgm.stop()
        if self.game_bgm and self.game_bgm.state != 'play':
            self.game_bgm.play()

    def stop_all_bgm(self):
        """ปิดเพลงพื้นหลังทั้งหมด"""
        if self.menu_bgm:
            self.menu_bgm.stop()
        if self.game_bgm:
            self.game_bgm.stop()