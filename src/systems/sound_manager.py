from kivy.core.audio import SoundLoader
from kivy.clock import Clock
class SoundManager:
    def __init__(self):
        self.correct = SoundLoader.load("assets/sound/correct.wav")
        self.wrong = SoundLoader.load("assets/sound/wrong.wav")
        self.gameover = SoundLoader.load("assets/sound/gameover.wav")
        self.click = SoundLoader.load("assets/sound/click_start_botton.mp3")  # 👈 เพิ่มตรงนี้
        self.menu_bgm = SoundLoader.load('assets/sound/music/menu_theme.mp3')
        self.game_bgm = SoundLoader.load('assets/sound/music/theme.mp3')
        self.shop_eror = SoundLoader.load('assets/sound/shop_error.mp3')
        self.typing_sound = SoundLoader.load('assets/sound/typing.mp3')
        self.wrong_answer_sound = SoundLoader.load('assets/sound/wrong_answer.mp3')
        self.sfx_thunder = SoundLoader.load('assets/sound/thunder.mp3')
        self.sfx_poltergeist = SoundLoader.load('assets/sound/whisper.mp3')
        self.sfx_jumpscare = SoundLoader.load('assets/sound/scream.mp3')
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

        self.typing_sounds = []
        for _ in range(5): 
            sound = SoundLoader.load('assets/sound/typing.mp3')
            # แนะนำ: ถ้าเสียงยังหน่วง ลองเปลี่ยนไฟล์จาก .mp3 เป็น .wav จะทำงานได้ไวกว่าใน Kivy ครับ
            if sound:
                self.typing_sounds.append(sound)
        
        self.typing_index = 0

    def play_correct(self):
        if self.correct:
            self.correct.stop()
            self.correct.play()

    def play_wrong(self):
        if self.wrong:
            self.wrong.stop()
            self.wrong.play()
    def play_noscore(self):
        if self.shop_eror:
            self.shop_eror.stop()
            self.shop_eror.play()

    def play_gameover(self):
        if self.gameover:
            self.gameover.stop()
            self.gameover.play()
    
    def play_typing_sound(self):
        if self.typing_sounds:
            # ดึงเสียงก้อนปัจจุบันออกมาเล่น
            sound = self.typing_sounds[self.typing_index]
            
            if sound.state == 'play':
                sound.stop()
            sound.play()
            
            # ขยับคิวไปเล่นก้อนถัดไป (ถ้าครบ 5 ก็วนกลับไป 0 ใหม่)
            self.typing_index += 1
            if self.typing_index >= len(self.typing_sounds):
                self.typing_index = 0

    def play_wrong_answer(self):
        if self.wrong_answer_sound:
            self.wrong_answer_sound.stop()
            self.wrong_answer_sound.play()
    
    def play_click(self):   
        if self.click:
            self.click.stop()   
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
    
    def play_thunder(self):
        if self.sfx_thunder:
            self.sfx_thunder.play()

    def play_poltergeist(self):
        if self.sfx_poltergeist:
            self.sfx_poltergeist.play()
            Clock.schedule_once(lambda dt: self.sfx_poltergeist.stop(), 2.0)
    def play_jumpscare(self):
        if self.sfx_jumpscare:
            self.sfx_jumpscare.play()