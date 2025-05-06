from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.lang import Builder

KV = '''
<LoginScreen>:
    MDFloatLayout:
        MDLabel:
            text: "Добро пожаловать в HabitTracker!"
            font_style: "H5"
            halign: "center"
            pos_hint: {"center_x": 0.5, "center_y": 0.8}
            size_hint_x: 0.8

        MDTextField:
            id: email
            hint_text: "e-mail"
            pos_hint: {"center_x": 0.5, "center_y": 0.6}
            size_hint_x: 0.8
            icon_right: "email"
            required: True

        MDTextField:
            id: password
            hint_text: "пароль"
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            size_hint_x: 0.8
            password: True
            icon_right: "key"
            required: True

        MDRaisedButton:
            text: "Войти"
            pos_hint: {"center_x": 0.5, "center_y": 0.35}
            size_hint_x: 0.8
            on_release: root.try_login()

        MDRaisedButton:
            text: "Создать аккаунт"
            pos_hint: {"center_x": 0.5, "center_y": 0.25}
            size_hint_x: 0.8
            md_bg_color: "gray"
            on_release: root.switch_to_register()
'''


class LoginScreen(MDScreen):
    def try_login(self):
        email = self.ids.email.text
        password = self.ids.password.text
        print(f"Попытка входа: email={email}, password={password}")
        # Здесь должна быть логика проверки входа

    def switch_to_register(self):
        print("Переход к регистрации")
        # Здесь должен быть переход на экран регистрации


class HabitTrackerApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        Builder.load_string(KV)
        return LoginScreen()


if __name__ == '__main__':
    HabitTrackerApp().run()