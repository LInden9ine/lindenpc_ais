import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox

from ui.components_window import ComponentsWindow
from ui.login_window import LoginWindow
import os

print("Starting...")


class MainWindow(tk.Tk):
    def __init__(self):
        print("MainWindow: Initializing...")
        tk.Tk.__init__(self)
        self.title("LindenPC - AIS")
        self.geometry("800x600")
        self._token = None  # Используем _token для внутреннего хранения
        self.create_widgets()
        self.get_token()
        print("MainWindow: Initialized")

    def get_token(self):
        print("get_token: Starting")
        self.get_token_from_login()
        print("get_token: Finished")

    def get_token_from_login(self):
        print("get_token_from_login: Starting")
        login_window = LoginWindow(self)
        self.wait_window(login_window)  # Ждем закрытия окна логина
        self.token = login_window.token  # Устанавливаем токен
        if self.token:
            self.create_menu()
        print("get_token_from_login: Finished")

    def create_menu(self):
        print("create_menu: Starting")
        self.menu_bar = tk.Menu(self)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Выход", command=self.quit)
        self.menu_bar.add_cascade(label="Файл", menu=self.file_menu)
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(
            label="О программе", command=self.show_about)
        self.menu_bar.add_cascade(label="Помощь", menu=self.help_menu)
        self.config(menu=self.menu_bar)
        print("create_menu: Finished")

    def create_widgets(self):
        print("create_widgets: Starting")
        self.components_button = ttk.Button(
            self, text="Управление комплектующими", command=self.open_components_window)
        self.components_button.pack(pady=20)
        self.welcome_label = ttk.Label(
            self, text="Добро пожаловать в AIS LindenPC!")
        self.welcome_label.pack(pady=20)
        print("create_widgets: Finished")

    def open_components_window(self):
        print("open_components_window: Starting")
        print(f"Token in MainWindow: {self.token}")  # Добавляем эту строку
        if self.token:  # Проверяем, что токен установлен
            ComponentsWindow(self, self.token)  # Передаем токен
        else:
            messagebox.showerror("Ошибка", "Необходимо авторизоваться")
        print("open_components_window: Finished")

    def show_about(self):
        print("show_about: Starting")
        tk.messagebox.showinfo(
            "О программе", "Автоматизированная информационная система для LindenPC")
        print("show_about: Finished")

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        print("set_token: Starting")
        self._token = value
        print("set_token: Finished")


print("Creating MainWindow...")
main_window = MainWindow()
print("Running mainloop...")
main_window.mainloop()
print("Exited mainloop")
