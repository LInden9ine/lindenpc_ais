# main_ui.py
import sys
from PyQt6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)  # Создаем экземпляр QApplication здесь

    login_window = LoginWindow(app)  # Передаем экземпляр приложения
    login_window.show()

    def show_main_window(username):
        print(f"Отображаем главное окно для пользователя: {username}")
        # Передаем экземпляр приложения
        main_window = MainWindow(username, app)
        print("Главное окно создано")
        main_window.show()
        main_window.activateWindow()
        main_window.raise_()
        print("Главное окно отображено")

    login_window.login_successful.connect(show_main_window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
