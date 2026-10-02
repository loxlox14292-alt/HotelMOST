from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView


def button(text, secondary=False, danger=False):
    result = QPushButton(text)
    result.setProperty("secondary", secondary)
    result.setProperty("danger", danger)
    return result


def table(headers):
    result = QTableWidget(0, len(headers))
    result.setHorizontalHeaderLabels(headers)
    result.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    result.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    result.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    result.setAlternatingRowColors(True)
    result.setShowGrid(False)
    result.verticalHeader().setDefaultSectionSize(42)
    result.verticalHeader().setVisible(False)
    return result


def fill_table(widget, rows):
    widget.setRowCount(0)
    for row_index, row in enumerate(rows):
        widget.insertRow(row_index)
        for column_index, value in enumerate(row):
            item = QTableWidgetItem("" if value is None else str(value))
            if column_index == 0:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            widget.setItem(row_index, column_index, item)


def metric_card(title, value):
    card = QFrame(objectName="metricCard")
    layout = QVBoxLayout(card)
    caption = QLabel(title, objectName="muted")
    metric = QLabel(str(value), objectName="metric")
    layout.addWidget(caption)
    layout.addWidget(metric)
    return card, metric


def logout_to_login(window):
    from .auth import LoginWindow

    window.login_window = LoginWindow()
    window.login_window.show()
    window.close()


def page_header(title, subtitle="", action=None):
    wrapper = QFrame(objectName="topBar")
    layout = QHBoxLayout(wrapper)
    layout.setContentsMargins(20, 15, 16, 15)
    texts = QVBoxLayout()
    texts.addWidget(QLabel(title, objectName="pageTitle"))
    if subtitle:
        texts.addWidget(QLabel(subtitle, objectName="muted"))
    layout.addLayout(texts)
    layout.addStretch()
    if action is not None:
        layout.addWidget(action)
    return wrapper
