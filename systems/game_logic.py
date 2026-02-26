# systems/game_logic.py

class GameLogic:
    def __init__(self, hp_system):
        # รับ instance ของ HPSystem เข้ามาทำงานร่วมกัน
        self.hp = hp_system  
        self.score = 0
        self.streak = 0
        self.combo_multiplier = 1

    def check_answer(self, user_answer, correct_word):
        """ระบบตรวจคำตอบ (Thai -> English) และจัดการคะแนน/ชีวิต"""
        # แปลงเป็นตัวพิมพ์เล็กและตัดช่องว่างเพื่อความแม่นยำในการตรวจ
        if str(user_answer).strip().lower() == str(correct_word).strip().lower():
            # ตอบถูก: เพิ่มคะแนนตามตัวคูณ Combo และเพิ่ม Streak
            self.score += (10 * self.combo_multiplier)
            self.streak += 1
            self.update_combo()
            return True
        else:
            # ตอบผิด: ลดชีวิต 1 แต้ม และรีเซ็ต Streak/Combo
            self.hp.take_damage(1)
            self.streak = 0
            self.combo_multiplier = 1
            return False

    def update_combo(self):
        """ระบบ Combo / Streak (โบนัสคูณคะแนน)"""
        if self.streak >= 5:
            self.combo_multiplier = 3  # ตอบถูกติดกัน 5 ครั้ง คะแนน x3
        elif self.streak >= 3:
            self.combo_multiplier = 2  # ตอบถูกติดกัน 3 ครั้ง คะแนน x2

    def buy_life(self, cost=50):
        """ระบบซื้อชีวิต (หักคะแนนเพื่อเพิ่ม HP)"""
        if self.score >= cost and self.hp.current_hp < self.hp.max_hp:
            self.score -= cost
            self.hp.current_hp += 1
            return True
        return False

    def get_hint(self, word, cost=20):
        """ระบบ Hint (หักคะแนนเพื่อดูตัวอักษร 2 ตัวแรก)"""
        if self.score >= cost:
            self.score -= cost
            if len(word) > 2:
                return f"{word[:2]}{'_' * (len(word) - 2)}"
            return f"{word[0]}_"
        return None