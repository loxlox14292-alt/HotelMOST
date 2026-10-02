from PyQt6.QtWidgets import QComboBox, QDialog, QDoubleSpinBox, QFormLayout, QHBoxLayout, QLineEdit, QMessageBox, QSpinBox, QTabWidget, QVBoxLayout, QWidget

from . import db
from .reporting import BarChart, export_analytics_pdf
from .widgets import button, fill_table, logout_to_login, metric_card, page_header, table


class RoomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление номера")
        self.setMinimumWidth(440)
        form = QFormLayout(self)
        form.setSpacing(14)
        self.number = QLineEdit(placeholderText="например, 405")
        self.category = QComboBox()
        self.category.addItems(["Single", "Double", "Comfort", "Семейный", "Улучшенный двухместный стандарт"])
        self.capacity = QSpinBox(); self.capacity.setRange(1, 10); self.capacity.setValue(2)
        self.price = QDoubleSpinBox(); self.price.setRange(1, 1_000_000); self.price.setDecimals(2); self.price.setSuffix(" руб."); self.price.setValue(3000)
        self.status = QComboBox()
        self.status.addItem("Свободен", "free")
        self.status.addItem("Занят", "occupied")
        self.status.addItem("Уборка", "cleaning")
        self.status.addItem("Ремонт", "repair")
        form.addRow("Номер", self.number)
        form.addRow("Категория", self.category)
        form.addRow("Количество мест", self.capacity)
        form.addRow("Цена за сутки", self.price)
        form.addRow("Статус", self.status)
        actions = QHBoxLayout()
        cancel = button("Отмена", secondary=True); cancel.clicked.connect(self.reject)
        save = button("Добавить номер"); save.clicked.connect(self.accept)
        actions.addStretch(); actions.addWidget(cancel); actions.addWidget(save)
        form.addRow(actions)


class AdminWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.monthly = []
        self.booking_status = []
        self.room_status = []
        self.setWindowTitle("Отель МОСТ — администратор")
        self.resize(1200, 760)
        root = QVBoxLayout(self); root.setContentsMargins(28, 24, 28, 28)
        logout = button("Выйти", secondary=True)
        logout.clicked.connect(lambda: logout_to_login(self))
        root.addWidget(page_header("Панель управления", f"Администратор: {user['full_name']}", logout))
        tabs = QTabWidget(); root.addWidget(tabs)
        tabs.addTab(self.analytics_tab(), "Аналитика")
        tabs.addTab(self.rooms_tab(), "Номерной фонд")
        tabs.addTab(self.users_tab(), "Пользователи")
        tabs.addTab(self.bookings_tab(), "Бронирования")
        self.refresh_all()

    def analytics_tab(self):
        page = QWidget(); layout = QVBoxLayout(page)
        cards = QHBoxLayout()
        card, self.occupancy = metric_card("Загрузка номеров", "0%"); cards.addWidget(card)
        card, self.revenue = metric_card("Выручка за месяц", "0 руб."); cards.addWidget(card)
        card, self.active = metric_card("Активные заезды", "0"); cards.addWidget(card)
        card, self.requests = metric_card("Новые заявки", "0"); cards.addWidget(card)
        layout.addLayout(cards)
        self.chart = BarChart(); layout.addWidget(self.chart)
        actions = QHBoxLayout(); actions.addStretch()
        refresh = button("Обновить", secondary=True); refresh.clicked.connect(self.load_analytics)
        export = button("Скачать PDF-отчёт"); export.clicked.connect(self.export_report)
        actions.addWidget(refresh); actions.addWidget(export); layout.addLayout(actions)
        return page

    def rooms_tab(self):
        page = QWidget(); layout = QVBoxLayout(page)
        self.rooms = table(["ID", "Номер", "Категория", "Мест", "Цена", "Статус"]); layout.addWidget(self.rooms)
        actions = QHBoxLayout()
        add = button("Добавить номер"); add.clicked.connect(self.add_room)
        refresh = button("Обновить", secondary=True); refresh.clicked.connect(self.load_rooms)
        actions.addWidget(add); actions.addWidget(refresh); actions.addStretch(); layout.addLayout(actions)
        return page

    def add_room(self):
        dialog = RoomDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        room_number = dialog.number.text().strip()
        if not room_number:
            QMessageBox.warning(self, "Добавление номера", "Укажите номер комнаты.")
            return
        try:
            db.execute("INSERT INTO rooms(room_number,category,capacity,price,status) VALUES(%s,%s,%s,%s,%s)",
                       (room_number, dialog.category.currentText(), dialog.capacity.value(),
                        dialog.price.value(), dialog.status.currentData()))
            self.load_rooms()
            QMessageBox.information(self, "Номер добавлен", f"Номер {room_number} добавлен в номерной фонд.")
        except Exception as exc:
            message = "Номер с таким обозначением уже существует." if "Duplicate" in str(exc) else str(exc)
            QMessageBox.critical(self, "Не удалось добавить номер", message)

    def users_tab(self):
        page = QWidget(); layout = QVBoxLayout(page)
        self.users = table(["ID", "Логин", "ФИО", "Роль", "Создан"]); layout.addWidget(self.users)
        refresh = button("Обновить", secondary=True); refresh.clicked.connect(self.load_users); layout.addWidget(refresh)
        return page

    def bookings_tab(self):
        page = QWidget(); layout = QVBoxLayout(page)
        self.bookings = table(["ID", "Гость", "Номер", "Заезд", "Выезд", "Статус", "Сумма"]); layout.addWidget(self.bookings)
        refresh = button("Обновить", secondary=True); refresh.clicked.connect(self.load_bookings); layout.addWidget(refresh)
        return page

    def refresh_all(self):
        self.load_analytics(); self.load_rooms(); self.load_users(); self.load_bookings()

    def load_analytics(self):
        try:
            stats = db.fetch_one("""SELECT
              ROUND(100*SUM(status='occupied')/NULLIF(COUNT(*),0),0),
              (SELECT COALESCE(SUM(total_price),0) FROM bookings WHERE status IN ('active','completed') AND DATE_FORMAT(check_in_date,'%Y-%m')=DATE_FORMAT(CURDATE(),'%Y-%m')),
              (SELECT COUNT(*) FROM bookings WHERE status='active'),
              (SELECT COUNT(*) FROM bookings WHERE status='requested') FROM rooms""")
            occupancy, revenue, active, requests = stats or (0,0,0,0)
            self.occupancy.setText(f"{occupancy or 0}%"); self.revenue.setText(f"{float(revenue or 0):,.0f} руб.")
            self.active.setText(str(active)); self.requests.setText(str(requests))
            self.monthly = db.fetch_all("""SELECT DATE_FORMAT(check_in_date,'%m.%Y'),COUNT(*),SUM(total_price)
              FROM bookings WHERE status IN ('active','completed')
              AND check_in_date >= DATE_SUB(CURDATE(),INTERVAL 5 MONTH)
              GROUP BY DATE_FORMAT(check_in_date,'%Y-%m'),DATE_FORMAT(check_in_date,'%m.%Y') ORDER BY MIN(check_in_date)""")
            self.booking_status = db.fetch_all("SELECT status,COUNT(*) FROM bookings GROUP BY status ORDER BY status")
            self.room_status = db.fetch_all("SELECT status,COUNT(*) FROM rooms GROUP BY status ORDER BY status")
            self.chart.set_data([(row[0], row[2]) for row in self.monthly])
        except Exception as exc: QMessageBox.critical(self, "Аналитика", str(exc))

    def load_rooms(self):
        try: fill_table(self.rooms, db.fetch_all("SELECT id_room,room_number,category,capacity,price,status FROM rooms ORDER BY room_number"))
        except Exception as exc: QMessageBox.critical(self, "Номера", str(exc))

    def load_users(self):
        try: fill_table(self.users, db.fetch_all("SELECT id_user,username,full_name,role,created_at FROM users ORDER BY id_user"))
        except Exception as exc: QMessageBox.critical(self, "Пользователи", str(exc))

    def load_bookings(self):
        try: fill_table(self.bookings, db.fetch_all("""SELECT b.id_booking,g.full_name,r.room_number,b.check_in_date,b.check_out_date,b.status,b.total_price
            FROM bookings b JOIN guests g ON g.id_guest=b.guest_id JOIN rooms r ON r.id_room=b.room_id ORDER BY b.id_booking DESC"""))
        except Exception as exc: QMessageBox.critical(self, "Бронирования", str(exc))

    def export_report(self):
        metrics = [("Загрузка", self.occupancy.text()), ("Выручка за месяц", self.revenue.text()),
                   ("Активные заезды", self.active.text()), ("Новые заявки", self.requests.text())]
        try:
            path = export_analytics_pdf(self, metrics, self.monthly, self.booking_status, self.room_status)
            if path:
                QMessageBox.information(self, "Отчёт", f"PDF-отчёт сохранён:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка отчёта", f"Не удалось сформировать PDF:\n{exc}")
