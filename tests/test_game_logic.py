import unittest
from systems.game_logic import GameLogic

# 1. สร้าง Mock (ตัวจำลอง) ของ HPSystem เพื่อให้ GameLogic เรียกใช้ได้ตอนเทส
class MockHPSystem:
    def __init__(self, max_hp=3):
        self.max_hp = max_hp
        self.current_hp = max_hp

    def take_damage(self):
        self.current_hp -= 1

class TestGameLogic(unittest.TestCase):
    def setUp(self):
        # โค้ดส่วนนี้จะรันใหม่ทุกครั้งก่อนเริ่มแต่ละเทส
        self.hp = MockHPSystem()
        self.logic = GameLogic(self.hp)

    def test_correct_answer(self):
        """เทสการตอบคำถามถูกต้อง"""
        result = self.logic.check_answer("cat", "cat")
        self.assertTrue(result)
        self.assertEqual(self.logic.score, 10)
        self.assertEqual(self.logic.streak, 1)

    def test_incorrect_answer_and_combo_reset(self):
        """เทสการตอบผิด และเช็คว่า Combo ต้องถูกรีเซ็ต"""
        # สมมติว่าตอบถูกมาก่อน 3 ครั้ง
        self.logic.streak = 3
        self.logic.combo_multiplier = 2
        
        result = self.logic.check_answer("dog", "cat")
        self.assertFalse(result)
        self.assertEqual(self.logic.streak, 0)
        self.assertEqual(self.logic.combo_multiplier, 1)

    def test_combo_multiplier_upgrade(self):
        """เทสว่าถ้าตอบถูกติดกัน Combo x2 และ x3 จะทำงานไหม"""
        # ตอบถูก 3 ครั้ง (ได้โบนัส x2)
        for _ in range(3):
            self.logic.check_answer("dog", "dog")
        self.assertEqual(self.logic.combo_multiplier, 2)
        
        # ตอบถูกเพิ่มอีก 2 ครั้ง รวมเป็น 5 ครั้ง (ต้องได้โบนัส x3)
        self.logic.check_answer("pig", "pig")
        self.logic.check_answer("cow", "cow")
        self.assertEqual(self.logic.combo_multiplier, 3)

    def test_buy_life_success(self):
        """เทสการซื้อชีวิตเมื่อคะแนนพอและเลือดไม่เต็ม"""
        self.logic.score = 60
        self.hp.current_hp = 2 # สมมติว่าเลือดลดไป 1
        
        success = self.logic.buy_life(cost=50)
        self.assertTrue(success)
        self.assertEqual(self.hp.current_hp, 3)
        self.assertEqual(self.logic.score, 10) # 60 - 50 = 10

    def test_buy_life_fail_full_hp(self):
        """เทสการซื้อชีวิตต้องไม่สำเร็จถ้าเลือดเต็มอยู่แล้ว"""
        self.logic.score = 100
        self.hp.current_hp = 3 # เลือดเต็ม (Max = 3)
        
        success = self.logic.buy_life(cost=50)
        self.assertFalse(success)
        self.assertEqual(self.logic.score, 100) # คะแนนต้องไม่ลด

    def test_get_hint(self):
        """เทสการขอคำใบ้และตัดคะแนน"""
        self.logic.score = 30
        hint = self.logic.get_hint("apple", cost=20)
        
        self.assertEqual(hint, "ap___") # ตัวอักษร 2 ตัวแรก + เส้นใต้ 3 ตัว
        self.assertEqual(self.logic.score, 10)

if __name__ == '__main__':
    unittest.main()