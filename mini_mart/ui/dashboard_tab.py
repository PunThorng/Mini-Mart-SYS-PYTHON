from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QTableWidget, QTableWidgetItem, QScrollArea,
    QHeaderView, QGraphicsDropShadowEffect, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
import datetime


CARD_BORDER = "1px solid #e2e8f0"
CARD_BG = "background: white;"


def _shadow(blur=20, y=2, alpha=16):
    e = QGraphicsDropShadowEffect()
    e.setBlurRadius(blur)
    e.setXOffset(0)
    e.setYOffset(y)
    e.setColor(QColor(0, 0, 0, alpha))
    return e


def _badge(text, bg="#eef2ff", fg="#4f46e5"):
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"background: {bg}; color: {fg}; font-size: 10px; font-weight: 700; "
        f"border-radius: 0px; padding: 2px 10px; letter-spacing: 0.3px;"
    )
    lbl.setAlignment(Qt.AlignCenter)
    return lbl


def _payment_badge(method):
    colors = {
        "Cash":       ("#ecfdf5", "#059669"),
        "Card":       ("#eff6ff", "#2563eb"),
        "Transfer":   ("#faf5ff", "#7c3aed"),
        "Credit":     ("#fef2f2", "#dc2626"),
    }
    bg, fg = colors.get(method, ("#f1f5f9", "#64748b"))
    return _badge(method, bg, fg)


class _StatCard(QFrame):
    def __init__(self, icon: str, title: str, value: str, subtitle: str, color: str):
        super().__init__()
        self.setObjectName("card")
        self.setStyleSheet(
            f"QFrame#card {{ {CARD_BG} border: {CARD_BORDER} }}"
        )
        self.setGraphicsEffect(_shadow(blur=16, y=1, alpha=10))
        self.setFixedHeight(100)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(2)

        top = QHBoxLayout()
        top.setSpacing(8)
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 16px; background: transparent;")
        top.addWidget(icon_lbl)
        t = QLabel(title)
        t.setStyleSheet(
            "color: #94a3b8; font-size: 11px; font-weight: 600; "
            "letter-spacing: 0.3px; background: transparent;"
        )
        top.addWidget(t)
        top.addStretch()
        layout.addLayout(top)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(
            f"color: {color}; font-size: 26px; font-weight: 700; "
            f"background: transparent; letter-spacing: -0.5px;"
        )
        layout.addWidget(self.value_label)

        s = QLabel(subtitle)
        s.setStyleSheet(
            "color: #cbd5e1; font-size: 11px; font-weight: 400; "
            "background: transparent;"
        )
        layout.addWidget(s)

    def set_value(self, value: str):
        self.value_label.setText(value)


class _MiniStat(QFrame):
    def __init__(self, label, value, color="#64748b"):
        super().__init__()
        self.setStyleSheet("background: transparent; border: none;")
        l = QHBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(label)
        lbl.setStyleSheet(
            "color: #94a3b8; font-size: 11px; font-weight: 500; "
            "letter-spacing: 0.3px; background: transparent;"
        )
        l.addWidget(lbl)

        l.addStretch()

        self.val = QLabel(value)
        self.val.setStyleSheet(
            f"color: {color}; font-size: 18px; font-weight: 700; "
            f"background: transparent; letter-spacing: -0.2px;"
        )
        l.addWidget(self.val)


