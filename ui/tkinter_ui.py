import tkinter as tk
from tkinter import ttk
import requests
import configparser
from tkinter import messagebox
from ui.login_window import LoginWindow
import ui.components_window
from ui.roles_window import RolesWindow
from ui.users_window import UsersWindow
from api_launcher import start_api
import atexit


class MainWindow(tk.Tk):
    def __init__(self, token=None, user_data=None):
        super().__init__()
        self.api_process = start_api()
        atexit.register(self.cleanup)

        self.title("LindenPC AIS")
        self.geometry("800x600")

        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.api_url = self.config.get("API", "url")

        self.token = token
        self.user_data = user_data

        self.menu_bar = tk.Menu(self)
        self.configure(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Файл", menu=self.file_menu)
        self.file_menu.add_command(label="Выход", command=self.quit)

        self.user_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Пользователь", menu=self.user_menu)
        self.user_menu.add_command(
            label="Войти", command=self.open_login_window)

        self.users_menu_item = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(
            label="Пользователи", menu=self.users_menu_item)
        self.users_menu_item.add_command(label="Управление пользователями",
                                         command=self.open_users_window, state="disabled")

        self.components_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(
            label="Комплектующие", menu=self.components_menu)
        self.components_menu.add_command(label="Управление комплектующими",
                                         command=self.open_components_window, state="disabled")

        self.roles_menu_item = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Роли", menu=self.roles_menu_item)
        self.roles_menu_item.add_command(label="Управление ролями",
                                         command=self.open_roles_window, state="disabled")

        if self.token:
            self.enable_menus()
        else:
            self.disable_menus()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Обработчик закрытия главного окна"""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.cleanup()
            self.destroy()

    def open_login_window(self):
        LoginWindow(self, self.login_success)

    def login_success(self, token, user_data):
        self.token = token
        self.user_data = user_data
        print(f"Token received in MainWindow: {self.token}")
        print(
            f"User data received in MainWindow: {self.user_data.get('role_name')}")
        messagebox.showinfo("Успех", "Вы успешно вошли в систему!")
        self.enable_menus()

    def enable_menus(self):
        self.components_menu.entryconfig(
            "Управление комплектующими", state="normal")
        if self.user_data.get("role_name") == "admin":
            self.roles_menu_item.entryconfig(
                "Управление ролями", state="normal")
            self.users_menu_item.entryconfig(
                "Управление пользователями", state="normal")
        else:
            self.roles_menu_item.entryconfig(
                "Управление ролями", state="disabled")
            self.users_menu_item.entryconfig(
                "Управление пользователями", state="disabled")

    def disable_menus(self):
        self.components_menu.entryconfig(
            "Управление комплектующими", state="disabled")
        self.roles_menu_item.entryconfig("Управление ролями", state="disabled")
        self.users_menu_item.entryconfig(
            "Управление пользователями", state="disabled")

    def open_components_window(self):
        ui.components_window.ComponentsWindow(self, self.token, self.user_data)

    def open_roles_window(self):
        RolesWindow(self, self.token)

    def open_users_window(self):
        UsersWindow(self, self.token)

    def quit(self):
        self.destroy()

    def cleanup(self):
        if self.api_process:
            self.api_process.terminate()
