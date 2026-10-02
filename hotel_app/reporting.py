from datetime import datetime

from PyQt6.QtCore import QMarginsF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QPageLayout, QPageSize, QPainter, QPdfWriter, QPen
from PyQt6.QtWidgets import QFileDialog, QWidget


INK = QColor("#172554")
MUTED = QColor("#64748b")
GRID = QColor("#e2e8f0")
ACCENT = QColor("#4f46e5")
PALETTE = [QColor(color) for color in ("#4f46e5", "#06b6d4", "#f59e0b", "#10b981", "#ec4899")]

BOOKING_LABELS = {
    "requested": "Новая заявка",
    "active": "Активная",
    "completed": "Завершена",
    "cancelled": "Отменена",
}
ROOM_LABELS = {
    "free": "Свободен",
    "occupied": "Занят",
    "cleaning": "Уборка",
    "repair": "Ремонт",
}


class BarChart(QWidget):
    """Compact revenue chart used in the administrator dashboard."""

    def __init__(self):
        super().__init__()
        self.data = []
        self.setMinimumHeight(270)

    def set_data(self, rows):
        self.data = [(str(label), float(value or 0)) for label, value in rows]
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("white"))
        if not self.data:
            painter.setPen(MUTED)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Пока нет данных для диаграммы")
            painter.end()
            return

        margin, gap = 46, 14
        area = self.rect().adjusted(margin, 24, -24, -42)
        maximum = max([value for _, value in self.data] + [1])
        width = max(18, (area.width() - gap * (len(self.data) - 1)) / max(1, len(self.data)))
        painter.setPen(QPen(GRID, 1))
        painter.drawLine(area.bottomLeft(), area.bottomRight())
        for index, (label, value) in enumerate(self.data):
            height = area.height() * value / maximum
            rect = QRectF(area.left() + index * (width + gap), area.bottom() - height, width, height)
            painter.setBrush(ACCENT)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, 5, 5)
            painter.setPen(INK)
            painter.drawText(QRectF(rect.left() - 5, area.bottom() + 7, width + 10, 24),
                             Qt.AlignmentFlag.AlignCenter, label)
            painter.drawText(QRectF(rect.left() - 10, rect.top() - 24, width + 20, 20),
                             Qt.AlignmentFlag.AlignCenter, f"{value:,.0f}")
        painter.end()


def _font(size, bold=False):
    font = QFont("Segoe UI")
    font.setPointSizeF(size)
    font.setBold(bold)
    return font


def _text(painter, rect, value, size=10, color=INK, bold=False,
          alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter):
    painter.setFont(_font(size, bold))
    painter.setPen(color)
    painter.drawText(QRectF(rect), alignment, str(value))


def _draw_header(painter, page_width, title, subtitle):
    painter.fillRect(QRectF(0, 0, page_width, 178), INK)
    _text(painter, QRectF(58, 42, page_width - 116, 48), title, 23, QColor("white"), True)
    _text(painter, QRectF(60, 94, page_width - 120, 32), subtitle, 10, QColor("#c7d2fe"))
    _text(painter, QRectF(60, 132, page_width - 120, 22),
          "Информационная система отеля «МОСТ»", 9, QColor("#a5b4fc"))


def _draw_footer(painter, page_width, page_height, page_number, generated):
    painter.setPen(QPen(GRID, 1))
    painter.drawLine(58, page_height - 55, page_width - 58, page_height - 55)
    _text(painter, QRectF(60, page_height - 45, page_width - 120, 25),
          f"Сформировано {generated}  ·  Страница {page_number} из 2", 8, MUTED)


def _draw_metric_cards(painter, page_width, metrics):
    margin, gap = 60, 18
    card_width = (page_width - 2 * margin - gap) / 2
    card_height = 92
    for index, (label, value) in enumerate(metrics[:4]):
        row, column = divmod(index, 2)
        x = margin + column * (card_width + gap)
        y = 218 + row * (card_height + 14)
        painter.setPen(QPen(GRID, 1))
        painter.setBrush(QColor("#ffffff"))
        painter.drawRoundedRect(QRectF(x, y, card_width, card_height), 12, 12)
        painter.fillRect(QRectF(x, y + 12, 5, card_height - 24), ACCENT)
        _text(painter, QRectF(x + 20, y + 13, card_width - 38, 25), label, 9, MUTED, True)
        _text(painter, QRectF(x + 20, y + 40, card_width - 38, 39), value, 19, INK, True)


