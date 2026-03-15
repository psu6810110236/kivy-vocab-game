import sys
import os
from kivy.config import Config

# รองรับการ resize หน้าจอทุกขนาด (PC, Mobile, Tablet)
Config.set('graphics', 'resizable', True)
# ลบการล็อคขนาดออก — Kivy จะใช้ขนาดหน้าจอจริงของอุปกรณ์แทน

# 1. หาตำแหน่งปัจจุบันของโฟลเดอร์ที่ไฟล์ main.py นี้ตั้งอยู่
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 2. นำโฟลเดอร์ src เข้าไปในระบบของ Python
SRC_DIR = os.path.join(BASE_DIR, 'src')
sys.path.insert(0, SRC_DIR)

# 3. นำเข้า App หลักจากไฟล์ src/app.py
try:
    from app import VocabGameApp
except ModuleNotFoundError as e:
    print(f"\n[ แจ้งเตือน Error ] ไม่สามารถโหลดโมดูลได้: {e}")
    print("โปรดตรวจสอบว่ามีไฟล์ src/app.py และแก้ไขการอิมพอร์ตในไฟล์อื่นๆ ครบแล้ว\n")
    sys.exit(1)

# 4. จุดเริ่มต้นการรันโปรแกรม
if __name__ == '__main__':
    VocabGameApp().run()