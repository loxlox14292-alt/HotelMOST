from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QDateEdit, QDialog, QFormLayout, QHBoxLayout, QLineEdit, QMessageBox, QVBoxLayout, QWidget

from . import db
from .widgets import button, fill_table, logout_to_login, page_header, table


class GuestWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Отель МОСТ — кабинет гостя")
        self.resize(1050, 650)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        logout = button("Выйти", secondary=True)
        logout.clicked.connect(lambda: logout_to_login(self))
        layout.addWidget(page_header(f"Здравствуйте, {user['full_name']}", "Выберите номер и оставьте заявку на бронирование", logout))
        filters = QHBoxLayout()
        self.start, self.end = QDateEdit(QDate.currentDate()), QDateEdit(QDate.currentDate().addDays(1))
        for field in (self.start, self.end): field.setCalendarPopup(True)
        search = button("Показать свободные")
        search.clicked.connect(self.load)
        filters.addWidget(self.start); filters.addWidget(self.end); filters.addWidget(search); filters.addStretch()
        layout.addLayout(filters)
        self.grid = table(["ID", "Номер", "Категория", "Мест", "Цена за сутки"])
        layout.addWidget(self.grid)
        reserve = button("Оставить заявку")
        reserve.clicked.connect(self.reserve)
        layout.addWidget(reserve)
        self.load()

    def load(self):
        try:
            rows = db.fetch_all("""SELECT r.id_room,r.room_number,r.category,r.capacity,r.price FROM rooms r
                WHERE r.status IN ('free','cleaning') AND NOT EXISTS (
                  SELECT 1 FROM bookings b WHERE b.room_id=r.id_room AND b.status IN ('requested','active')
                  AND b.check_in_date < %s AND b.check_out_date > %s)
                ORDER BY r.price,r.room_number""",
                (self.end.date().toString("yyyy-MM-dd"), self.start.date().toString("yyyy-MM-dd")))
            fill_table(self.grid, rows)
        except Exception as exc: QMessageBox.critical(self, "Ошибка", str(exc))

    def reserve(self):
        row = self.grid.currentRow()
        if row < 0: QMessageBox.information(self, "Бронирование", "Выберите номер."); return
        if self.end.date() <= self.start.date(): QMessageBox.warning(self, "Даты", "Проверьте даты заезда и выезда."); return
        dialog = QDialog(self); dialog.setWindowTitle("Контактные данны"); form = QFormLayout(dialog)
        passport, phone = QLineEdit(), QLineEdit(); form.addRow("Паспорт", passport); form.addRow("Телефон", phone)
        submit = button("Подтвердить"); submit.clicked.connect(dialog.accept); form.addRow(submit)
        if dialog.exec() != QDialog.DialogCode.Accepted or not passport.text().strip() or not phone.text().strip(): return
        room_id = self.grid.item(row, 0).text(); price = float(self.grid.item(row, 4).text()); nights = self.start.date().daysTo(self.end.date())
        try:
            with db.connection() as conn, conn.cursor() as cursor:
                cursor.execute("INSERT INTO guests(full_name,passport,phone) VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE full_name=VALUES(full_name),phone=VALUES(phone)",
                               (self.user['full_name'], passport.text().strip(), phone.text().strip()))
                cursor.execute("SELECT id_guest FROM guests WHERE passport=%s", (passport.text().strip(),)); guest_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO bookings(check_in_date,check_out_date,total_price,guest_id,room_id,user_id,status) VALUES(%s,%s,%s,%s,%s,%s,'requested')",
                               (self.start.date().toString("yyyy-MM-dd"), self.end.date().toString("yyyy-MM-dd"), price*nights, guest_id, room_id, self.user['id_user']))
                conn.commit()
            QMessageBox.information(self, "Заявка принята", "Менеджер проверит заявку и свяжется с вами.")
            self.load()
        except Exception as exc: QMessageBox.critical(self, "Ошибка", str(exc))
