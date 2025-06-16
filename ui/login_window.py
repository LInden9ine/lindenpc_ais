import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import requests
import configparser
import threading


class LoginWindow(tk.Toplevel):
    def __init__(self, parent, login_success_callback):
        super().__init__(parent)
        self.parent = parent
        self.login_success_callback = login_success_callback
        self.title("Авторизация")
        self.geometry("300x200")

        # Инициализация API URL
        self.config = configparser.ConfigParser()
        try:
            self.config.read("config.ini")
            self.api_url = self.config.get("API", "url")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка чтения config.ini: {e}")
            self.api_url = None

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Логин:").pack(pady=5)
        self.login_entry = ttk.Entry(self)
        self.login_entry.pack(pady=5)

        ttk.Label(self, text="Пароль:").pack(pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        ttk.Button(self, text="Войти", command=self.login).pack(pady=10)

    def login(self):
        # Показываем label с сообщением о загрузке
        self.loading_label = ttk.Label(self, text="Авторизация...")
        self.loading_label.pack()

        # Проверка наличия API URL
        if not self.api_url:
            messagebox.showerror(
                "Ошибка", "Не удалось прочитать файл конфигурации.")
            return

        # Проверка доступности сервера
        try:
            response = requests.get(f"{self.api_url}/", timeout=2)
            if response.status_code != 200:
                raise ConnectionError("Сервер не отвечает")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Сервер API недоступен: {str(e)}")
            return

        # Запуск авторизации в отдельном потоке
        threading.Thread(
            target=self._perform_login,  # Исправлено имя метода
            # Исправлена запятая
            args=(self.login_entry.get(), self.password_entry.get()),
            daemon=True
        ).start()

    def _perform_login(self, username, password):
        """Метод для выполнения в фоновом потоке"""
        try:
            response = requests.post(
                f"{self.api_url}/token",
                data={"username": username, "password": password},
                timeout=5
            )
            response.raise_for_status()
            user_data = response.json()

            if 'access_token' in user_data:
                self.parent.after(0, self._handle_success,
                                  user_data['access_token'], user_data)
            else:
                self.parent.after(0, messagebox.showerror,
                                  "Ошибка", "Неверный ответ сервера")

        except requests.exceptions.RequestException as e:
            self.parent.after(0, messagebox.showerror,
                              "Ошибка", f"Ошибка авторизации: {str(e)}")

    def _handle_success(self, token, user_data):
        """Обработка успешной авторизации в основном потоке"""
        self.login_success_callback(token, user_data)
        self.destroy()  # Явно закрываем окно авторизации
