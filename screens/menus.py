from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.animation import Animation
import json
import os

class MainMenuScreen(Screen):
    def on_enter(self, *args):
        app = App.get_running_app()
        app.sound.play_menu_bgm()
        self.update_highscore()

    def update_highscore(self):
        highscore = 0
        try:
            if os.path.exists('highscore.json'):
                with open('highscore.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    highscore = data.get('highscore', 0)
        except Exception as e:
            print(f"Error loading highscore: {e}")
        
        self.ids.highscore_label.text = f'🏆 สูงสุด: {highscore}'

class OptionsScreen(Screen):
    pass
