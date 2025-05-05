from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.lang import Builder
from kivy.properties import StringProperty
import sqlite3
from kivymd.toast import toast
# Бычий  сизципень

# Загрузка всех KV-файлов
Builder.load_file('/Users/bezenov_v/Desktop/HabitTracker/kv/login.kv')
Builder.load_file('/Users/bezenov_v/Desktop/HabitTracker/kv/registr.kv')
Builder.load_file('/Users/bezenov_v/Desktop/HabitTracker/kv/main.kv')
Builder.load_file('/Users/bezenov_v/Desktop/HabitTracker/kv/add_habit.kv')
Builder.load_file('/Users/bezenov_v/Desktop/HabitTracker/kv/profile.kv')


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profile (
            user_id INTEGER PRIMARY KEY,
            email TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()


init_db()


class LoginScreen(MDScreen):
    def try_login(self):
        email = self.ids.email.text
        password = self.ids.password.text

        if email and password:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                print(f"Успешный вход: email={email}")
                toast("Успешный вход!")
                self.manager.current = 'main'
            else:
                print("Неверный email или пароль")
                toast("Неверный email или пароль")
        else:
            print("Заполните все поля")
            toast("Заполните все поля")

    def switch_to_register(self):
        self.manager.current = 'register'


class RegisterScreen(MDScreen):
    def try_register(self):
        email = self.ids.reg_email.text
        password = self.ids.reg_password.text

        if email and password:
            try:
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
                conn.commit()
                conn.close()
                print(f"Успешная регистрация: email={email}")
                toast("Успешная регистрация!")
                self.manager.current = 'login'
            except sqlite3.IntegrityError:
                print("Пользователь с таким email уже существует")
                toast("Пользователь с таким email уже существует")
        else:
            print("Заполните все поля")
            toast("Заполните все поля")

    def switch_to_login(self):
        self.manager.current = 'login'


class MainScreen(MDScreen):
    streak_count = StringProperty("7")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def show_streak(self):
        toast(f"Текущая серия: {self.streak_count} дней подряд!")

    def show_profile(self):
        self.manager.current = 'profile'

    def add_habit(self):
        self.manager.current = 'add_habit'


class ProfileScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_profile()

    def load_profile(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM users LIMIT 1')
        result = cursor.fetchone()
        conn.close()

        if result:
            self.ids.email_field.text = result[0]

    def save_profile(self):
        email = self.ids.email_field.text

        if email:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO profile (user_id, email) VALUES (1, ?)', (email,))
            conn.commit()
            conn.close()
            toast("Профиль сохранен!")
            self.back_to_main()
        else:
            toast("Введите email")

    def back_to_main(self):
        self.manager.current = 'main'


class AddHabitScreen(MDScreen):
    def save_habit(self):
        name = self.ids.habit_name.text
        icon = self.ids.habit_icon.icon
        description = self.ids.habit_description.text

        if name:
            print(f"Сохранение привычки: {name}, {icon}, {description}")
            toast("Привычка сохранена!")
            self.manager.current = 'main'
        else:
            toast("Введите название привычки")

    def cancel(self):
        self.manager.current = 'main'


class HabitTrackerApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        sm = MDScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(AddHabitScreen(name='add_habit'))
        sm.add_widget(ProfileScreen(name='profile'))

        return sm

    def show_achievements(self):
        toast("Достижения")

    def show_faq(self):
        toast("FAQ")


if __name__ == '__main__':
    HabitTrackerApp().run()