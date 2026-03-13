import sys
import os

# 1. หาพาธ (Path) ปัจจุบันของโฟลเดอร์ที่ไฟล์ main.py นี้ตั้งอยู่
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 2. นำโฟลเดอร์ 'src' เข้าไปในระบบพจนานุกรมพาธของ Python 
# (เพื่อให้เราสามารถ import โมดูลใน src ได้โดยตรงเหมือนกับตอนที่คุณยังไม่ได้แยกโฟลเดอร์)
SRC_DIR = os.path.join(BASE_DIR, 'src')
sys.path.insert(0, SRC_DIR)

# 3. นำเข้า App หลักจากไฟล์ src/app.py
try:
    from app import VocabGameApp
except ModuleNotFoundError as e:
    # ดักจับ Error เผื่อว่าหาไฟล์ app.py ไม่เจอ หรือมีการ import ภายในผิดพลาด
    print(f"\n[ แจ้งเตือน Error ] ไม่สามารถโหลดโมดูลได้: {e}")
    print("โปรดตรวจสอบว่าคุณมีไฟล์ 'src/app.py' และแก้ไขการ import ในไฟล์อื่นๆ ครบแล้ว\n")
    sys.exit(1)

# 4. จุดเริ่มต้นการรันโปรแกรม
if __name__ == '__main__':
    # รันแอปพลิเคชัน
    VocabGameApp().run()