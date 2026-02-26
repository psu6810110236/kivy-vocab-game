from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.uix.progressbar import ProgressBar
LabelBase.register(DEFAULT_FONT, 'LEELAWUI.TTF')
import random

# Import ระบบต่างๆ ของเรา
from systems.sound_manager import SoundManager
from systems.hp_system import HPSystem
from systems.game_logic import GameLogic 

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=10, padding=10, **kwargs)

        # 1. โหลดระบบพื้นฐาน
        self.sound = SoundManager()
        self.hp = HPSystem(max_hp=3)
        self.logic = GameLogic(self.hp)

        # ระบบเวลา
        self.time_left = 60.0  
        self.time_speed = 1.00  
        # เปลี่ยนเป็นอัปเดตทุก 0.1 วิ เพื่อให้หลอดเวลาลดแบบสมูทๆ
        Clock.schedule_interval(self.update_timer, 0.10) 

        # 2. Mock ข้อมูลคำศัพท์ 100 คำ
        self.vocab_list = [
            {"thai": "แมว", "english": "cat"}, {"thai": "หมา", "english": "dog"},
            {"thai": "นก", "english": "bird"}, {"thai": "แอปเปิ้ล", "english": "apple"},
            {"thai": "โรงเรียน", "english": "school"}, {"thai": "มด", "english": "ant"},
            {"thai": "หมี", "english": "bear"}, {"thai": "วัว", "english": "cow"},
            {"thai": "เป็ด", "english": "duck"}, {"thai": "ช้าง", "english": "elephant"},
            {"thai": "ปลา", "english": "fish"}, {"thai": "แพะ", "english": "goat"},
            {"thai": "ม้า", "english": "horse"}, {"thai": "กิ้งก่า", "english": "iguana"},
            {"thai": "แมงกะพรุน", "english": "jellyfish"}, {"thai": "จิงโจ้", "english": "kangaroo"},
            {"thai": "สิงโต", "english": "lion"}, {"thai": "ลิง", "english": "monkey"},
            {"thai": "รังนก", "english": "nest"}, {"thai": "นกฮูก", "english": "owl"},
            {"thai": "หมู", "english": "pig"}, {"thai": "นกกระทา", "english": "quail"},
            {"thai": "กระต่าย", "english": "rabbit"}, {"thai": "งู", "english": "snake"},
            {"thai": "เสือ", "english": "tiger"}, {"thai": "ร่ม", "english": "umbrella"},
            {"thai": "รถตู้", "english": "van"}, {"thai": "ปลาวาฬ", "english": "whale"},
            {"thai": "ไซโลโฟน", "english": "xylophone"}, {"thai": "จามรี", "english": "yak"},
            {"thai": "ม้าลาย", "english": "zebra"}, {"thai": "เด็กผู้ชาย", "english": "boy"},
            {"thai": "เด็กผู้หญิง", "english": "girl"}, {"thai": "ผู้ชาย", "english": "man"},
            {"thai": "ผู้หญิง", "english": "woman"}, {"thai": "หนังสือ", "english": "book"},
            {"thai": "ปากกา", "english": "pen"}, {"thai": "ดินสอ", "english": "pencil"},
            {"thai": "ยางลบ", "english": "eraser"}, {"thai": "ไม้บรรทัด", "english": "ruler"},
            {"thai": "โต๊ะเรียน", "english": "desk"}, {"thai": "เก้าอี้", "english": "chair"},
            {"thai": "โต๊ะ", "english": "table"}, {"thai": "ประตู", "english": "door"},
            {"thai": "หน้าต่าง", "english": "window"}, {"thai": "เตียง", "english": "bed"},
            {"thai": "ห้อง", "english": "room"}, {"thai": "บ้าน", "english": "house"},
            {"thai": "หลังคา", "english": "roof"}, {"thai": "กำแพง", "english": "wall"},
            {"thai": "พระอาทิตย์", "english": "sun"}, {"thai": "พระจันทร์", "english": "moon"},
            {"thai": "ดาว", "english": "star"}, {"thai": "ท้องฟ้า", "english": "sky"},
            {"thai": "เมฆ", "english": "cloud"}, {"thai": "ฝน", "english": "rain"},
            {"thai": "หิมะ", "english": "snow"}, {"thai": "ลม", "english": "wind"},
            {"thai": "ไฟ", "english": "fire"}, {"thai": "น้ำ", "english": "water"},
            {"thai": "ต้นไม้", "english": "tree"}, {"thai": "ดอกไม้", "english": "flower"},
            {"thai": "หญ้า", "english": "grass"}, {"thai": "ใบไม้", "english": "leaf"},
            {"thai": "ราก", "english": "root"}, {"thai": "สีแดง", "english": "red"},
            {"thai": "สีเขียว", "english": "green"}, {"thai": "สีน้ำเงิน", "english": "blue"},
            {"thai": "สีเหลือง", "english": "yellow"}, {"thai": "สีดำ", "english": "black"},
            {"thai": "สีขาว", "english": "white"}, {"thai": "สีส้ม", "english": "orange"},
            {"thai": "สีชมพู", "english": "pink"}, {"thai": "สีม่วง", "english": "purple"},
            {"thai": "สีน้ำตาล", "english": "brown"}, {"thai": "สีเทา", "english": "gray"},
            {"thai": "หนึ่ง", "english": "one"}, {"thai": "สอง", "english": "two"},
            {"thai": "สาม", "english": "three"}, {"thai": "สี่", "english": "four"},
            {"thai": "ห้า", "english": "five"}, {"thai": "หก", "english": "six"},
            {"thai": "เจ็ด", "english": "seven"}, {"thai": "แปด", "english": "eight"},
            {"thai": "เก้า", "english": "nine"}, {"thai": "สิบ", "english": "ten"},
            {"thai": "กิน", "english": "eat"}, {"thai": "ดื่ม", "english": "drink"},
            {"thai": "นอน", "english": "sleep"}, {"thai": "วิ่ง", "english": "run"},
            {"thai": "เดิน", "english": "walk"}, {"thai": "กระโดด", "english": "jump"},
            {"thai": "ว่ายน้ำ", "english": "swim"}, {"thai": "บิน", "english": "fly"},
            {"thai": "อ่าน", "english": "read"}, {"thai": "เขียน", "english": "write"},
            {"thai": "พูด", "english": "speak"}, {"thai": "ฟัง", "english": "listen"},
            {"thai": "เล่น", "english": "play"}, {"thai": "ทำงาน", "english": "work"}
        ]
        self.current_word = random.choice(self.vocab_list)

        # --- สร้างหน้าตา UI ---
        
        # ส่วนที่ 0: หลอดเวลา (เพิ่มเข้ามาใหม่)
        time_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.15))
        self.time_label = Label(text=f"Time: {int(self.time_left)}s", font_size=24, color=(1, 0.8, 0, 1))
        # สร้าง ProgressBar ตั้งค่าสูงสุดที่ 60 
        self.time_bar = ProgressBar(max=60, value=self.time_left, size_hint=(0.8, 1), pos_hint={'center_x': 0.5})
        
        time_layout.add_widget(self.time_label)
        time_layout.add_widget(self.time_bar)
        self.add_widget(time_layout)

        # ส่วนที่ 1: แถบสถานะ (HP, คะแนน, คอมโบ)
        status_layout = BoxLayout(size_hint=(1, 0.15))
        self.hp_label = Label(text=f"HP: {self.hp.current_hp}/{self.hp.max_hp}", font_size=24)
        self.score_label = Label(text=f"Score: {self.logic.score}", font_size=24)
        self.combo_label = Label(text=f"Combo: x{self.logic.combo_multiplier} (Streak: {self.logic.streak})", font_size=20)
        
        status_layout.add_widget(self.hp_label)
        status_layout.add_widget(self.score_label)
        status_layout.add_widget(self.combo_label)
        self.add_widget(status_layout)

        # ส่วนที่ 2: พื้นที่ทายคำศัพท์
        game_layout = BoxLayout(orientation="vertical", size_hint=(1, 0.4), spacing=10)
        self.word_label = Label(text=f"คำศัพท์: {self.current_word['thai']}", font_size=36, bold=True)
        self.answer_input = TextInput(hint_text="พิมพ์คำแปลภาษาอังกฤษที่นี่...", multiline=False, font_size=28, halign="center")
        self.answer_input.bind(on_text_validate=self.check_answer) 
        
        submit_btn = Button(text="ส่งคำตอบ", font_size=24, size_hint=(1, 0.6), background_color=(0.2, 0.6, 1, 1))
        submit_btn.bind(on_press=self.check_answer)
        
        game_layout.add_widget(self.word_label)
        game_layout.add_widget(self.answer_input)
        game_layout.add_widget(submit_btn)
        self.add_widget(game_layout)

        # ส่วนที่ 3: ร้านค้าแลกแต้ม
        shop_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        buy_life_btn = Button(text="ซื้อชีวิต (50)", font_size=20)
        buy_life_btn.bind(on_press=self.buy_life)
        
        hint_btn = Button(text="ขอคำใบ้ (20)", font_size=20)
        hint_btn.bind(on_press=self.get_hint)

        slow_time_btn = Button(text="หน่วงเวลา (30)", font_size=20, background_color=(0.5, 0.2, 0.8, 1))
        slow_time_btn.bind(on_press=self.buy_slow_time)
        
        shop_layout.add_widget(buy_life_btn)
        shop_layout.add_widget(hint_btn)
        shop_layout.add_widget(slow_time_btn)
        self.add_widget(shop_layout)

        # ส่วนที่ 4: ปุ่มสำหรับ Test 
        test_layout = BoxLayout(size_hint=(1, 0.15), spacing=10)
        test_add_btn = Button(text="[Test] +10 คะแนน", font_size=20, background_color=(0, 0.8, 0, 1))
        test_add_btn.bind(on_press=self.test_add_score)
        
        test_reduce_btn = Button(text="[Test] -10 คะแนน", font_size=20, background_color=(0.8, 0, 0, 1))
        test_reduce_btn.bind(on_press=self.test_reduce_score)
        
        test_layout.add_widget(test_add_btn)
        test_layout.add_widget(test_reduce_btn)
        self.add_widget(test_layout)

    # --- ฟังก์ชันการทำงาน ---
    
    def update_timer(self, dt):
        """ลูปนับเวลาถอยหลัง (รันทุกๆ 0.1 วินาที)"""
        if self.hp.is_dead() or self.time_left <= 0:
            return False  
        self.time_speed += 0.001  # เพิ่มความเร็วการนับเวลาขึ้นเรื่อยๆ (บัฟหน่วงเวลาจะลดความเร็วนี้ลงชั่วคราว)
        # หักเวลาตามตัวคูณความเร็ว (คูณ 0.1 เพราะฟังก์ชันถูกเรียกถี่ขึ้น 10 เท่า)
        self.time_left -= (self.time_speed * 0.1) 
        
        if self.time_left <= 0:
            self.time_left = 0
            self.sound.play_gameover()
            self.word_label.text = "TIME'S UP! GAME OVER!"
            self.answer_input.disabled = True
            
        # อัปเดตทั้งข้อความและหลอด Progress Bar
        self.time_label.text = f"Time: {int(self.time_left)}s (Speed: {self.time_speed:.2f}x)"
        self.time_bar.value = self.time_left

    def update_ui(self):
        """อัปเดตข้อความบนหน้าจอให้ตรงกับข้อมูลปัจจุบัน"""
        self.hp_label.text = f"HP: {self.hp.current_hp}/{self.hp.max_hp}"
        self.score_label.text = f"Score: {self.logic.score}"
        self.combo_label.text = f"Combo: x{self.logic.combo_multiplier} (Streak: {self.logic.streak})"
        self.word_label.text = f"คำศัพท์: {self.current_word['thai']}"

    def next_word(self):
        """สุ่มคำศัพท์ใหม่และล้างช่องพิมพ์"""
        self.current_word = random.choice(self.vocab_list)
        self.answer_input.text = ""
        self.update_ui()

    def check_answer(self, instance):
        """ตรวจคำตอบเมื่อกดปุ่ม หรือกด Enter"""
        if self.hp.is_dead() or self.time_left <= 0:
            return  

        user_ans = self.answer_input.text
        correct_ans = self.current_word["english"]
        
        is_correct = self.logic.check_answer(user_ans, correct_ans)
        
        if is_correct:
            self.sound.play_correct()
            self.time_left += 3  # โบนัส ตอบถูกบวกเวลา 3 วินาที
            
            # ถ้าโบนัสทำให้เวลาเกินหลอด ให้ขยายขีดจำกัดหลอดตามไปด้วย
            if self.time_left > self.time_bar.max:
                self.time_bar.max = self.time_left
            self.time_bar.value = self.time_left
            
            self.next_word()
        else:
            self.sound.play_wrong()
            self.answer_input.text = "" 
            if self.time_speed > 1.0:
                self.time_speed = 1.0 # <--- ตอบผิดก็โดนรีเซ็ตบัฟหน่วงเวลาด้วย
            self.update_ui()
            
            if self.hp.is_dead():
                self.sound.play_gameover()
                self.word_label.text = "GAME OVER!"
                self.answer_input.disabled = True 

    def buy_life(self, instance):
        if self.logic.buy_life(cost=50):
            self.update_ui()

    def get_hint(self, instance):
        hint = self.logic.get_hint(self.current_word["english"], cost=20)
        if hint:
            self.answer_input.text = hint
            self.update_ui()

    def buy_slow_time(self, instance):
        """แลกแต้มเพื่อให้เวลานับถอยหลังช้าลงใน 1 Turn"""
        cost = 30
        if self.logic.score >= cost:
            if self.time_speed > 0.5: 
                self.logic.score -= cost
                self.time_speed -= 0.1  # ลดอัตราการนับเวลาลงแบบเห็นผลชัดเจน (เฉพาะข้อนี้)
                self.update_ui()
                print(f"เวลาเดินช้าลง! (ความเร็วปัจจุบัน: {self.time_speed:.1f})")
            else:
                print("หน่วงเวลาถึงขีดสุดแล้วสำหรับข้อนี้!")
        else:
            print("คะแนนไม่พอซื้อบัฟหน่วงเวลา!")

    def test_add_score(self, instance):
        self.logic.score += 10
        self.update_ui()

    def test_reduce_score(self, instance):
        self.logic.score -= 10
        if self.logic.score < 0:
            self.logic.score = 0
        self.update_ui()

class VocabGameApp(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    VocabGameApp().run()