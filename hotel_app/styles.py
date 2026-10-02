APP_STYLE = """
QWidget { background: #f4f7fb; color: #172033; font-family: 'Segoe UI'; font-size: 14px; }
QLabel { background: transparent; }
QFrame#sidebar {
  background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #172554,stop:0.55 #312e81,stop:1 #4f46e5);
  border-radius: 24px;
}
QFrame#card, QFrame#metricCard, QFrame#topBar {
  background: #ffffff; border: 1px solid #e5eaf2; border-radius: 18px;
}
QFrame#metricCard { border-left: 5px solid #6366f1; }
QFrame#topBar { padding: 2px; }
QLabel#brand { color: white; font-size: 30px; font-weight: 800; letter-spacing: 3px; }
QLabel#muted { color: #69758a; font-size: 13px; }
QLabel#metric { color: #1e1b4b; font-size: 31px; font-weight: 800; }
QLabel#pageTitle { font-size: 27px; font-weight: 800; color: #18213a; }
QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
  min-height: 25px; background: white; border: 1px solid #d7deea; border-radius: 11px; padding: 9px 12px;
}
QLineEdit:hover, QComboBox:hover, QDateEdit:hover { border-color: #a5b4fc; }
QLineEdit:focus, QComboBox:focus, QDateEdit:focus { border: 2px solid #6366f1; padding: 8px 11px; }
QPushButton { min-height: 24px; background: #4f46e5; color: white; border: none; border-radius: 11px; padding: 10px 19px; font-weight: 700; }
QPushButton:hover { background: #4338ca; }
QPushButton:pressed { background: #3730a3; }
QPushButton[secondary="true"] { background: #eef2ff; color: #3730a3; border: 1px solid #dfe4ff; }
QPushButton[secondary="true"]:hover { background: #e0e7ff; }
QPushButton[danger="true"] { background: #e5484d; }
QPushButton[danger="true"]:hover { background: #cf3940; }
QTableWidget { background: white; alternate-background-color: #f8faff; border: 1px solid #e4e9f1; border-radius: 14px; gridline-color: #edf0f5; selection-background-color: #e0e7ff; selection-color: #1e1b4b; }
QTableWidget::item { padding: 7px; border-bottom: 1px solid #eef1f5; }
QHeaderView::section { background: #eef2ff; color: #3730a3; border: none; border-bottom: 2px solid #dfe4ff; padding: 11px; font-weight: 800; }
QTabWidget::pane { border: 1px solid #e5eaf2; border-radius: 15px; background: #ffffff; top: -1px; }
QTabBar::tab { background: #e9edf5; color: #566176; padding: 11px 20px; margin-right: 5px; border-top-left-radius: 10px; border-top-right-radius: 10px; font-weight: 700; }
QTabBar::tab:hover { background: #e0e7ff; color: #3730a3; }
QTabBar::tab:selected { background: #4f46e5; color: white; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: #c7d0df; border-radius: 5px; min-height: 28px; }
QToolTip { background: #172554; color: white; border: none; padding: 6px; }
"""
