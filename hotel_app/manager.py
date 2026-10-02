from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QDateEdit, QDialog, QFormLayout, QHBoxLayout, QLineEdit, QMessageBox, QVBoxLayout, QWidget

from . import db
from .widgets import button, fill_table, logout_to_login, page_header, table


class CheckInDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Оформление заезда")
        self.setMinimumWidth(430)
        form = QFormLayout(self)
        self.name, self.passport, self.phone = QLineEdit(), QLineEdit(), QLineEdit()
        self.room = QLineEdit(placeholderText="например, 101")
        self.start, self.end = QDateEdit(QDate.currentDate()), QDateEdit(QDate.currentDate().addDays(1))
        for field in (self.start, self.end):
            field.setCalendarPopup(True)
        for label, field in (("ФИО гостя", self.name), ("Паспорт", self.passport), ("Телефон", self.phone),
                             ("Номер", self.room), ("Заезд", self.start), ("Выезд", self.end)):
            form.addRow(label, field)
        save = button("Оформить")
        save.clicked.connect(self.accept)
        form.addRow(save)


class ManagerWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Отель МОСТ — менеджер")
        self.resize(1120, 700)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        logout = button("Выйти", secondary=True)
        logout.clicked.connect(lambda: logout_to_login(self))
        layout.addWidget(page_header("Рабочее место менеджера", f"Сотрудник: {user['full_name']}", logout))
        self.grid = table(["ID", "Гость", "Телефон", "Номер", "Заезд", "Выезд", "Сумма"])
        layout.addWidget(self.grid)
        actions = QHBoxLayout()
        add, checkout, refresh = button("Новый заезд"), button("Оформить выезд", danger=True), button("Обновить", secondary=True)
        add.clicked.connect(self.add_booking); checkout.clicked.connect(self.checkout); refresh.clicked.connect(self.load)
        for item in (add, checkout, refresh): actions.addWidget(item)
        actions.addStretch(); layout.addLayout(actions)
        self.load()

    def load(self):
        try:
            rows = db.fetch_all("""SELECT b.id_booking,g.full_name,g.phone,r.room_number,b.check_in_date,b.check_out_date,b.total_price
                FROM bookings b JOIN guests g ON g.id_guest=b.guest_id JOIN rooms r ON r.id_room=b.room_id
                WHERE b.status='active' ORDER BY b.check_in_date""")
            fill_table(self.grid, rows)
        except Exception as exc: QMessageBox.critical(self, "Ошибка", str(exc))

    def add_booking(self):
        dialog = CheckInDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted: return
        if dialog.end.date() <= dialog.start.date():
            QMessageBox.warning(self, "Даты", "Дата выезда должна быть позже даты заезда."); return
        try:
            with db.connection() as conn, conn.cursor() as cursor:
                cursor.execute("SELECT id_room,price FROM rooms WHERE room_number=%s AND status='free'", (dialog.room.text().strip(),))
                room = cursor.fetchone()
                if not room: raise ValueError("Номер не найден или не свободен.")
                cursor.execute("INSERT INTO guests(full_name,passport,phone) VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE phone=VALUES(phone)",
                               (dialog.name.text().strip(), dialog.passport.text().strip(), dialog.phone.text().strip()))
                cursor.execute("SELECT id_guest FROM guests WHERE passport=%s", (dialog.passport.text().strip(),)); guest_id = cursor.fetchone()[0]
                nights = dialog.start.date().daysTo(dialog.end.date())
                cursor.execute("INSERT INTO bookings(check_in_date,check_out_date,total_price,guest_id,room_id,user_id,status) VALUES(%s,%s,%s,%s,%s,%s,'active')",
                               (dialog.start.date().toString("yyyy-MM-dd"), dialog.end.date().toString("yyyy-MM-dd"), float(room[1])*nights, guest_id, room[0], self.user['id_user']))
                cursor.execute("UPDATE rooms SET status='occupied' WHERE id_room=%s", (room[0],)); conn.commit()
            self.load()
        except Exception as exc: QMessageBox.critical(self, "Не удалось оформить", str(exc))

    def checkout(self):
        row = self.grid.currentRow()
        if row < 0: QMessageBox.information(self, "Выезд", "Выберите бронирование."); return
        booking_id = self.grid.item(row, 0).text()
        try:
            with db.connection() as conn, conn.cursor() as cursor:
                cursor.execute("SELECT room_id FROM bookings WHERE id_booking=%s", (booking_id,)); room_id = cursor.fetchone()[0]
                cursor.execute("UPDATE bookings SET status='completed',actual_check_out=CURDATE() WHERE id_booking=%s", (booking_id,))
                cursor.execute("UPDATE rooms SET status='cleaning' WHERE id_room=%s", (room_id,)); conn.commit()
            self.load()
        except Exception as exc: QMessageBox.critical(self, "Ошибка", str(exc))