def _draw_revenue_chart(painter, page_width, monthly_rows):
    left, right = 64, page_width - 64
    _text(painter, QRectF(left, 440, right - left, 32), "Выручка по месяцам", 15, INK, True)
    _text(painter, QRectF(left, 471, right - left, 22), "Сумма завершённых и активных бронирований", 9, MUTED)

    chart = QRectF(left + 58, 520, right - left - 82, 635)
    rows = monthly_rows[-8:]
    values = [float(row[2] or 0) for row in rows]
    maximum = max(values + [1.0])
    baseline = chart.bottom() - 48
    plot_top = chart.top() + 24
    plot_height = baseline - plot_top

    painter.setFont(_font(8))
    for step in range(5):
        value = maximum * step / 4
        y = baseline - plot_height * step / 4
        painter.setPen(QPen(GRID, 1))
        painter.drawLine(int(chart.left()), int(y), int(chart.right()), int(y))
        painter.setPen(MUTED)
        painter.drawText(QRectF(left, y - 10, 48, 18), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                         f"{value:,.0f}")

    if not rows:
        _text(painter, QRectF(chart), "Нет бронирований за выбранный период", 11, MUTED,
              alignment=Qt.AlignmentFlag.AlignCenter)
        return

    slot_width = chart.width() / len(rows)
    bar_width = min(66, slot_width * 0.56)
    for index, row in enumerate(rows):
        label, count, revenue = row
        value = float(revenue or 0)
        bar_height = plot_height * value / maximum
        center_x = chart.left() + slot_width * (index + 0.5)
        bar = QRectF(center_x - bar_width / 2, baseline - bar_height, bar_width, bar_height)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(PALETTE[0])
        painter.drawRoundedRect(bar, 7, 7)
        _text(painter, QRectF(center_x - slot_width / 2, baseline + 8, slot_width, 25), label, 8, MUTED,
              alignment=Qt.AlignmentFlag.AlignCenter)
        if value:
            _text(painter, QRectF(center_x - slot_width / 2, baseline - bar_height - 26, slot_width, 22),
                  f"{value:,.0f}", 8, INK, True, Qt.AlignmentFlag.AlignCenter)


def _draw_donut(painter, rect, rows, labels):
    normalized = [(labels.get(str(label), str(label)), int(count or 0))
                  for label, count in rows if int(count or 0) > 0]
    total = sum(count for _, count in normalized)
    painter.setPen(Qt.PenStyle.NoPen)
    if total == 0:
        painter.setBrush(QColor("#e2e8f0"))
        painter.drawEllipse(rect)
        painter.setBrush(QColor("white"))
        painter.drawEllipse(rect.adjusted(rect.width() * .28, rect.height() * .28,
                                          -rect.width() * .28, -rect.height() * .28))
        _text(painter, rect, "Нет данных", 9, MUTED, alignment=Qt.AlignmentFlag.AlignCenter)
        return

    start = 0
    for index, (label, count) in enumerate(normalized):
        span = round(count / total * 360 * 16)
        painter.setBrush(PALETTE[index % len(PALETTE)])
        painter.drawPie(rect, start, span)
        start += span
    inner = rect.adjusted(rect.width() * .29, rect.height() * .29,
                          -rect.width() * .29, -rect.height() * .29)
    painter.setBrush(QColor("white"))
    painter.drawEllipse(inner)
    _text(painter, inner, str(total), 17, INK, True, Qt.AlignmentFlag.AlignCenter)


