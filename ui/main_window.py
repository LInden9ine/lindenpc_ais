# ui/main_window.py
import sys
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout)


class MainWindow(QWidget):
    def __init__(self, username, app):  # Принимаем экземпляр QApplication
        super().__init__()
        self.app = app  # Сохраняем экземпляр QApplication
        self.setWindowTitle("Главное окно")
        self.setGeometry(100, 100, 600, 400)

        self.username_label = QLabel(f"Вы вошли как: {username}")
        # Добавляем тестовую надпись
        self.test_label = QLabel("Тестовая надпись")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.test_label)  # Добавляем надпись в layout

        self.setLayout(self.layout)

# Убираем код запуска из этого файла
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     main_window = MainWindow("TestUser")
#     main_window.show()
#     sys.exit(app.exec())
