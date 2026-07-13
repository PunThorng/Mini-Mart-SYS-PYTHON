"""
Reports Tab - Weekly and Monthly financial reports
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QFrame, QHeaderView,
    QScrollArea, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter

try:
    from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis  # type: ignore[import]
except ImportError:
    QChart = QChartView = QBarSeries = QBarSet = QBarCategoryAxis = QValueAxis = None

from models.models import DailyReport, WeeklyReport, MonthlyReport, SemiAnnualReport, AnnualReport, IncomeReport, ExpenseReport
from ui.styles import ghost, success, primary, danger
from datetime import datetime


class ReportsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        title = QLabel("Financial Reports")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #0f172a;")
        layout.addWidget(title)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        self.income_btn  = QPushButton("Income Report")
        self.expense_btn = QPushButton("Expense Report")
        self.daily_btn   = QPushButton("Daily Report")
        self.weekly_btn  = QPushButton("Weekly Report")
        self.monthly_btn = QPushButton("Monthly Report")
        self.semiannual_btn = QPushButton("6-Month Report")
        self.annual_btn = QPushButton("12-Month Report")
        self.income_btn.clicked.connect(self._show_income)
        self.expense_btn.clicked.connect(self._show_expense)
        self.daily_btn.clicked.connect(self._show_daily)
        self.weekly_btn.clicked.connect(self._show_weekly)
        self.monthly_btn.clicked.connect(self._show_monthly)
        self.semiannual_btn.clicked.connect(self._show_semiannual)
        self.annual_btn.clicked.connect(self._show_annual)
        self.income_btn.setStyleSheet(success())
        self.expense_btn.setStyleSheet(danger())
        self.daily_btn.setStyleSheet(ghost())
        self.weekly_btn.setStyleSheet(ghost())
        self.monthly_btn.setStyleSheet(ghost())
        self.semiannual_btn.setStyleSheet(ghost())
        self.annual_btn.setStyleSheet(ghost())
        btn_row.addWidget(self.income_btn)
        btn_row.addWidget(self.expense_btn)
        btn_row.addWidget(self.daily_btn)
        btn_row.addWidget(self.weekly_btn)
        btn_row.addWidget(self.monthly_btn)
        btn_row.addWidget(self.semiannual_btn)
        btn_row.addWidget(self.annual_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.report_container = QWidget()
        self.report_layout = QVBoxLayout(self.report_container)
        self.report_layout.setContentsMargins(0, 0, 0, 0)
        self.report_layout.setSpacing(20)
        scroll.setWidget(self.report_container)
        layout.addWidget(scroll)

        self._show_weekly()

    def _clear_report(self):
        while self.report_layout.count():
            child = self.report_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _show_income(self):
        r = IncomeReport(self.db)
        self._render_income_report(r.get_title(), r.generate())

    def _show_expense(self):
        r = ExpenseReport(self.db)
        self._render_expense_report(r.get_title(), r.generate())

    def _show_daily(self):
        r = DailyReport(self.db)
        self._render_report(r.get_title(), r.generate())

    def _show_weekly(self):
        r = WeeklyReport(self.db)
        self._render_report(r.get_title(), r.generate())

    def _show_monthly(self):
        r = MonthlyReport(self.db)
        self._render_report(r.get_title(), r.generate())

    def _show_semiannual(self):
        r = SemiAnnualReport(self.db)
        self._render_report(r.get_title(), r.generate())

    def _show_annual(self):
        r = AnnualReport(self.db)
        self._render_report(r.get_title(), r.generate())

    def _render_report(self, title: str, data: dict):
        self._clear_report()

        hdr = QLabel(title)
        hdr.setStyleSheet("""
            font-size: 17px;
            font-weight: 700;
            color: #0f172a;
            background: white;
            border-radius: 0px;
            border: 1px solid #e2e8f0;
            padding: 16px 20px;
        """)
        self.report_layout.addWidget(hdr)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)

        def kpi(label, val, color):
            f = QFrame()
            f.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border-radius: 0px;
                    border: 1px solid #e2e8f0;
                    border-left: 4px solid {color};
                }}
            """)
            fl = QVBoxLayout(f)
            fl.setContentsMargins(16, 14, 16, 14)
            fl.setSpacing(4)
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 0.3px;")
            fl.addWidget(lbl)
            v = QLabel(val)
            v.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 700;")
            fl.addWidget(v)
            return f

        cards_row.addWidget(kpi("Total Income",    f"${data['total_income']:,.2f}",    "#3b82f6"))
        cards_row.addWidget(kpi("Gross Profit",    f"${data['gross_profit']:,.2f}",    "#10b981"))
        cards_row.addWidget(kpi("Expenditure",     f"${data['total_expenditure']:,.2f}", "#f59e0b"))
        cards_row.addWidget(kpi("Net Profit",      f"${data['net_profit']:,.2f}",       "#8b5cf6" if data['net_profit'] >= 0 else "#ef4444"))
        cards_row.addWidget(kpi("Transactions",    str(data['total_transactions']),      "#64748b"))
        cards_row.addWidget(kpi("Total Discount",  f"${data['total_discount']:,.2f}",   "#94a3b8"))

        card_widget = QWidget()
        card_widget.setLayout(cards_row)
        self.report_layout.addWidget(card_widget)

        cols = QHBoxLayout()
        cols.setSpacing(16)

        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        chart_frame.setMinimumHeight(280)
        clf = QVBoxLayout(chart_frame)
        clf.setContentsMargins(20, 18, 20, 18)
        clf.setSpacing(12)

        chart_lbl = QLabel("Daily Income Breakdown")
        chart_lbl.setStyleSheet("font-weight: 700; color: #0f172a; font-size: 14px;")
        clf.addWidget(chart_lbl)

        daily = data.get("daily_breakdown", [])
        if daily:
            chart_view = self._build_bar_chart(daily)
            if chart_view is not None:
                clf.addWidget(chart_view)
            else:
                clf.addWidget(self._build_daily_table(daily))
        else:
            no_data = QLabel("No data for this period.")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet("color: #94a3b8; font-size: 14px; padding: 40px;")
            clf.addWidget(no_data)

        cols.addWidget(chart_frame, 3)

        top_frame = QFrame()
        top_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        tfl = QVBoxLayout(top_frame)
        tfl.setContentsMargins(20, 18, 20, 18)
        tfl.setSpacing(8)

        top_lbl = QLabel("Top Products")
        top_lbl.setStyleSheet("font-weight: 700; color: #0f172a; font-size: 14px;")
        tfl.addWidget(top_lbl)

        top = data.get("top_products", [])
        if top:
            max_rev = max(float(p["revenue"]) for p in top) or 1
            for i, p in enumerate(top):
                row_widget = QWidget()
                row_layout = QVBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 4, 0, 4)
                row_layout.setSpacing(2)

                info = QLabel(f"#{i+1}  {p['name']}")
                info.setStyleSheet("font-weight: 700; color: #334155;")
                row_layout.addWidget(info)

                sub = QHBoxLayout()
                bar = QProgressBar()
                bar.setRange(0, 100)
                bar.setValue(int(float(p["revenue"]) / max_rev * 100))
                bar.setTextVisible(False)
                bar.setFixedHeight(8)
                bar.setStyleSheet("""
                    QProgressBar { border-radius: 0px; background: #e2e8f0; border: none; }
                    QProgressBar::chunk { background: #3b82f6; border-radius: 0px; }
                """)
                sub.addWidget(bar, 3)

                amt = QLabel(f"${float(p['revenue']):,.2f}  ({int(p['qty_sold'])} sold)")
                amt.setStyleSheet("color: #64748b; font-size: 11px;")
                sub.addWidget(amt, 2)
                row_layout.addLayout(sub)
                tfl.addWidget(row_widget)
        else:
            tfl.addWidget(QLabel("No sales data for this period."))

        tfl.addStretch()
        cols.addWidget(top_frame, 2)

        cols_widget = QWidget()
        cols_widget.setLayout(cols)
        self.report_layout.addWidget(cols_widget)

        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        sfl = QVBoxLayout(summary_frame)
        sfl.setContentsMargins(20, 18, 20, 18)
        sfl.setSpacing(12)

        sfl.addWidget(QLabel("Daily Sales Breakdown"))
        if daily:
            sfl.addWidget(self._build_daily_table(daily))
        else:
            sfl.addWidget(QLabel("No daily sales data for this period."))
        self.report_layout.addWidget(summary_frame)
        self.report_layout.addStretch()

    def _render_income_report(self, title: str, data: dict):
        self._clear_report()

        hdr = QLabel(title)
        hdr.setStyleSheet("""
            font-size: 17px;
            font-weight: 700;
            color: #0f172a;
            background: white;
            border-radius: 0px;
            border: 1px solid #e2e8f0;
            padding: 16px 20px;
        """)
        self.report_layout.addWidget(hdr)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)

        def kpi(label, val, color):
            f = QFrame()
            f.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border-radius: 0px;
                    border: 1px solid #e2e8f0;
                    border-left: 4px solid {color};
                }}
            """)
            fl = QVBoxLayout(f)
            fl.setContentsMargins(16, 14, 16, 14)
            fl.setSpacing(4)
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 0.3px;")
            fl.addWidget(lbl)
            v = QLabel(val)
            v.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 700;")
            fl.addWidget(v)
            return f

        cards_row.addWidget(kpi("Total Income",     f"${data['total_income']:,.2f}",    "#3b82f6"))
        cards_row.addWidget(kpi("Gross Profit",     f"${data['gross_profit']:,.2f}",    "#10b981"))
        cards_row.addWidget(kpi("COGS",             f"${data['cogs']:,.2f}",             "#f59e0b"))
        cards_row.addWidget(kpi("Transactions",     str(data['total_transactions']),     "#64748b"))
        cards_row.addWidget(kpi("Total Discount",   f"${data['total_discount']:,.2f}",   "#94a3b8"))

        card_widget = QWidget()
        card_widget.setLayout(cards_row)
        self.report_layout.addWidget(card_widget)

        mid_row = QHBoxLayout()
        mid_row.setSpacing(16)

        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        chart_frame.setMinimumHeight(280)
        clf = QVBoxLayout(chart_frame)
        clf.setContentsMargins(20, 18, 20, 18)
        clf.setSpacing(12)

        chart_lbl = QLabel("Daily Income")
        chart_lbl.setStyleSheet("font-weight: 700; color: #0f172a; font-size: 14px;")
        clf.addWidget(chart_lbl)

        daily = data.get("daily_breakdown", [])
        if daily:
            chart_view = self._build_bar_chart(daily)
            if chart_view is not None:
                clf.addWidget(chart_view)
            else:
                clf.addWidget(self._build_daily_table(daily))
        else:
            no_data = QLabel("No income data for this period.")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet("color: #94a3b8; font-size: 14px; padding: 40px;")
            clf.addWidget(no_data)

        mid_row.addWidget(chart_frame, 3)

        top_frame = QFrame()
        top_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        tfl = QVBoxLayout(top_frame)
        tfl.setContentsMargins(20, 18, 20, 18)
        tfl.setSpacing(8)

        top_lbl = QLabel("Top Products by Revenue")
        top_lbl.setStyleSheet("font-weight: 700; color: #0f172a; font-size: 14px;")
        tfl.addWidget(top_lbl)

        top = data.get("top_products", [])
        if top:
            max_rev = max(float(p["revenue"]) for p in top) or 1
            for i, p in enumerate(top):
                row_widget = QWidget()
                row_layout = QVBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 4, 0, 4)
                row_layout.setSpacing(2)
                info = QLabel(f"#{i+1}  {p['name']}")
                info.setStyleSheet("font-weight: 700; color: #334155;")
                row_layout.addWidget(info)
                sub = QHBoxLayout()
                bar = QProgressBar()
                bar.setRange(0, 100)
                bar.setValue(int(float(p["revenue"]) / max_rev * 100))
                bar.setTextVisible(False)
                bar.setFixedHeight(8)
                bar.setStyleSheet("""
                    QProgressBar { border-radius: 0px; background: #e2e8f0; border: none; }
                    QProgressBar::chunk { background: #3b82f6; border-radius: 0px; }
                """)
                sub.addWidget(bar, 3)
                amt = QLabel(f"${float(p['revenue']):,.2f}  ({int(p['qty_sold'])} sold)")
                amt.setStyleSheet("color: #64748b; font-size: 11px;")
                sub.addWidget(amt, 2)
                row_layout.addLayout(sub)
                tfl.addWidget(row_widget)
        else:
            tfl.addWidget(QLabel("No sales data."))

        tfl.addStretch()
        mid_row.addWidget(top_frame, 2)

        mid_widget = QWidget()
        mid_widget.setLayout(mid_row)
        self.report_layout.addWidget(mid_widget)

        payment_frame = QFrame()
        payment_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        pfl = QVBoxLayout(payment_frame)
        pfl.setContentsMargins(20, 18, 20, 18)
        pfl.setSpacing(12)

        pfl.addWidget(QLabel("Payment Method Breakdown"))
        payment_data = data.get("payment_breakdown", [])
        pay_table = QTableWidget(len(payment_data), 3)
        pay_table.setHorizontalHeaderLabels(["Method", "Transactions", "Total"])
        pay_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        pay_table.setEditTriggers(QTableWidget.NoEditTriggers)
        pay_table.verticalHeader().setVisible(False)
        pay_table.setAlternatingRowColors(True)
        pay_table.setMaximumHeight(180)
        pay_table.setSelectionMode(QTableWidget.NoSelection)

        for r, p in enumerate(payment_data):
            for c, v in enumerate([p["payment_method"], str(p["count"]), f"${float(p['total']):,.2f}"]):
                item = QTableWidgetItem(v)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                pay_table.setItem(r, c, item)
        pfl.addWidget(pay_table)
        self.report_layout.addWidget(payment_frame)
        self.report_layout.addStretch()

    def _render_expense_report(self, title: str, data: dict):
        self._clear_report()

        hdr = QLabel(title)
        hdr.setStyleSheet("""
            font-size: 17px;
            font-weight: 700;
            color: #0f172a;
            background: white;
            border-radius: 0px;
            border: 1px solid #e2e8f0;
            padding: 16px 20px;
        """)
        self.report_layout.addWidget(hdr)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)

        def kpi(label, val, color):
            f = QFrame()
            f.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border-radius: 0px;
                    border: 1px solid #e2e8f0;
                    border-left: 4px solid {color};
                }}
            """)
            fl = QVBoxLayout(f)
            fl.setContentsMargins(16, 14, 16, 14)
            fl.setSpacing(4)
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600; letter-spacing: 0.3px;")
            fl.addWidget(lbl)
            v = QLabel(val)
            v.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 700;")
            fl.addWidget(v)
            return f

        cards_row.addWidget(kpi("Total Expenditure", f"${data['total_expenditure']:,.2f}", "#f59e0b"))
        cards_row.addWidget(kpi("Total Purchases",   str(data['total_purchases']),         "#64748b"))

        card_widget = QWidget()
        card_widget.setLayout(cards_row)
        self.report_layout.addWidget(card_widget)

        mid_row = QHBoxLayout()
        mid_row.setSpacing(16)

        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        chart_frame.setMinimumHeight(280)
        clf = QVBoxLayout(chart_frame)
        clf.setContentsMargins(20, 18, 20, 18)
        clf.setSpacing(12)

        chart_lbl = QLabel("Daily Expenditure")
        chart_lbl.setStyleSheet("font-weight: 700; color: #0f172a; font-size: 14px;")
        clf.addWidget(chart_lbl)

        daily = data.get("daily_breakdown", [])
        if daily:
            chart_view = self._build_bar_chart(daily, "Expense ($)")
            if chart_view is not None:
                clf.addWidget(chart_view)
            else:
                table = QTableWidget(len(daily), 3)
                table.setHorizontalHeaderLabels(["Date", "Expense", "Purchases"])
                table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
                table.setEditTriggers(QTableWidget.NoEditTriggers)
                table.verticalHeader().setVisible(False)
                table.setAlternatingRowColors(True)
                table.setMaximumHeight(220)
                table.setSelectionMode(QTableWidget.NoSelection)
                for r, d in enumerate(daily):
                    day = d["day"]
                    if hasattr(day, "strftime"):
                        day_str = day.strftime("%A, %B %d, %Y")
                    else:
                        day_str = str(day)
                    for c, v in enumerate([day_str, f"${float(d['amount']):,.2f}", str(d['count'])]):
                        item = QTableWidgetItem(v)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        table.setItem(r, c, item)
                clf.addWidget(table)
        else:
            no_data = QLabel("No expenditure data for this period.")
            no_data.setAlignment(Qt.AlignCenter)
            no_data.setStyleSheet("color: #94a3b8; font-size: 14px; padding: 40px;")
            clf.addWidget(no_data)

        mid_row.addWidget(chart_frame, 3)

        top_frame = QFrame()
        top_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        tfl = QVBoxLayout(top_frame)
        tfl.setContentsMargins(20, 18, 20, 18)
        tfl.setSpacing(8)

        top_lbl = QLabel("Top Stock Purchases")
        top_lbl.setStyleSheet("font-weight: 700; color: #0f172a; font-size: 14px;")
        tfl.addWidget(top_lbl)

        top = data.get("top_purchases", [])
        if top:
            max_spent = max(float(p["total_spent"]) for p in top) or 1
            for i, p in enumerate(top):
                row_widget = QWidget()
                row_layout = QVBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 4, 0, 4)
                row_layout.setSpacing(2)
                info = QLabel(f"#{i+1}  {p['name']}")
                info.setStyleSheet("font-weight: 700; color: #334155;")
                row_layout.addWidget(info)
                sub = QHBoxLayout()
                bar = QProgressBar()
                bar.setRange(0, 100)
                bar.setValue(int(float(p["total_spent"]) / max_spent * 100))
                bar.setTextVisible(False)
                bar.setFixedHeight(8)
                bar.setStyleSheet("""
                    QProgressBar { border-radius: 0px; background: #e2e8f0; border: none; }
                    QProgressBar::chunk { background: #f59e0b; border-radius: 0px; }
                """)
                sub.addWidget(bar, 3)
                amt = QLabel(f"${float(p['total_spent']):,.2f}  ({int(p['qty_purchased'])} units)")
                amt.setStyleSheet("color: #64748b; font-size: 11px;")
                sub.addWidget(amt, 2)
                row_layout.addLayout(sub)
                tfl.addWidget(row_widget)
        else:
            tfl.addWidget(QLabel("No purchase data."))

        tfl.addStretch()
        mid_row.addWidget(top_frame, 2)

        mid_widget = QWidget()
        mid_widget.setLayout(mid_row)
        self.report_layout.addWidget(mid_widget)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)

        supplier_frame = QFrame()
        supplier_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        sfl = QVBoxLayout(supplier_frame)
        sfl.setContentsMargins(20, 18, 20, 18)
        sfl.setSpacing(12)

        sfl.addWidget(QLabel("Supplier Breakdown"))
        suppliers = data.get("supplier_breakdown", [])
        sup_table = QTableWidget(len(suppliers), 3)
        sup_table.setHorizontalHeaderLabels(["Supplier", "Purchases", "Total Spent"])
        sup_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        sup_table.setEditTriggers(QTableWidget.NoEditTriggers)
        sup_table.verticalHeader().setVisible(False)
        sup_table.setAlternatingRowColors(True)
        sup_table.setMaximumHeight(180)
        sup_table.setSelectionMode(QTableWidget.NoSelection)

        for r, s in enumerate(suppliers):
            for c, v in enumerate([s["supplier"], str(s["count"]), f"${float(s['total']):,.2f}"]):
                item = QTableWidgetItem(v)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                sup_table.setItem(r, c, item)
        sfl.addWidget(sup_table)
        bottom_row.addWidget(supplier_frame)

        cat_frame = QFrame()
        cat_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        cfl = QVBoxLayout(cat_frame)
        cfl.setContentsMargins(20, 18, 20, 18)
        cfl.setSpacing(12)

        cfl.addWidget(QLabel("Category Breakdown"))
        categories = data.get("category_breakdown", [])
        cat_table = QTableWidget(len(categories), 2)
        cat_table.setHorizontalHeaderLabels(["Category", "Total Spent"])
        cat_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        cat_table.setEditTriggers(QTableWidget.NoEditTriggers)
        cat_table.verticalHeader().setVisible(False)
        cat_table.setAlternatingRowColors(True)
        cat_table.setMaximumHeight(180)
        cat_table.setSelectionMode(QTableWidget.NoSelection)

        for r, c in enumerate(categories):
            for c2, v in enumerate([c["category"], f"${float(c['total']):,.2f}"]):
                item = QTableWidgetItem(v)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                cat_table.setItem(r, c2, item)
        cfl.addWidget(cat_table)
        bottom_row.addWidget(cat_frame)

        bottom_widget = QWidget()
        bottom_widget.setLayout(bottom_row)
        self.report_layout.addWidget(bottom_widget)
        self.report_layout.addStretch()

    def _build_bar_chart(self, daily, label="Income ($)"):
        try:
            from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis  # type: ignore[import]
        except ImportError:
            return None
        is_expense = "Expense" in label
        color = "#f59e0b" if is_expense else "#3b82f6"
        val_key = "amount" if is_expense else "income"
        bar_set = QBarSet(label)
        bar_set.setColor(QColor(color))
        categories = []
        for d in daily:
            bar_set.append(float(d[val_key]))
            day_obj = d["day"]
            if hasattr(day_obj, "strftime"):
                categories.append(day_obj.strftime("%b %d"))
            else:
                categories.append(str(day_obj))

        series = QBarSeries()
        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().hide()
        chart.setBackgroundBrush(Qt.white)

        axisX = QBarCategoryAxis()
        axisX.append(categories)
        axisX.setLabelsColor(QColor("#64748b"))
        axisX.setGridLineColor(QColor("#f1f5f9"))
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)

        axisY = QValueAxis()
        axisY.setLabelsColor(QColor("#64748b"))
        axisY.setGridLineColor(QColor("#f1f5f9"))
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(220)
        return chart_view

    def _build_daily_table(self, daily):
        table = QTableWidget(len(daily), 3)
        table.setHorizontalHeaderLabels(["Date", "Income", "Transactions"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setMaximumHeight(220)
        table.setSelectionMode(QTableWidget.NoSelection)

        for r, d in enumerate(daily):
            day = d["day"]
            if hasattr(day, "strftime"):
                day_str = day.strftime("%A, %B %d, %Y")
            else:
                day_str = str(day)
            for c, v in enumerate([day_str, f"${float(d['income']):,.2f}", str(d['txns'])]):
                item = QTableWidgetItem(v)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(r, c, item)
        return table

    def refresh(self):
        self._show_weekly()
