from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.lang import Builder
from kivy.properties import StringProperty
import sqlite3
from kivymd.toast import toast
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.image import AsyncImage
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.dialog import MDDialog
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
import os

# Бычий  сизципень мягков


# Загрузка всех KV-файлов
Builder.load_file('/Users/bezenov_v/Desktop/new/HabitTracker/kv/login.kv')
Builder.load_file('/Users/bezenov_v/Desktop/new/HabitTracker/kv/registr.kv')
Builder.load_file('/Users/bezenov_v/Desktop/new/HabitTracker/kv/main.kv')
Builder.load_file('/Users/bezenov_v/Desktop/new/HabitTracker/kv/add_habit.kv')
Builder.load_file('/Users/bezenov_v/Desktop/new/HabitTracker/kv/profile.kv')
Builder.load_file('/Users/bezenov_v/Desktop/new/HabitTracker/kv/habit_info.kv')


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
            icon TEXT,  -- Будем хранить путь к файлу
            description TEXT,
            frequency TEXT,
            period TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habit_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(habit_id) REFERENCES habits(id)
        )
    ''')

    conn.commit()
    conn.close()


init_db()

class IconButton(ButtonBehavior, Image):
    pass

class LoginScreen(MDScreen):
    def try_login(self):
        email = self.ids.email.text
        password = self.ids.password.text

        if email and password:
            try:
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute('SELECT id, email FROM users WHERE email=? AND password=?', (email, password))
                user = cursor.fetchone()

                if user:
                    user_id, user_email = user
                    # Сохраняем данные пользователя в приложении
                    app = MDApp.get_running_app()
                    app.current_user = {'id': user_id, 'email': user_email}

                    toast("Успешный вход!")
                    self.manager.current = 'main'
                else:
                    toast("Неверный email или пароль")

            except sqlite3.Error as e:
                print(f"Ошибка базы данных: {e}")
                toast("Ошибка входа")
            finally:
                conn.close()
        else:
            toast("Заполните все поля")

    def switch_to_register(self):
        self.manager.current = 'register'


class RegisterScreen(MDScreen):
    def try_register(self):
        email = self.ids.reg_email.text.strip()
        password = self.ids.reg_password.text
        password_confirm = self.ids.reg_password_confirm.text

        # Сброс предыдущих ошибок
        self.ids.reg_email.error = False
        self.ids.reg_password.error = False
        self.ids.reg_password_confirm.error = False

        # Валидация полей
        if not email:
            self.ids.reg_email.error = True
            self.ids.reg_email.helper_text = "Введите email"
            toast("Введите email")
            return

        if "@" not in email or "." not in email:
            self.ids.reg_email.error = True
            self.ids.reg_email.helper_text = "Некорректный email"
            toast("Некорректный email")
            return

        if not password:
            self.ids.reg_password.error = True
            self.ids.reg_password.helper_text = "Введите пароль"
            toast("Введите пароль")
            return

        if len(password) < 6:
            self.ids.reg_password.error = True
            self.ids.reg_password.helper_text = "Пароль слишком короткий"
            toast("Пароль должен содержать минимум 6 символов")
            return

        if password != password_confirm:
            self.ids.reg_password_confirm.error = True
            self.ids.reg_password_confirm.helper_text = "Пароли не совпадают"
            toast("Пароли не совпадают")
            return

        conn = None
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)',
                           (email, password))
            user_id = cursor.lastrowid

            # Создаем профиль
            cursor.execute('INSERT INTO profile (user_id, email) VALUES (?, ?)',
                           (user_id, email))
            conn.commit()

            # Автоматически входим под новым пользователем
            app = MDApp.get_running_app()
            app.current_user = {'id': user_id, 'email': email}

            toast("Регистрация успешна!")
            self.manager.current = 'main'

        except sqlite3.IntegrityError:
            toast("Пользователь с таким email уже существует")
        except Exception as e:
            print(f"Ошибка регистрации: {e}")
            toast("Ошибка регистрации")
        finally:
            conn.close()
        # Сброс ошибок
        self.ids.reg_email.error = False
        self.ids.reg_password.error = False
        self.ids.reg_password_confirm.error = False

        # Валидация полей
        if not email:
            self.ids.reg_email.error = True
            self.ids.reg_email.helper_text = "Введите email"
            toast("Введите email")
            return

        if "@" not in email or "." not in email:
            self.ids.reg_email.error = True
            self.ids.reg_email.helper_text = "Некорректный email"
            toast("Некорректный email")
            return

        if not password:
            self.ids.reg_password.error = True
            self.ids.reg_password.helper_text = "Введите пароль"
            toast("Введите пароль")
            return

        if len(password) < 6:
            self.ids.reg_password.error = True
            self.ids.reg_password.helper_text = "Пароль слишком короткий"
            toast("Пароль должен содержать минимум 6 символов")
            return

        if password != password_confirm:
            self.ids.reg_password_confirm.error = True
            self.ids.reg_password_confirm.helper_text = "Пароли не совпадают"
            toast("Пароли не совпадают")
            return

        # Если все проверки пройдены, регистрируем пользователя
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
            conn.commit()
            conn.close()

            toast("Регистрация прошла успешно!")
            self.manager.current = 'login'

            # Очищаем поля после успешной регистрации
            self.ids.reg_email.text = ""
            self.ids.reg_password.text = ""
            self.ids.reg_password_confirm.text = ""

        except sqlite3.IntegrityError:
            self.ids.reg_email.error = True
            self.ids.reg_email.helper_text = "Email уже занят"
            toast("Пользователь с таким email уже существует")
        except Exception as e:
            print(f"Ошибка регистрации: {e}")
            toast("Ошибка регистрации")

    def switch_to_login(self):
        self.manager.current = 'login'


class MainScreen(MDScreen):
    streak_count = StringProperty("1")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_habits()

    def load_habits(self):
        habits_container = self.ids.habits_container
        habits_container.clear_widgets()

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, icon, description, frequency, period FROM habits WHERE user_id=1')
            habits = cursor.fetchall()
            conn.close()

            for habit in habits:
                habit_id, name, icon_path, description, frequency, period = habit
                self.add_habit_to_ui(habit_id, name, icon_path, description, frequency, period)
        except Exception as e:
            print(f"Ошибка загрузки привычек: {e}")

    def add_habit_to_ui(self, habit_id, name, icon_path, description, frequency, period):
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.progressbar import MDProgressBar
        from kivy.uix.image import AsyncImage

        card = MDCard(
            size_hint=(None, None),
            size=("300dp", "160dp"),
            pos_hint={"center_x": 0.5},
            padding="10dp",
            spacing="10dp",
            ripple_behavior=True,
            on_release=lambda x, hid=habit_id: self.show_habit_info(hid)
        )

        box = MDBoxLayout(orientation='vertical')

        # Получаем данные о прогрессе
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM habit_completions 
            WHERE habit_id=? 
            AND completion_date >= ?
        ''', (habit_id, self.get_period_start(period)))
        completions = cursor.fetchone()[0]
        max_completions = self.get_max_completions(frequency, period)
        progress = min(completions / max_completions * 100, 100) if max_completions > 0 else 0
        conn.close()

        # Первая строка - название и иконка
        top_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="40dp")

        # Добавляем иконку
        icon = AsyncImage(
            source=icon_path,
            size_hint=(None, None),
            size=("30dp", "30dp"),
            pos_hint={"center_y": 0.5}
        )

        top_box.add_widget(icon)
        top_box.add_widget(MDLabel(
            text=name,
            theme_text_color="Primary",
            font_style="H6",
            halign="left",
            size_hint_x=0.8
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

        # Третья строка - частота и период
        freq_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="20dp")
        freq_box.add_widget(MDLabel(
            text=f"Частота: {frequency}",
            theme_text_color="Hint",
            font_style="Caption",
            halign="left",
            size_hint_x=0.5
        ))
        freq_box.add_widget(MDLabel(
            text=f"Период: {period}",
            theme_text_color="Hint",
            font_style="Caption",
            halign="right",
            size_hint_x=0.5
        ))

        # Прогресс-бар
        progress_bar = MDProgressBar(
            value=progress,
            max=100,
            size_hint_y=None,
            height="10dp"
        )

        # Текст прогресса
        progress_label = MDLabel(
            text=f"Прогресс: {int(progress)}% ({completions}/{max_completions})",
            theme_text_color="Hint",
            font_style="Caption",
            halign="center",
            size_hint_y=None,
            height="20dp"
        )

        box.add_widget(top_box)
        box.add_widget(desc_label)
        box.add_widget(freq_box)
        box.add_widget(progress_bar)
        box.add_widget(progress_label)
        card.add_widget(box)

        self.ids.habits_container.add_widget(card)

    def get_period_start(self, period):
        # Такой же метод как в HabitInfoScreen
        from datetime import datetime, timedelta
        now = datetime.now()

        if period == "1 неделя":
            return now - timedelta(weeks=1)
        elif period == "3 недели":
            return now - timedelta(weeks=3)
        elif period == "1 месяц":
            return now - timedelta(days=30)
        elif period == "3 месяца":
            return now - timedelta(days=90)
        elif period == "1 год":
            return now - timedelta(days=365)
        return now - timedelta(days=1)

    def get_max_completions(self, frequency, period):
        # Такой же метод как в HabitInfoScreen
        if frequency == "Каждый день":
            if period == "1 неделя":
                return 7
            elif period == "3 недели":
                return 21
            elif period == "1 месяц":
                return 30
            elif period == "3 месяца":
                return 90
            elif period == "1 год":
                return 365
        elif frequency == "Каждую неделю":
            if period == "1 неделя":
                return 1
            elif period == "3 недели":
                return 3
            elif period == "1 месяц":
                return 4
            elif period == "3 месяца":
                return 12
            elif period == "1 год":
                return 52
        elif frequency == "Каждый месяц":
            if period == "1 неделя":
                return 0
            elif period == "3 недели":
                return 0
            elif period == "1 месяц":
                return 1
            elif period == "3 месяца":
                return 3
            elif period == "1 год":
                return 12
        return 1

    def show_streak(self):
        toast(f"Текущая серия: {self.streak_count} дней подряд!")

    def show_profile(self):
        self.manager.current = 'profile'

    def add_habit(self):
        self.manager.current = 'add_habit'

    def show_habit_info(self, habit_id):
        habit_screen = self.manager.get_screen('habit_info')
        habit_screen.habit_id = habit_id
        self.manager.current = 'habit_info'


class ProfileScreen(MDScreen):
    def on_pre_enter(self, *args):
        """Загружаем email текущего пользователя при открытии экрана"""
        self.load_current_user_email()

    def load_current_user_email(self):
        app = MDApp.get_running_app()
        if app.current_user:
            self.ids.email_field.text = app.current_user['email']
        else:
            toast("Не удалось загрузить данные пользователя")

    def save_profile(self):
        new_email = self.ids.email_field.text.strip()
        app = MDApp.get_running_app()

        if not app.current_user:
            toast("Ошибка: пользователь не авторизован")
            return

        if not new_email:
            toast("Введите email")
            return

        if "@" not in new_email or "." not in new_email:
            toast("Некорректный email")
            return

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            # Проверяем, не занят ли email другим пользователем
            cursor.execute('SELECT id FROM users WHERE email=? AND id!=?',
                           (new_email, app.current_user['id']))
            if cursor.fetchone():
                toast("Этот email уже используется")
                return

            # Обновляем email в базе данных
            cursor.execute('UPDATE users SET email=? WHERE id=?',
                           (new_email, app.current_user['id']))
            cursor.execute('UPDATE profile SET email=? WHERE user_id=?',
                           (new_email, app.current_user['id']))

            conn.commit()

            # Обновляем email в текущей сессии
            app.current_user['email'] = new_email
            toast("Email успешно изменен")

        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")
            toast("Ошибка сохранения")
        finally:
            conn.close()

    def logout(self):
        app = MDApp.get_running_app()
        app.current_user = None
        self.manager.current = 'login'
        # Очищаем поля ввода на экране логина
        login_screen = self.manager.get_screen('login')
        login_screen.ids.email.text = ""
        login_screen.ids.password.text = ""
        toast("Вы вышли из системы")

    def back_to_main(self):
        self.manager.current = 'main'


class AddHabitScreen(MDScreen):
    edit_mode = False
    editing_habit_id = None
    current_icon = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.icon_picker_dialog = None
  # Будет хранить путь к выбранной иконке
    def select_icon(self, icon_path):
        """Обработчик выбора иконки"""
        self.current_icon = icon_path
        self.ids.habit_icon.source = icon_path
        if hasattr(self, 'icon_dialog'):
            self.icon_dialog.dismiss()
        toast(f"Выбрана иконка: {os.path.basename(icon_path)}")

    def show_icon_picker(self):
        try:
            # Создаем контейнер для иконок
            grid = MDGridLayout(cols=4, spacing="10dp", padding="10dp", adaptive_height=True)

            # Путь к папке с иконками
            icons_dir = os.path.join(os.path.dirname(__file__), "assets", "icons")

            # Проверяем существование папки
            if not os.path.exists(icons_dir):
                os.makedirs(icons_dir)
                toast("Папка с иконками создана. Добавьте туда PNG-файлы")
                return

            # Получаем список файлов
            icon_files = [f for f in os.listdir(icons_dir) if f.lower().endswith('.png')]

            if not icon_files:
                toast("Нет доступных иконок в папке assets/icons")
                return

            # Добавляем иконки в сетку
            for icon_file in sorted(icon_files):
                icon_path = os.path.join(icons_dir, icon_file)
                btn = IconButton(
                    source=icon_path,
                    size_hint=(None, None),
                    size=("64dp", "64dp"),
                    allow_stretch=True
                )
                # Исправленный вызов - передаем только path
                btn.bind(on_release=lambda btn_instance, path=icon_path: self.select_icon(path))
                grid.add_widget(btn)

            # Создаем диалог
            self.icon_dialog = MDDialog(
                title="[b]Выберите иконку[/b]",
                type="custom",
                content_cls=grid,
                size_hint=(0.9, 0.8),
                buttons=[
                    MDFlatButton(
                        text="ОТМЕНА",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=lambda x: self.icon_dialog.dismiss()
                    )
                ]
            )
            self.icon_dialog.open()

        except Exception as e:
            print(f"Ошибка при открытии выбора иконок: {e}")
            toast("Ошибка загрузки иконок")

    def save_habit(self):
        # Проверяем обязательные поля
        if not self.ids.habit_name.text:
            toast("Введите название привычки")
            return

        if not self.current_icon:
            toast("Выберите иконку для привычки")
            return

        # Получаем данные из полей формы
        name = self.ids.habit_name.text
        description = self.ids.habit_description.text
        frequency = self.ids.frequency_btn.text
        period = self.ids.period_btn.text

        # Проверяем, что частота и период выбраны
        if frequency == "Выберите частоту":
            toast("Выберите частоту выполнения")
            return

        if period == "Выберите период":
            toast("Выберите период выполнения")
            return

        # Получаем относительный путь к иконке
        icons_dir = os.path.join("assets", "icons")
        icon_name = os.path.basename(self.current_icon)
        icon_path = os.path.join(icons_dir, icon_name)

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            if self.edit_mode:
                # Редактирование существующей привычки
                cursor.execute('''
                    UPDATE habits 
                    SET name=?, icon=?, description=?, frequency=?, period=?
                    WHERE id=?
                ''', (name, icon_path, description, frequency, period, self.editing_habit_id))
            else:
                # Создание новой привычки
                cursor.execute('''
                    INSERT INTO habits (user_id, name, icon, description, frequency, period)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (1, name, icon_path, description, frequency, period))

            conn.commit()
            conn.close()

            # Показываем уведомление об успехе
            toast("Привычка сохранена!")

            # Возвращаемся на главный экран
            self.manager.current = 'main'

            # Обновляем список привычек
            self.manager.get_screen('main').load_habits()

            # Сбрасываем режим редактирования
            self.edit_mode = False
            self.editing_habit_id = None

            # Очищаем форму (если не в режиме редактирования)
            if not self.edit_mode:
                self.ids.habit_name.text = ""
                self.current_icon = ""
                self.ids.habit_icon.source = "assets/icons/default.png"
                self.ids.habit_description.text = ""
                self.ids.frequency_btn.text = "Выберите частоту"
                self.ids.period_btn.text = "Выберите период"

        except sqlite3.Error as e:
            print(f"Ошибка базы данных при сохранении привычки: {e}")
            toast("Ошибка сохранения в базе данных")

        except Exception as e:
            print(f"Неожиданная ошибка при сохранении привычки: {e}")
            toast("Ошибка сохранения привычки")

    def on_pre_leave(self):
        # Очищаем поля при выходе с экрана
        if not self.edit_mode:
            self.ids.habit_name.text = ""
            self.ids.habit_icon.icon = "plus"
            self.ids.habit_description.text = ""
            self.ids.frequency_btn.text = "Выберите частоту"
        self.edit_mode = False
        self.editing_habit_id = None

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

    def show_period_menu(self):
        period_items = [
            {
                "text": "1 неделя",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="1 неделя": self.set_period(x),
            },
            {
                "text": "3 недели",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="3 недели": self.set_period(x),
            },
            {
                "text": "1 месяц",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="1 месяц": self.set_period(x),
            },
            {
                "text": "3 месяца",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="3 месяца": self.set_period(x),
            },
            {
                "text": "1 год",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="1 год": self.set_period(x),
            },
        ]

        self.period_menu = MDDropdownMenu(
            caller=self.ids.period_btn,
            items=period_items,
            width_mult=4,
        )
        self.period_menu.open()

    def set_period(self, period):
        self.ids.period_btn.text = period
        self.period_menu.dismiss()

    def set_frequency(self, frequency):
        self.ids.frequency_btn.text = frequency
        self.frequency_menu.dismiss()
    def cancel(self):
        self.manager.current = 'main'


class HabitInfoScreen(MDScreen):
    habit_id = None

    def on_pre_enter(self):
        if self.habit_id:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT name, icon, description, frequency, period FROM habits WHERE id=?', (self.habit_id,))
            habit = cursor.fetchone()
            conn.close()

            if not habit:
                toast("Привычка не найдена")
                self.manager.current = 'main'
                return

            if habit:
                name, icon, description, frequency, period = habit
                self.ids.habit_name.text = name
                self.ids.habit_icon.icon = icon if icon else "emoticon-happy-outline"
                self.ids.habit_description.text = description
                self.ids.habit_frequency.text = f"Частота: {frequency}"
                self.ids.habit_period.text = f"Период: {period}"

            self.update_progress()

    def update_progress(self):
        if not self.habit_id:
            return

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Получаем данные о привычке
        cursor.execute('SELECT frequency, period FROM habits WHERE id=?', (self.habit_id,))
        habit_data = cursor.fetchone()

        if habit_data:
            frequency, period = habit_data
            # Получаем все отметки за текущий период
            cursor.execute('''
                SELECT COUNT(*) FROM habit_completions 
                WHERE habit_id=? 
                AND completion_date >= ?
            ''', (self.habit_id, self.get_period_start(period)))

            completions = cursor.fetchone()[0]
            max_completions = self.get_max_completions(frequency, period)
            progress = min(completions / max_completions * 100, 100)

            # Обновляем прогресс
            self.ids.progress_label.text = f"Прогресс: {int(progress)}%"
            self.ids.progress_bar.value = progress

            # Активируем/деактивируем кнопку
            can_complete = self.can_complete_today()
            self.ids.complete_btn.disabled = not can_complete
            self.ids.complete_btn.text = "Выполнено" if not can_complete else "Отметить выполнение"

        conn.close()

    def get_period_start(self, period):
        from datetime import datetime, timedelta
        now = datetime.now()

        if period == "1 неделя":
            return now - timedelta(weeks=1)
        elif period == "3 недели":
            return now - timedelta(weeks=3)
        elif period == "1 месяц":
            return now - timedelta(days=30)
        elif period == "3 месяца":
            return now - timedelta(days=90)
        elif period == "1 год":
            return now - timedelta(days=365)
        return now - timedelta(days=1)  # По умолчанию

    def get_max_completions(self, frequency, period):
        if frequency == "Каждый день":
            if period == "1 неделя":
                return 7
            elif period == "3 недели":
                return 21
            elif period == "1 месяц":
                return 30
            elif period == "3 месяца":
                return 90
            elif period == "1 год":
                return 365
        elif frequency == "Каждую неделю":
            if period == "1 неделя":
                return 1
            elif period == "3 недели":
                return 3
            elif period == "1 месяц":
                return 4
            elif period == "3 месяца":
                return 12
            elif period == "1 год":
                return 52
        elif frequency == "Каждый месяц":
            if period == "1 неделя":
                return 0
            elif period == "3 недели":
                return 0
            elif period == "1 месяц":
                return 1
            elif period == "3 месяца":
                return 3
            elif period == "1 год":
                return 12
        return 1

    def can_complete_today(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM habit_completions 
            WHERE habit_id=? 
            AND date(completion_date) = date('now')
        ''', (self.habit_id,))

        count = cursor.fetchone()[0]
        conn.close()
        return count == 0

    def mark_completed(self):
        # Проверяем, что привычка еще существует
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM habits WHERE id=?', (self.habit_id,))
        if not cursor.fetchone():
            toast("Привычка была удалена")
            conn.close()
            self.manager.current = 'main'
            return

        if not self.can_complete_today():
            toast("Вы уже отметили выполнение сегодня")
            return

        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO habit_completions (habit_id) VALUES (?)', (self.habit_id,))
            conn.commit()
            conn.close()

            toast("Привычка отмечена как выполненная!")
            self.update_progress()

            # Обновляем главный экран
            main_screen = self.manager.get_screen('main')
            main_screen.load_habits()
        except Exception as e:
            print(f"Ошибка отметки выполнения: {e}")
            toast("Ошибка отметки выполнения")

    def back_to_main(self):
        self.manager.current = 'main'

    def edit_habit(self):
        # Реализуем редактирование привычки
        try:
            # Получаем текущие данные привычки
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT name, icon, description, frequency FROM habits WHERE id=?', (self.habit_id,))
            habit = cursor.fetchone()
            conn.close()

            if habit:
                # Переходим на экран добавления привычки в режиме редактирования
                add_screen = self.manager.get_screen('add_habit')
                add_screen.ids.habit_name.text = habit[0]  # name
                add_screen.ids.habit_icon.icon = habit[1] if habit[1] else "plus"  # icon
                add_screen.ids.habit_description.text = habit[2]  # description
                add_screen.ids.frequency_btn.text = habit[3]  # frequency
                add_screen.edit_mode = True
                add_screen.editing_habit_id = self.habit_id
                self.manager.current = 'add_habit'
        except Exception as e:
            print(f"Ошибка при редактировании привычки: {e}")
            toast("Ошибка при редактировании")

    def show_delete_dialog(self):
        from kivymd.uix.dialog import MDDialog

        self.delete_dialog = MDDialog(
            title="Удаление привычки",
            text=f"Вы уверены, что хотите удалить привычку '{self.ids.habit_name.text}'?",
            buttons=[
                MDFlatButton(
                    text="Отмена",
                    on_release=lambda *args: self.delete_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Удалить",
                    md_bg_color=self.theme_cls.error_color,
                    on_release=lambda *args: self.delete_habit()
                ),
            ],
        )
        self.delete_dialog.open()

    def delete_habit(self):
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            # Удаляем привычку из таблицы habits
            cursor.execute('DELETE FROM habits WHERE id=?', (self.habit_id,))

            # Удаляем связанные отметки о выполнении
            cursor.execute('DELETE FROM habit_completions WHERE habit_id=?', (self.habit_id,))

            conn.commit()
            conn.close()

            toast("Привычка удалена")
            if hasattr(self, 'delete_dialog'):
                self.delete_dialog.dismiss()

            # Возвращаемся на главный экран
            self.manager.current = 'main'

            # Обновляем список привычек на главном экране
            main_screen = self.manager.get_screen('main')
            main_screen.load_habits()

        except Exception as e:
            print(f"Ошибка удаления привычки: {e}")
            toast("Ошибка при удалении привычки")


class HabitTrackerApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None  # Будет хранить {'id': X, 'email': 'user@example.com'}
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        sm = MDScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(AddHabitScreen(name='add_habit'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(HabitInfoScreen(name='habit_info'))

        return sm

    def show_achievements(self):
        toast("Достижения")

    def show_faq(self):
        toast("FAQ")


class IconPickerDialog(MDDialog):
    def __init__(self, callback, **kwargs):
        self.callback = callback
        super().__init__(
            title="Выберите иконку",
            type="custom",
            content_cls=self.create_content(),
            buttons=[
                MDFlatButton(
                    text="Отмена",
                    on_release=lambda x: self.dismiss()
                )
            ],
            **kwargs
        )

    def create_content(self):
        layout = GridLayout(cols=4, spacing=10, padding=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        icons_dir = os.path.join(os.path.dirname(__file__), "assets", "icons")

        for icon_file in sorted(os.listdir(icons_dir)):
            if icon_file.endswith(".png"):
                icon_path = os.path.join(icons_dir, icon_file)
                btn = IconButton(
                    source=icon_path,
                    size_hint=(None, None),
                    size=(64, 64),
                    on_release=lambda x, path=icon_path: self.icon_selected(path)
                )
                layout.add_widget(btn)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(layout)
        return scroll

    def icon_selected(self, icon_path):
        self.callback(icon_path)
        self.dismiss()


if __name__ == '__main__':
    HabitTrackerApp().run()
