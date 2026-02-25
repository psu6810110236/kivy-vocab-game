from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from systems.hp_system import HPSystem 

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Vocab Game'))
        btn_start = Button(text='Start')
        btn_start.bind(on_press=self.go_to_game) 
        layout.add_widget(btn_start)
        self.add_widget(layout)

    def go_to_game(self, instance):
        self.manager.current = 'game'

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hp_system = HPSystem() 
  

class VocabGameApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    VocabGameApp().run()