
import sys

from PyQt6.QtWidgets import QApplication

from hotel_app.auth import LoginWindow
from hotel_app.styles import APP_STYLE


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Отель МОСТ")
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
