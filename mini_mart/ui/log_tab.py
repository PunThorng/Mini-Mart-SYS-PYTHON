from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


def _badge(text, bg="#f1f5f9", fg="#64748b"):
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"background: {bg}; color: {fg}; font-size: 10px; font-weight: 700; "
        f"border-radius: 0px; padding: 2px 10px; letter-spacing: 0.3px;"
    )
    lbl.setAlignment(Qt.AlignCenter)
    return lbl


class LogTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background: #f1f4f9;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 32)
        layout.setSpacing(20)

        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: #0f172a;
                border: none;
            }
        """)
        header_frame.setFixedHeight(60)
        hl = QHBoxLayout(header_frame)
        hl.setContentsMargins(26, 0, 26, 0)
        title = QLabel("Activity Log")
        title.setStyleSheet(
            "color: white; font-size: 20px; font-weight: 700; "
            "letter-spacing: -0.3px; background: transparent;"
        )
        hl.addWidget(title)
        hl.addStretch()

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Activity", "Sales", "Stock In"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #e2e8f0;
                padding: 4px 12px;
                font-size: 12px;
                color: #1e293b;
                min-width: 120px;
            }
            QComboBox:focus { border-color: #2563eb; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: white;
                selection-background-color: #eef2ff;
                color: #1e293b;
            }
        """)
        self.filter_combo.currentTextChanged.connect(self.refresh)
        hl.addWidget(self.filter_combo)

        layout.addWidget(header_frame)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Date", "Type", "Description", "Amount"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.horizontalHeader().setFixedHeight(34)
        self.table.setColumnWidth(0, 160)
        self.table.setColumnWidth(1, 90)
        self.table.setColumnWidth(2, 300)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(32)
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                alternate-background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                font-size: 12px;
                color: #334155;
                outline: none;
            }
            QHeaderView::section {
                background: #f1f5f9;
                color: #64748b;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.6px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 4px 12px;
                text-transform: uppercase;
            }
            QTableWidget::item {
                padding: 4px 12px;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:hover {
                background: #eef2ff;
            }
        """)

        layout.addWidget(self.table)

    def refresh(self):
        self.table.setRowCount(0)

        filter_text = self.filter_combo.currentText()
        rows = []

        if filter_text in ("All Activity", "Sales"):
            try:
                sales = self.db.get_recent_sales(200)
                for s in sales:
                    details = self.db.get_sale_details(s["sale_id"])
                    products = ", ".join(d["product_name"] for d in details)
                    rows.append((
                        s["sale_date"],
                        "Sale",
                        f"#{s['sale_id']} - {products} ({s.get('payment_method', '')})",
                        float(s["total_amount"]),
                    ))
            except Exception as e:
                print(f"LogTab: sales error: {e}")

        if filter_text in ("All Activity", "Stock In"):
            try:
                purchases = self.db.get_recent_purchases(200)
                for p in purchases:
                    rows.append((
                        p["purchase_date"],
                        "Stock In",
                        f"{p['product_name']} x{p['quantity']} (supplier: {p.get('supplier', 'N/A')})",
                        float(p["total_cost"]),
                    ))
            except Exception as e:
                print(f"LogTab: stock error: {e}")

        rows.sort(key=lambda r: r[0], reverse=True)

        self.table.setRowCount(len(rows))
        for r, (dt, typ, desc, amount) in enumerate(rows):
            dt_str = dt.strftime("%Y-%m-%d %H:%M") if hasattr(dt, "strftime") else str(dt)
            self._set_cell(r, 0, dt_str, "#64748b")

            if typ == "Sale":
                self.table.setCellWidget(r, 1, _badge("Sale", "#ecfdf5", "#059669"))
            else:
                self.table.setCellWidget(r, 1, _badge("Stock In", "#eff6ff", "#2563eb"))

            self._set_cell(r, 2, desc, "#0f172a", "500")
            self._set_cell(r, 3, f"${amount:,.2f}", "#0f172a", "700")

    def _set_cell(self, row, col, text, color="#334155", weight="400"):
        item = QTableWidgetItem(str(text))
        font = item.font()
        font.setWeight(QFont.Bold if weight == "700" else
                       QFont.DemiBold if weight == "600" else
                       QFont.Medium if weight == "500" else QFont.Normal)
        item.setFont(font)
        item.setForeground(QColor(color))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        self.table.setItem(row, col, item)
