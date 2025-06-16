from ui.tkinter_ui import MainWindow
from ui.login_window import LoginWindow
import tkinter as tk
from api_launcher import start_api


def run_application():
    # Запускаем сервер API
    api_process = start_api()

    # Создаем главное окно
    root = tk.Tk()
    root.withdraw()  # Скрываем корневое окно

    # Функция для запуска главного окна после авторизации
    def on_login_success(token, user_data):
        login_window.destroy()  # Закрываем окно авторизации
        main_window = MainWindow(token, user_data)
        main_window.mainloop()

    # Создаем окно авторизации
    login_window = LoginWindow(root, on_login_success)

    root.mainloop()


if __name__ == "__main__":
    run_application()
