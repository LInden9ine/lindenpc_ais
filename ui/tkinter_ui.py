import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import httpx
import asyncio
import json
import traceback


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Авторизация")
        self.geometry("300x150")

        self.login_label = ttk.Label(self, text="Логин:")
        self.login_label.pack(pady=2)
        self.login_input = ttk.Entry(self)
        self.login_input.pack(pady=2)

        self.password_label = ttk.Label(self, text="Пароль:")
        self.password_label.pack(pady=2)
        self.password_input = ttk.Entry(self, show="*")
        self.password_input.pack(pady=2)

        self.login_button = ttk.Button(
            self, text="Войти", command=self.start_login_attempt)
        self.login_button.pack(pady=10)

    def start_login_attempt(self):
        login = self.login_input.get()
        password = self.password_input.get()
        asyncio.run(self.attempt_login(login, password))

    async def attempt_login(self, login, password):
        try:
            url = "http://127.0.0.1:8000/token"
            data = {"username": login, "password": password}
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=data, headers=headers)
                response.raise_for_status()
                print(f"Response status code: {response.status_code}")
                print(f"Response content: {response.content}")
                token_data = response.json()
                if token_data and "access_token" in token_data:
                    print(f"Токен получен: {token_data}")
                    self.show_main_window(login)
                    self.destroy()  # Закрываем окно входа
                else:
                    print("Не удалось получить токен")
                    messagebox.showerror(
                        "Ошибка авторизации", "Неверный логин или пароль.")
        except httpx.HTTPStatusError as e:
            print(f"Ошибка HTTP: {e}")
            messagebox.showerror("Ошибка авторизации",
                                 f"Неверный логин или пароль: {e}")
        except Exception as e:
            print(f"Ошибка при отправке запроса: {e}")
            messagebox.showerror("Ошибка авторизации",
                                 f"Произошла ошибка: {e}")

    def show_main_window(self, username):
        main_window = MainWindow(username)
        main_window.mainloop()  # Запускаем главный цикл главного окна


class MainWindow(tk.Tk):
    def __init__(self, username):
        super().__init__()

        self.title(f"Главное окно - {username}")
        self.geometry("400x300")

        self.label = ttk.Label(self, text=f"Привет, {username}!")
        self.label.pack(pady=20)


if __name__ == "__main__":
    login_window = LoginWindow()
    login_window.mainloop()