def _draw_chart_card(painter, rect, title, rows, labels):
    painter.setPen(QPen(GRID, 1))
    painter.setBrush(QColor("white"))
    painter.drawRoundedRect(rect, 12, 12)
    _text(painter, QRectF(rect.left() + 18, rect.top() + 12, rect.width() - 36, 30), title, 12, INK, True)
    donut_rect = QRectF(rect.left() + 20, rect.top() + 62, min(215, rect.width() * .48), min(215, rect.width() * .48))
    _draw_donut(painter, donut_rect, rows, labels)

    normalized = [(labels.get(str(label), str(label)), int(count or 0))
                  for label, count in rows if int(count or 0) > 0]
    legend_x = donut_rect.right() + 14
    legend_width = rect.right() - legend_x - 14
    y = rect.top() + 72
    for index, (label, count) in enumerate(normalized):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(PALETTE[index % len(PALETTE)])
        painter.drawRoundedRect(QRectF(legend_x, y + 4, 10, 10), 3, 3)
        percent = (100 * count / sum(item[1] for item in normalized)) if normalized else 0
        _text(painter, QRectF(legend_x + 17, y, legend_width - 17, 20), f"{label}: {count} ({percent:.0f}%)", 8, INK)
        y += 30


def _draw_monthly_table(painter, page_width, monthly_rows):
    x, y, width = 64, 735, page_width - 128
    _text(painter, QRectF(x, y, width, 30), "Детализация по месяцам", 14, INK, True)
    y += 39
    col_month, col_count, col_sum = x, x + width * .53, x + width * .72
    painter.fillRect(QRectF(x, y, width, 30), QColor("#eef2ff"))
    _text(painter, QRectF(col_month + 10, y, width * .48, 30), "Месяц", 8, INK, True)
    _text(painter, QRectF(col_count, y, width * .18, 30), "Бронирования", 8, INK, True, Qt.AlignmentFlag.AlignCenter)
    _text(painter, QRectF(col_sum, y, width * .27, 30), "Выручка", 8, INK, True, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    y += 31
    rows = monthly_rows[-8:]
    if not rows:
        _text(painter, QRectF(x + 10, y, width - 20, 32), "Нет данных за последние шесть месяцев", 9, MUTED)
        return
    for index, (month, count, revenue) in enumerate(rows):
        if index % 2 == 0:
            painter.fillRect(QRectF(x, y, width, 30), QColor("#f8fafc"))
        _text(painter, QRectF(col_month + 10, y, width * .48, 30), month, 8, INK)
        _text(painter, QRectF(col_count, y, width * .18, 30), count, 8, INK, alignment=Qt.AlignmentFlag.AlignCenter)
        _text(painter, QRectF(col_sum, y, width * .27, 30), f"{float(revenue or 0):,.2f} руб.", 8, INK,
              alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        y += 31


def export_analytics_pdf(parent, metrics, monthly_rows, booking_status_rows=(), room_status_rows=()):
    """Export a two-page analytics report with revenue and distribution charts."""
    suggested = f"hotel_report_{datetime.now():%Y%m%d}.pdf"
    path, _ = QFileDialog.getSaveFileName(parent, "Сохранить отчёт", suggested, "PDF (*.pdf)")
    if not path:
        return None
    if not path.lower().endswith(".pdf"):
        path += ".pdf"

    writer = QPdfWriter(path)
    writer.setTitle("Аналитический отчёт отеля МОСТ")
    writer.setCreator("Информационная система отеля МОСТ")
    writer.setResolution(120)
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setPageMargins(QMarginsF(0, 0, 0, 0), QPageLayout.Unit.Millimeter)
    painter = QPainter(writer)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    page_width, page_height = writer.width(), writer.height()
    generated = datetime.now().strftime("%d.%m.%Y %H:%M")

    _draw_header(painter, page_width, "Аналитический отчёт", f"Срез данных на {generated}")
    _draw_metric_cards(painter, page_width, metrics)
    _draw_revenue_chart(painter, page_width, monthly_rows)
    _draw_footer(painter, page_width, page_height, 1, generated)

    writer.newPage()
    _draw_header(painter, page_width, "Структура отеля", "Состав бронирований и состояние номерного фонда")
    margin, gap = 60, 22
    card_width = (page_width - 2 * margin - gap) / 2
    card_height = 390
    _draw_chart_card(painter, QRectF(margin, 220, card_width, card_height),
                     "Бронирования по статусу", booking_status_rows, BOOKING_LABELS)
    _draw_chart_card(painter, QRectF(margin + card_width + gap, 220, card_width, card_height),
                     "Номера по статусу", room_status_rows, ROOM_LABELS)
    _draw_monthly_table(painter, page_width, monthly_rows)
    _draw_footer(painter, page_width, page_height, 2, generated)
    painter.end()
    return path
