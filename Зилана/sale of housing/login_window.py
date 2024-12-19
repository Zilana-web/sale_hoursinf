from PyQt6.QtCore import QFile, QTextStream
from PyQt6.QtWidgets import QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QWidget, QComboBox, QMessageBox
from main_window import MainWindow
import utils

class LoginWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.setWindowTitle("Вход")
        self.setGeometry(200, 200, 300, 200)
        utils.center_window(self)
        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Логин")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Войти", self)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.register_button = QPushButton("Регистрация", self)
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.apply_stylesheet()

    def apply_stylesheet(self):
        file = QFile("styles/styles.css")
        if not file.exists():
            QMessageBox.warning(self, "Ошибка", "Файл стилей не найден")
            return
        file.open(QFile.OpenModeFlag.ReadOnly)
        stylesheet = QTextStream(file).readAll()
        self.setStyleSheet(stylesheet)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        user = self.db.authenticate_user(username, password)
        if user:
            self.main_window = MainWindow(self.db, user)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if self.db.register_user(username, password):
            QMessageBox.information(self, "Успех", "Регистрация успешна")
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует")
