import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import requests
import configparser
import os
import urllib.parse
import json  # Импортируем модуль json


class LoginWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Авторизация")
        self.geometry("300x200")
        self.token = None  # Инициализируем атрибут token

        self.config = configparser.ConfigParser()
        try:
            self.config.read("config.ini")
            self.api_url = self.config.get("API", "url")
        except Exception as e:
            messagebox.showerror(
                "Ошибка", f"Ошибка чтения config.ini: {e}")
            self.api_url = None  # Устанавливаем в None, чтобы предотвратить дальнейшие ошибки
            return  # Прерываем инициализацию

        self.create_widgets()
        print("LoginWindow: Initialized")

    def create_widgets(self):
        self.login_label = ttk.Label(self, text="Логин:")
        self.login_label.pack(pady=5)
        self.login_entry = ttk.Entry(self)
        self.login_entry.pack(pady=5)

        self.password_label = ttk.Label(self, text="Пароль:")
        self.password_label.pack(pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        self.login_button = ttk.Button(self, text="Войти", command=self.login)
        self.login_button.pack(pady=10)

    def login(self):
        print("login: Starting")
        if not self.api_url:  # Проверяем, удалось ли прочитать config.ini
            messagebox.showerror(
                "Ошибка", "Не удалось прочитать файл конфигурации.")
            return

        username = self.login_entry.get()
        password = self.password_entry.get()

        try:
            # Создаем словарь с данными
            data = {"username": username, "password": password}

            # Отправляем POST-запрос с данными в формате application/x-www-form-urlencoded
            response = requests.post(f"{self.api_url}/token", data=data)

            response.raise_for_status()
            data = response.json()
            access_token = data.get("access_token")

            if access_token:
                print("access_token", access_token)
                self.token = access_token  # Устанавливаем токен
                self.destroy()  # Закрываем окно авторизации
            else:
                messagebox.showerror(
                    "Ошибка", "Не удалось получить токен доступа")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка авторизации: {e}")
        print("login: Finished")
