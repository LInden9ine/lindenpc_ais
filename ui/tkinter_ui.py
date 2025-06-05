from ui.components_window import ComponentsWindow
from ui.login_window import LoginWindow
from tkinter import messagebox
from tkinter import ttk
import tkinter as tk
print("Starting...")

try:
    from ui.components_window import ComponentsWindow
except Exception as e:
    print(f"Error importing ComponentsWindow: {e}")
    ComponentsWindow = None  # Чтобы избежать ошибки, если импорт не удался
try:
    from ui.login_window import LoginWindow
except Exception as e:
    print(f"Error importing LoginWindow: {e}")
    LoginWindow = None  # Чтобы избежать ошибки, если импорт не удался


class MainWindow(tk.Tk):
    def __init__(self):
        print("MainWindow: Initializing...")
        tk.Tk.__init__(self)
        self.title("LindenPC - AIS")
        self.geometry("800x600")
        self.token = None
        self.create_menu()
        self.create_widgets()
        self.get_token()
        print("MainWindow: Initialized")

    def get_token(self):
        print("get_token: Starting")
        self.token = self.get_token_from_login()
        print("get_token: Finished")

    def get_token_from_login(self):
        print("get_token_from_login: Starting")
        login_window = LoginWindow(self)
        print("get_token_from_login: Finished")
        return self.token

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
        self.users_button = ttk.Button(
            self, text="Управление пользователями", command=self.open_users_window)
        self.users_button.pack(pady=20)
        self.welcome_label = ttk.Label(
            self, text="Добро пожаловать в AIS LindenPC!")
        self.welcome_label.pack(pady=20)
        print("create_widgets: Finished")

    def open_components_window(self):
        print("open_components_window: Starting")
        ComponentsWindow(self)
        print("open_components_window: Finished")

    def open_users_window(self):
        print("open_users_window: Starting")
        pass
        print("open_users_window: Finished")

    def show_about(self):
        print("show_about: Starting")
        tk.messagebox.showinfo(
            "О программе", "Автоматизированная информационная система для LindenPC")
        print("show_about: Finished")

    def set_token(self, token):
        print("set_token: Starting")
        self.token = token
        print("set_token: Finished")


print("Creating MainWindow...")
main_window = MainWindow()
print("Running mainloop...")
main_window.mainloop()
print("Exited mainloop")
