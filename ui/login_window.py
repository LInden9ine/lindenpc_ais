# ui/login_window.py
import sys
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QMessageBox)
from PyQt6.QtCore import pyqtSignal as Signal, QObject, Qt
import httpx
import asyncio
import traceback


class LoginWindow(QWidget):
    login_successful = Signal(str)  # Сигнал для передачи логина
    attempt_login_signal = Signal(str, str)

    def __init__(self, app):  # Принимаем экземпляр QApplication
        super().__init__()
        self.app = app  # Сохраняем экземпляр QApplication
        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 100, 300, 150)

        self.login_label = QLabel("Логин:")
        self.login_input = QLineEdit()

        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(
            self.start_login_attempt)  # Изменен коннект

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.login_label)
        self.layout.addWidget(self.login_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)

        self.setLayout(self.layout)

        self.attempt_login_signal.connect(self.call_attempt_login)

    def start_login_attempt(self):
        print("start_login_attempt вызван")  # Отладочное сообщение
        login = self.login_input.text()
        password = self.password_input.text()
        self.attempt_login_signal.emit(login, password)

    def call_attempt_login(self, login, password):
        asyncio.create_task(self.attempt_login(login, password))

    async def attempt_login(self, login, password):
        print(f"attempt_login вызван: login={login}, password={password}")
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
                    self.login_successful.emit(self.login_input.text())
                    self.close()
                else:
                    print("Не удалось получить токен")
                    QMessageBox.warning(
                        self, "Ошибка авторизации", "Неверный логин или пароль.")

        except httpx.HTTPStatusError as e:
            print(f"Ошибка HTTP: {e}")
            QMessageBox.warning(self, "Ошибка авторизации",
                                "Неверный логин или пароль.")
        except Exception as e:
            print(f"Ошибка при отправке запроса: {e}")
            QMessageBox.warning(self, "Ошибка авторизации",
                                "Неверный логин или пароль.")
