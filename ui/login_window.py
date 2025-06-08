import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import requests
import configparser
import os
import urllib.parse
import json  # Импортируем модуль json
import threading  # Импортируем модуль threading


class LoginWindow(tk.Toplevel):
    def __init__(self, parent, login_success_callback):  # Add callback
        super().__init__(parent)
        self.parent = parent
        self.title("Авторизация")
        self.geometry("300x200")
        self.token = None  # Инициализируем атрибут token
        self.login_success_callback = login_success_callback  # Save callback

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

        def do_login():  # Функция для выполнения в отдельном потоке
            print("do_login: Starting in thread")
            try:
                try:
                    # Создаем словарь с данными
                    data = {"username": username, "password": password}
                    print("do_login: Data created:", data)
                except Exception as e:
                    print("do_login: Error creating data:", e)
                    self.parent.after(0, messagebox.showerror,
                                      "Ошибка", f"Ошибка при создании данных: {e}")
                    return

                try:
                    # Отправляем POST-запрос с данными в формате application/x-www-form-urlencoded
                    print(
                        f"do_login: Sending request to: {self.api_url}/token")
                    response = requests.post(
                        f"{self.api_url}/token", data=data)
                    print(
                        f"do_login: Response status code: {response.status_code}")
                    response.raise_for_status()
                    print("do_login: Request successful")
                except requests.exceptions.RequestException as e:
                    print(f"do_login: Request error: {e}")
                    self.parent.after(0, messagebox.showerror,
                                      "Ошибка", f"Ошибка авторизации: {e}")
                    return

                try:
                    user_data = response.json()
                    print(f"do_login: User data: {user_data}")
                    access_token = user_data.get("access_token")
                except Exception as e:
                    print(f"do_login: Error parsing JSON: {e}")
                    self.parent.after(0, messagebox.showerror,
                                      "Ошибка", "Ошибка при разборе ответа сервера")
                    return

                if access_token:
                    print("do_login: Access token received")
                    # ВАЖНО: Обновляем UI из основного потока
                    self.parent.after(
                        0, self.login_success_callback, access_token, user_data)
                    # Закрываем окно авторизации
                    self.parent.after(0, self.destroy)
                else:
                    print("do_login: Access token not received")
                    # ВАЖНО: Обновляем UI из основного потока
                    self.parent.after(0, messagebox.showerror,
                                      "Ошибка", "Не удалось получить токен доступа")
            except Exception as e:
                print(f"do_login: An unexpected error occurred: {e}")
                self.parent.after(0, messagebox.showerror,
                                  "Ошибка", f"Непредвиденная ошибка: {e}")
            print("do_login: Finished in thread")

        # Создаем и запускаем поток
        print("login: Creating and starting thread")
        thread = threading.Thread(target=do_login)
        thread.start()
        print("login: Thread started")