class _TableWidget(QTableWidget):
    def __init__(self, headers, widths):
        super().__init__(0, len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.horizontalHeader().setFixedHeight(34)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QTableWidget.NoSelection)
        self.setShowGrid(False)
        self.verticalHeader().setDefaultSectionSize(32)
        for col, w in enumerate(widths):
            self.setColumnWidth(col, w)
        self.setStyleSheet("""
            QTableWidget {
                background: transparent;
                alternate-background-color: #f8fafc;
                border: none;
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


class _TableCard(QFrame):
    def __init__(self, title, icon_char, table, extra_widget=None):
        super().__init__()
        self.setObjectName("card")
        self.setStyleSheet(
            f"QFrame#card {{ {CARD_BG} border: {CARD_BORDER} }}"
        )
        self.setGraphicsEffect(_shadow(blur=16, y=1, alpha=8))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        tl = QHBoxLayout()
        tl.setContentsMargins(20, 14, 20, 0)
        tl.setSpacing(8)
        icon_lbl = QLabel(icon_char)
        icon_lbl.setStyleSheet("font-size: 14px; background: transparent;")
        tl.addWidget(icon_lbl)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "font-size: 13px; font-weight: 700; color: #0f172a; "
            "background: transparent;"
        )
        tl.addWidget(title_lbl)
        tl.addStretch()
        if extra_widget:
            tl.addWidget(extra_widget)
        layout.addLayout(tl)

        layout.addSpacing(8)
        layout.addWidget(table, 1)


class DashboardTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._build_ui()
        self._start_auto_refresh()
        self.refresh()

    def _start_auto_refresh(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(30000)

    def _build_ui(self):
        self.setStyleSheet("background: #f1f4f9;")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
        )

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(32, 24, 32, 32)
        self.main_layout.setSpacing(20)

        self._build_header()
        self._build_stats()
        self._build_mini_stats()
        self._build_tables()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _build_header(self):
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

        title = QLabel("Dashboard")
        title.setStyleSheet(
            "color: white; font-size: 20px; font-weight: 700; "
            "letter-spacing: -0.3px; background: transparent;"
        )
        hl.addWidget(title)

        hl.addSpacing(16)

        self._ts_label = QLabel()
        self._ts_label.setStyleSheet(
            "color: #64748b; font-size: 12px; font-weight: 400; "
            "background: transparent;"
        )
        hl.addWidget(self._ts_label)

        hl.addStretch()

        self.main_layout.addWidget(header_frame)

    def _build_stats(self):
        cards_row = QHBoxLayout()
        cards_row.setSpacing(18)

        self.card_products  = _StatCard("\U0001f4e6", "Total Products", "\u2014",
                                        "Items in inventory", "#3b82f6")
        self.card_sales     = _StatCard("\U0001f4ca", "Today\u2019s Sales", "\u2014",
                                        "Transactions today", "#10b981")
        self.card_revenue   = _StatCard("\U0001f4b0", "Today\u2019s Revenue", "$0.00",
                                        "Total revenue", "#f59e0b")
        self.card_low_stock = _StatCard("\u26a0\ufe0f", "Low Stock Items", "\u2014",
                                        "Need restocking", "#ef4444")

        for card in [
            self.card_products, self.card_sales,
            self.card_revenue, self.card_low_stock
        ]:
            cards_row.addWidget(card)
        self.main_layout.addLayout(cards_row)

    def _build_mini_stats(self):
        wrapper = QFrame()
        wrapper.setStyleSheet(
            f"background: white; border: {CARD_BORDER};"
        )
        wrapper.setGraphicsEffect(_shadow(blur=14, y=1, alpha=8))
        wrapper.setFixedHeight(48)
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(24, 0, 24, 0)
        row.setSpacing(0)

        self.mini_profit    = _MiniStat("Gross Profit",   "$0.00", "#10b981")
        self.mini_discount  = _MiniStat("Discounts",      "$0.00", "#f59e0b")
        self.mini_cogs      = _MiniStat("COGS",           "$0.00", "#64748b")
        self.mini_expense   = _MiniStat("Expenditure",    "$0.00", "#ef4444")

        for i, m in enumerate([self.mini_profit, self.mini_discount, self.mini_cogs, self.mini_expense]):
            if i > 0:
                sep = QFrame()
                sep.setFixedWidth(1)
                sep.setStyleSheet("background: #e2e8f0; border: none;")
                row.addWidget(sep)
            row.addWidget(m, 1)

        self.main_layout.addWidget(wrapper)

    def _build_tables(self):
        tables_row = QHBoxLayout()
        tables_row.setSpacing(18)

        self.sales_table = _TableWidget(
            ["Date", "Product", "Items", "Total", "Payment"],
            [115, 130, 35, 75, 75]
        )
        self.sales_table.setFixedHeight(300)

        self.sales_search = QLineEdit()
        self.sales_search.setPlaceholderText("Search product...")
        self.sales_search.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 0px;
                padding: 4px 10px;
                font-size: 11px;
                background: white;
                color: #1e293b;
                max-width: 160px;
            }
            QLineEdit:focus { border-color: #2563eb; }
        """)
        self.sales_search.textChanged.connect(self._filter_sales)

        self.sales_card = _TableCard(
            "Recent Sales", "\U0001f4cb", self.sales_table,
            extra_widget=self.sales_search
        )

        self.low_table = _TableWidget(
            ["Product", "Category", "Qty", "Price"],
            [150, 90, 50, 80]
        )
        self.low_table.setFixedHeight(300)
        self.low_card = _TableCard(
            "Low Stock Alerts", "\u26a0\ufe0f", self.low_table,
            extra_widget=self._low_count_badge()
        )

        tables_row.addWidget(self.sales_card, 1)
        tables_row.addWidget(self.low_card, 1)
        self.main_layout.addLayout(tables_row)

    def _low_count_badge(self):
        self._low_count_tag = QLabel(" 0 items ")
        self._low_count_tag.setStyleSheet(
            "background: #fef2f2; color: #dc2626; font-size: 11px; "
            "font-weight: 700; border-radius: 0px; padding: 2px 10px;"
        )
        return self._low_count_tag

    def _render_sales(self, data):
        self.sales_table.setRowCount(len(data))
        for r, d in enumerate(data):
            s = d["sale"]
            dt = s["sale_date"].strftime("%Y-%m-%d %H:%M")
            self._set_cell(self.sales_table, r, 0, dt, "#64748b")
            self._set_cell(self.sales_table, r, 1, d["products"], "#0f172a", "500")
            self._set_cell(self.sales_table, r, 2, str(s["item_count"]))
            self._set_cell(
                self.sales_table, r, 3,
                f"${float(s['total_amount']):,.2f}", "#0f172a", "800"
            )
            self.sales_table.setCellWidget(r, 4, _payment_badge(s["payment_method"]))

    def _filter_sales(self, text):
        if not hasattr(self, "_sales_data"):
            return
        if not text.strip():
            self._render_sales(self._sales_data)
            return
        q = text.strip().lower()
        filtered = [d for d in self._sales_data if q in d["products"].lower()]
        self._render_sales(filtered)

    def refresh(self):
        try:
            now = datetime.datetime.now()
            self._ts_label.setText(
                now.strftime("%A, %b %d, %Y  \u2014  %I:%M %p")
            )

            products = self.db.get_all_products()
            total_products = len(products)
            self.card_products.set_value(str(total_products))

            recent = self.db.get_recent_sales(100)
            today = datetime.date.today()
            today_sales = [s for s in recent if s["sale_date"].date() == today]
            today_count = len(today_sales)
            today_revenue = sum(float(s["total_amount"]) for s in today_sales)

            self.card_sales.set_value(str(today_count))
            self.card_revenue.set_value(f"${today_revenue:,.2f}")

            low_stock = self.db.get_low_stock_products(10)
            low_count = len(low_stock)
            self.card_low_stock.set_value(str(low_count))
            self._low_count_tag.setText(f" {low_count} items ")

            display = recent[:50]
            self._sales_data = []
            for s in display:
                details = self.db.get_sale_details(s["sale_id"])
                products = ", ".join(d["product_name"] for d in details)
                self._sales_data.append({
                    "sale": s,
                    "products": products,
                })
            self._render_sales(self._sales_data)

            self.low_table.setRowCount(len(low_stock))
            for r, p in enumerate(low_stock):
                self._set_cell(self.low_table, r, 0, p["name"], "#0f172a", "600")
                self._set_cell(self.low_table, r, 1, p["category_name"], "#64748b")
                qty = p["quantity"]
                qty_item = QTableWidgetItem(str(qty))
                qty_item.setForeground(QColor("#dc2626"))
                qty_item.setFont(QFont("", 11, QFont.Bold))
                self.low_table.setItem(r, 2, qty_item)
                self._set_cell(
                    self.low_table, r, 3,
                    f"${float(p['sell_price']):,.2f}", "#0f172a"
                )

            report = self.db.get_daily_report()
            self.mini_profit.val.setText(
                f"${report.get('gross_profit', 0):,.2f}"
            )
            self.mini_discount.val.setText(
                f"${report.get('total_discount', 0):,.2f}"
            )
            self.mini_cogs.val.setText(
                f"${report.get('cogs', 0):,.2f}"
            )
            self.mini_expense.val.setText(
                f"${report.get('total_expenditure', 0):,.2f}"
            )

        except Exception as e:
            print(f"Dashboard refresh error: {e}")

    @staticmethod
    def _set_cell(table, row, col, text, color="#334155", weight="400"):
        item = QTableWidgetItem(str(text))
        font = item.font()
        font.setWeight(QFont.Bold if weight == "800" else
                       QFont.DemiBold if weight == "600" else QFont.Normal)
        item.setFont(font)
        item.setForeground(QColor(color))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        table.setItem(row, col, item)
