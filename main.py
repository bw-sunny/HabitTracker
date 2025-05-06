from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.lang import Builder
from kivy.properties import StringProperty
import sqlite3
from kivymd.toast import toast
from kivymd.uix.menu import MDDropdownMenu
# Бычий  сизципень мягков


# Загрузка всех KV-файлов
Builder.load_file('C:/Users/Misha/PycharmProjects/HabitTracker/kv/login.kv')
Builder.load_file('C:/Users/Misha/PycharmProjects/HabitTracker/kv/registr.kv')
Builder.load_file('C:/Users/Misha/PycharmProjects/HabitTracker/kv/main.kv')
Builder.load_file('C:/Users/Misha/PycharmProjects/HabitTracker/kv/add_habit.kv')
Builder.load_file('C:/Users/Misha/PycharmProjects/HabitTracker/kv/profile.kv')


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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            icon TEXT,
            description TEXT,
            frequency TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
        self.load_habits()

    def load_habits(self):
        # Очищаем существующие привычки
        habits_container = self.ids.habits_container
        habits_container.clear_widgets()

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            # Предполагаем user_id = 1 для примера
            cursor.execute('SELECT name, icon, description, frequency FROM habits WHERE user_id=1')
            habits = cursor.fetchall()
            conn.close()

            for habit in habits:
                name, icon, description, frequency = habit
                self.add_habit_to_ui(name, icon, description, frequency)
        except Exception as e:
            print(f"Ошибка загрузки привычек: {e}")

    def add_habit_to_ui(self, name, icon, description, frequency):
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel

        card = MDCard(
            size_hint=(None, None),
            size=("300dp", "120dp"),
            pos_hint={"center_x": 0.5},
            padding="10dp",
            spacing="10dp"
        )

        box = MDBoxLayout(orientation='vertical')

        # Первая строка - название и иконка
        top_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="40dp")
        top_box.add_widget(MDLabel(
            text=name,
            theme_text_color="Primary",
            font_style="H6",
            halign="left"
        ))
        top_box.add_widget(MDLabel(
            text=icon,
            theme_text_color="Primary",
            font_style="H6",
            halign="right"
        ))

        # Вторая строка - описание
        desc_label = MDLabel(
            text=description,
            theme_text_color="Secondary",
            font_style="Body1",
            halign="left",
            size_hint_y=None,
            height="40dp"
        )

        # Третья строка - частота
        freq_label = MDLabel(
            text=f"Частота: {frequency}",
            theme_text_color="Hint",
            font_style="Caption",
            halign="left"
        )

        box.add_widget(top_box)
        box.add_widget(desc_label)
        box.add_widget(freq_label)
        card.add_widget(box)

        self.ids.habits_container.add_widget(card)

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
        frequency = self.ids.frequency_btn.text

        if not all([name, description, frequency != "Выберите частоту"]):
            if not name:
                toast("Введите название привычки")
            elif not description:
                toast("Введите описание привычки")
            else:
                toast("Выберите частоту")
            return

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            # Предполагаем, что user_id = 1 для примера
            cursor.execute('''
                INSERT INTO habits (user_id, name, icon, description, frequency)
                VALUES (?, ?, ?, ?, ?)
            ''', (1, name, icon, description, frequency))
            conn.commit()
            conn.close()

            toast("Привычка сохранена!")
            self.manager.current = 'main'
            # Обновляем главный экран
            main_screen = self.manager.get_screen('main')
            main_screen.load_habits()
        except Exception as e:
            print(f"Ошибка сохранения привычки: {e}")
            toast("Ошибка сохранения")

    def show_frequency_menu(self):
        frequency_items = [
            {
                "text": "Каждый день",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Каждый день": self.set_frequency(x),
            },
            {
                "text": "Каждую неделю",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Каждую неделю": self.set_frequency(x),
            },
            {
                "text": "Каждый месяц",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Каждый месяц": self.set_frequency(x),
            },
        ]

        self.frequency_menu = MDDropdownMenu(
            caller=self.ids.frequency_btn,
            items=frequency_items,
            width_mult=4,
        )
        self.frequency_menu.open()

    def set_frequency(self, frequency):
        self.ids.frequency_btn.text = frequency
        self.frequency_menu.dismiss()
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