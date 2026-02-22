from kivy.app import App
from kivy.uix.label import Label

class VocabGameApp(App):
    def build(self):
        return Label(text='Welcome to English Vocab Game!')

if __name__ == '__main__':
    VocabGameApp().run()