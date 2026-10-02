import hashlib

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QVBoxLayout, QWidget

from . import db
from .widgets import button


def password_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Регистрация пользователя")
        self.setMinimumWidth(420)
        form = QFormLayout(self)
        self.name = QLineEdit()
        self.login = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("ФИО", self.name)
        form.addRow("Логин", self.login)
        form.addRow("Пароль", self.password)
        form.addRow("Тип аккаунта", QLabel("Гость"))
        save = button("Создать аккаунт")
        save.clicked.connect(self.save)
        form.addRow(save)

    def save(self):
        name, login, password = self.name.text().strip(), self.login.text().strip(), self.password.text()
        role = "guest"
        if not name or not login or len(password) < 6:
            QMessageBox.warning(self, "Проверка", "Заполните поля; пароль должен содержать не менее 6 символов.")
            return
        try:
            if db.fetch_one("SELECT id_user FROM users WHERE username=%s", (login,)):
                QMessageBox.warning(self, "Регистрация", "Такой логин уже занят.")
                return
            db.execute("INSERT INTO users (username, password_hash, role, full_name) VALUES (%s,%s,%s,%s)",
                       (login, password_hash(password), role, name))
            QMessageBox.information(self, "Готово", "Аккаунт гостя создан. Теперь можно войти.")
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать аккаунт:\n{exc}")


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Отель МОСТ — вход")
        self.setFixedSize(900, 560)
        root = QHBoxLayout(self)
        root.setContentsMargins(26, 26, 26, 26)
        hero = QFrame(objectName="sidebar")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(34, 34, 34, 34)
        hero_layout.addWidget(QLabel("МОСТ", objectName="brand"))
        hero_layout.addWidget(QLabel("СИСТЕМА УПРАВЛЕНИЯ ОТЕЛЕМ", styleSheet="color:#a5b4fc;font-weight:700;letter-spacing:2px"))
        hero_layout.addStretch()
        message = QLabel("Управляйте бронированиями,\nномерным фондом и отчётами\nв одном современном пространстве.")
        message.setStyleSheet("color:#eef2ff;font-size:19px;font-weight:600;line-height:1.5")
        hero_layout.addWidget(message)
        hero_layout.addSpacing(24)
        hint = QLabel("●  Три уровня доступа\n●  Аналитика и PDF-отчёты\n●  Работа с гостями и номерами")
        hint.setStyleSheet("color:#c7d2fe;font-size:14px;line-height:1.7")
        hero_layout.addWidget(hint)
        hero_layout.addStretch()
        project_note = QLabel("Учебный проект · Python / PyQt6 / MySQL")
        project_note.setStyleSheet("color:#e0e7ff;font-size:13px;font-weight:600")
        hero_layout.addWidget(project_note)
        root.addWidget(hero, 5)

        panel = QFrame(objectName="card")
        form = QVBoxLayout(panel)
        form.setContentsMargins(45, 50, 45, 50)
        form.addStretch()
        form.addWidget(QLabel("Добро пожаловать", objectName="pageTitle"))
        form.addWidget(QLabel("Войдите в свою учётную запись", objectName="muted"))
        self.login = QLineEdit(placeholderText="Логин")
        self.password = QLineEdit(placeholderText="Пароль")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.returnPressed.connect(self.authenticate)
        form.addSpacing(18)
        form.addWidget(self.login)
        form.addWidget(self.password)
        enter = button("Войти")
        enter.clicked.connect(self.authenticate)
        register = button("Зарегистрироваться", secondary=True)
        register.clicked.connect(lambda: RegisterDialog(self).exec())
        form.addWidget(enter)
        form.addWidget(register)
        form.addStretch()
        root.addWidget(panel, 4)

    def authenticate(self):
        try:
            user = db.fetch_one("SELECT id_user, full_name, role FROM users WHERE username=%s AND password_hash=%s",
                                (self.login.text().strip(), password_hash(self.password.text())), True)
            if not user:
                QMessageBox.warning(self, "Вход", "Неверный логин или пароль.")
                return
            if user["role"] == "admin":
                from .admin import AdminWindow
                self.next_window = AdminWindow(user)
            elif user["role"] == "manager":
                from .manager import ManagerWindow
                self.next_window = ManagerWindow(user)
            else:
                from .guest import GuestWindow
                self.next_window = GuestWindow(user)
            self.next_window.show()
            self.close()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка БД", f"Проверьте MySQL и параметры из README:\n{exc}")
