from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from systems.sound_manager import SoundManager
from systems.hp_system import HPSystem
from kivy.uix.label import Label

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        # สร้างตัวจัดการเสียง
        self.sound = SoundManager()
        self.hp = HPSystem(max_hp=3)

        self.hp_label = Label(text=f"HP: {self.hp.current_hp}", font_size=28)
        self.add_widget(self.hp_label)


        # ปุ่ม Correct
        btn_correct = Button(text="Correct", font_size=32)
        btn_correct.bind(on_press=lambda x: self.sound.play_correct())

        # ปุ่ม Wrong
        btn_wrong = Button(text="Wrong", font_size=32)
        btn_wrong.bind(on_press=self.on_wrong)


        # ปุ่ม Game Over
        btn_gameover = Button(text="Game Over", font_size=32)
        btn_gameover.bind(on_press=lambda x: self.sound.play_gameover())

        self.add_widget(btn_correct)
        self.add_widget(btn_wrong)
        self.add_widget(btn_gameover)
    def on_wrong(self, instance):
        self.hp.take_damage()
        self.hp_label.text = f"HP: {self.hp.current_hp}"
        self.add_widget(self.hp_label)
        self.sound.play_wrong()

        if self.hp.is_dead():
            print("GAME OVER")

class VocabGameApp(App):
    def build(self):
        return MainLayout()


if __name__ == "__main__":
    VocabGameApp().run()