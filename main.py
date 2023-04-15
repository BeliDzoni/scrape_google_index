from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.clock import Clock
from functools import partial
from scrape_driver import Scrape


class ScreenManagement(ScreenManager):
    def __init__(self, **kwargs):
        super(ScreenManagement, self).__init__(**kwargs)


class RegisterWindow(Screen):
    def __init__(self, **kwargs):
        super(RegisterWindow, self).__init__(**kwargs)
        self.add_widget(Label(text='Site to be searched', size_hint=(.45, .1), pos_hint={'x': .05, 'y': .85}))
        self.site = TextInput(multiline=False, size_hint=(.45, .1), pos_hint={'x': .5, 'y': .85})
        self.add_widget(self.site)

        self.add_widget(Label(text='Keywords', size_hint=(.45, .1), pos_hint={'x': .05, 'y': .65}))
        self.keywords = TextInput(multiline=False, size_hint=(.45, .1), pos_hint={'x': .5, 'y': .65})
        self.add_widget(self.keywords)

        self.add_widget(Label(text='Latitude', size_hint=(.45, .1), pos_hint={'x': .05, 'y': .45}))
        self.latitude = TextInput(multiline=False, size_hint=(.45, .1), pos_hint={'x': .5, 'y': .45}, text='45.267136')
        self.add_widget(self.latitude)

        self.add_widget(Label(text='Longitude', size_hint=(.45, .1), pos_hint={'x': .05, 'y': .25}))
        self.longitude = TextInput(multiline=False, size_hint=(.45, .1), pos_hint={'x': .5, 'y': .25}, text='19.833549')
        self.add_widget(self.longitude)

        self.btn = Button(text='Search', size_hint=(.9, .2), pos_hint={'center_x': .5, 'y': .03})
        self.add_widget(self.btn)
        self.btn.bind(on_press=self.search)

    def search(self, instance):
        self.btn.disabled = True
        self.btn.text = 'In progress...'
        site = self.site.text.strip()
        keywords = [w.strip() for w in self.keywords.text.split(',')]
        latitude = float(self.latitude.text)
        longitude = float(self.longitude.text)
        print(site)
        print(keywords)
        print(latitude)
        print(longitude)
        if site and keywords and keywords != [''] and latitude and longitude:
            scrape = Scrape(site, keywords, latitude=latitude, longitude=longitude)
            scrape.scrape()
        Clock.schedule_once(partial(self.btn_enable, self.btn), 2)

    def btn_enable(self, *args):
        self.btn.text = 'Search'
        self.btn.disabled = False

class LoginWindow(Screen):
    def __init__(self, **kwargs):
        super(LoginWindow, self).__init__(**kwargs)
        self.btn2 = Button(text='Go')
        self.add_widget(self.btn2)
        self.btn2.bind(on_press=self.screen_transition)

    def screen_transition(self, *args):
        self.manager.current = 'register'


class Application(App):
    def build(self):
        sm = ScreenManagement(transition=FadeTransition())
        sm.add_widget(LoginWindow(name='login'))
        sm.add_widget(RegisterWindow(name='register'))
        return sm


if __name__ == "__main__":
    Application().run()
