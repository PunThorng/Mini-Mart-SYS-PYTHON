"""
Main Application Window
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTabWidget, QStatusBar, QFrame
)
from PyQt5.QtCore import Qt, QTimer

from ui.dashboard_tab import DashboardTab
from ui.products_tab import ProductsTab
from ui.sales_tab import SalesTab
from ui.stock_tab import StockTab
from ui.reports_tab import ReportsTab
from ui.search_tab import SearchTab
from ui.log_tab import LogTab


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Mini Mart Management System")
        self.setMinimumSize(1200, 750)
        self.resize(1350, 820)
        self._build_ui()
        self._start_clock()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = self._make_header()
        root.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #f1f5f9;
            }
            QTabBar::tab {
                background: #1e293b;
                color: #94a3b8;
                padding: 16px 12px;
                min-width: 120px;
                font-size: 13px;
                border: none;
                border-left: 3px solid transparent;
                margin: 0;
                text-align: left;
            }
            QTabBar::tab:selected {
                background: #0f172a;
                color: white;
                font-weight: bold;
                border-left: 3px solid #3b82f6;
            }
            QTabBar::tab:hover:!selected {
                background: #334155;
                color: #e2e8f0;
            }
        """)

        self.dashboard_tab = DashboardTab(self.db)
        self.products_tab = ProductsTab(self.db)
        self.sales_tab = SalesTab(self.db)
        self.stock_tab = StockTab(self.db)
        self.search_tab = SearchTab(self.db)
        self.reports_tab = ReportsTab(self.db)
        self.log_tab = LogTab(self.db)

        self.tabs.addTab(self.dashboard_tab, "  Dashboard")
        self.tabs.addTab(self.sales_tab,     "  New Sale")
        self.tabs.addTab(self.products_tab,  "  Products")
        self.tabs.addTab(self.stock_tab,     "  Stock In")
        self.tabs.addTab(self.search_tab,    "  Search")
        self.tabs.addTab(self.reports_tab,   "  Reports")
        self.tabs.addTab(self.log_tab,       "  Log")

        root.addWidget(self.tabs)

        self.tabs.currentChanged.connect(self._on_tab_change)

        self.products_tab.product_changed.connect(self.dashboard_tab.refresh)
        self.products_tab.product_changed.connect(self.sales_tab.refresh)
        self.products_tab.product_changed.connect(self.stock_tab.refresh)
        self.products_tab.product_changed.connect(self.search_tab.refresh)
        self.products_tab.product_changed.connect(self.log_tab.refresh)

        self.status = QStatusBar()
        self.status.setStyleSheet("""
            QStatusBar {
                background: #1e293b;
                color: #94a3b8;
                font-size: 12px;
                padding: 2px 12px;
            }
            QStatusBar::item { border: none; }
        """)
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")

    def _make_header(self) -> QFrame:
        frame = QFrame()
        frame.setFixedHeight(56)
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f172a, stop:1 #1e293b);
                border-bottom: 1px solid #334155;
            }
        """)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(24, 0, 24, 0)

        title = QLabel("Mini Mart Management System")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: 700;
                letter-spacing: 0.5px;
                background: transparent;
            }
        """)
        layout.addWidget(title)

        subtitle = QLabel("Point of Sale & Inventory")
        subtitle.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 12px;
                font-weight: 400;
                padding-left: 12px;
                background: transparent;
            }
        """)
        layout.addWidget(subtitle)

        layout.addStretch()

        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                font-size: 12px;
                background: transparent;
            }
        """)
        layout.addWidget(self.clock_label)

        return frame

    def _start_clock(self):
        from datetime import datetime
        def update():
            self.clock_label.setText(datetime.now().strftime("%a, %b %d %Y  %H:%M:%S"))
        timer = QTimer(self)
        timer.timeout.connect(update)
        timer.start(1000)
        update()

    def _on_tab_change(self, index: int):
        widget = self.tabs.widget(index)
        if hasattr(widget, "refresh"):
            widget.refresh()
