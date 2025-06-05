# ui/login_window.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
import json


class LoginWindow:
    def __init__(self, master):  # master - это MainWindow
        print("LoginWindow: Initializing")  # Добавлено
        self.master = master
        self.root = tk.Toplevel(master)  # Создаем Toplevel окно
        self.root.title("Авторизация")
        self.root.geometry("300x200")

        self.login_label = ttk.Label(self.root, text="Логин:")
        self.login_label.pack(pady=5)
        self.login_entry = ttk.Entry(self.root)
        self.login_entry.pack(pady=5)

        self.password_label = ttk.Label(self.root, text="Пароль:")
        self.password_label.pack(pady=5)
        self.password_entry = ttk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        self.login_button = ttk.Button(
            self.root, text="Войти", command=self.login)
        self.login_button.pack(pady=10)
        print("LoginWindow: Initialized")  # Добавлено

    def login(self):
        print("login: Starting")  # Добавлено
        login = self.login_entry.get()
        password = self.password_entry.get()

        data = {"username": login, "password": password}

        try:
            response = requests.post("http://127.0.0.1:8000/token", data=data)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data["access_token"]

            self.master.set_token(access_token)
            messagebox.showinfo("Успех", "Авторизация прошла успешно!")
            self.root.destroy()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка авторизации: {e}")
        except (KeyError, TypeError) as e:
            messagebox.showerror(
                "Ошибка", f"Неверный формат ответа от сервера: {e}")
        print("login: Finished")  # Добавлено
