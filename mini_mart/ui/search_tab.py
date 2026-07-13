"""
Search Tab - Find products by name, code, or category
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem, QFrame, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer
from ui.styles import primary, ghost
from PyQt5.QtGui import QColor, QFont


class SearchTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._do_search)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        title = QLabel("Product Search")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #0f172a;")
        layout.addWidget(title)

        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        sf = QHBoxLayout(search_frame)
        sf.setContentsMargins(20, 16, 20, 16)
        sf.setSpacing(12)

        sf.addWidget(QLabel("Search by:"))
        self.field_combo = QComboBox()
        self.field_combo.addItems(["Product Name", "Product ID / Code", "Category"])
        self.field_combo.setFixedWidth(180)
        sf.addWidget(self.field_combo)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Type to search")
        self.search_edit.textChanged.connect(self._on_text_change)
        sf.addWidget(self.search_edit, 2)

        search_btn = QPushButton("Search")
        search_btn.setStyleSheet(primary())
        search_btn.clicked.connect(self._do_search)
        sf.addWidget(search_btn)

        all_btn = QPushButton("Show All")
        all_btn.setStyleSheet(ghost())
        all_btn.clicked.connect(self._show_all)
        sf.addWidget(all_btn)

        layout.addWidget(search_frame)

        result_frame = QFrame()
        result_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        rf = QVBoxLayout(result_frame)
        rf.setContentsMargins(24, 20, 24, 20)
        rf.setSpacing(12)

        self.result_label = QLabel("Enter a search term above")
        self.result_label.setStyleSheet("color: #64748b; font-size: 13px;")
        rf.addWidget(self.result_label)

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Code", "Name", "Category", "Cost Price", "Sell Price",
            "Qty", "Unit", "Margin %"
        ])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        for col, w in enumerate([45, 90, 0, 120, 90, 90, 60, 60, 80]):
            if w: self.table.setColumnWidth(col, w)
        rf.addWidget(self.table)

        layout.addWidget(result_frame)

    def _on_text_change(self):
        self._search_timer.start(300)

    def _field_key(self) -> str:
        text = self.field_combo.currentText()
        if "ID" in text or "Code" in text:
            return "product_code"
        elif "Category" in text:
            return "category"
        return "name"

    def _do_search(self):
        query = self.search_edit.text().strip()
        if not query:
            self._show_all()
            return
        field = self._field_key()
        results = self.db.search_products(query, field)
        self._display(results, f"Found {len(results)} result(s) for '{query}'")

    def _show_all(self):
        results = self.db.get_all_products()
        self._display(results, f"Showing all {len(results)} products")

    def _display(self, products, label: str):
        self.result_label.setText(label)
        self.table.setRowCount(len(products))

        from models.models import Product as PModel
        for r, p in enumerate(products):
            prod = PModel.from_dict(p)
            margin = prod.get_profit_margin()

            vals = [
                p["product_id"], p["product_code"], p["name"],
                p["category_name"],
                f"${float(p['cost_price']):,.2f}",
                f"${float(p['sell_price']):,.2f}",
                p["quantity"], p["unit"],
                f"{margin:.1f}%"
            ]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(str(v))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if c == 6 and int(p["quantity"]) <= 10:
                    item.setForeground(QColor("#ef4444"))
                    item.setFont(QFont("Arial", 10, QFont.Bold))
                if c == 8:
                    item.setForeground(QColor("#10b981") if margin >= 15 else QColor("#f59e0b") if margin >= 5 else QColor("#ef4444"))
                self.table.setItem(r, c, item)

    def refresh(self):
        if self.search_edit.text().strip():
            self._do_search()
        else:
            self._show_all()
