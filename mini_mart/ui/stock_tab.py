"""
Stock Tab - Record incoming stock / purchases
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox,
    QPushButton, QTableWidget, QTableWidgetItem,
    QFrame, QFormLayout, QMessageBox, QTextEdit,
    QHeaderView, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from models.models import StockPurchase
from ui.styles import success, ghost, danger, small


class StockTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._products_cache = []
        self.selected_purchase_id = None
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(20)

        form_frame = QFrame()
        form_frame.setFixedWidth(380)
        form_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        fl = QVBoxLayout(form_frame)
        fl.setContentsMargins(24, 24, 24, 24)
        fl.setSpacing(14)

        self.form_title = QLabel("Record Stock Purchase")
        self.form_title.setStyleSheet("font-size: 17px; font-weight: 700; color: #0f172a;")
        fl.addWidget(self.form_title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter products")
        self.search_edit.textChanged.connect(self._filter_products)
        form.addRow("Search:", self.search_edit)

        self.product_combo = QComboBox()
        self.product_combo.setEditable(True)
        self.product_combo.setInsertPolicy(QComboBox.NoInsert)
        self.product_combo.currentIndexChanged.connect(self._on_product_change)
        form.addRow("Product *:", self.product_combo)

        self.current_stock_lbl = QLabel("\u2014")
        self.current_stock_lbl.setStyleSheet("color: #3b82f6; font-weight: 700;")
        form.addRow("Current Stock:", self.current_stock_lbl)

        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 999999)
        form.addRow("Qty to Add *:", self.qty_spin)

        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 999999)
        self.cost_spin.setDecimals(2)
        self.cost_spin.setPrefix("$ ")
        form.addRow("Cost / Unit *:", self.cost_spin)

        self.total_lbl = QLabel("$0.00")
        self.total_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #059669;")
        self.qty_spin.valueChanged.connect(self._update_total)
        self.cost_spin.valueChanged.connect(self._update_total)
        form.addRow("Total Cost:", self.total_lbl)

        self.supplier_edit = QLineEdit()
        self.supplier_edit.setPlaceholderText("Optional supplier name")
        form.addRow("Supplier:", self.supplier_edit)

        self.notes_edit = QTextEdit()
        self.notes_edit.setFixedHeight(70)
        self.notes_edit.setPlaceholderText("Optional notes")
        form.addRow("Notes:", self.notes_edit)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        form.addRow("Purchase Date:", self.date_edit)

        fl.addLayout(form)
        fl.addSpacing(8)

        self.save_btn = QPushButton("Record Purchase")
        self.save_btn.setStyleSheet(success())
        self.save_btn.clicked.connect(self._save)

        self.update_btn = QPushButton("Update")
        self.update_btn.setStyleSheet(ghost())
        self.update_btn.clicked.connect(self._update)
        self.update_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet(danger())
        self.delete_btn.clicked.connect(self._delete)
        self.delete_btn.setEnabled(False)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.update_btn)
        btn_row.addWidget(self.delete_btn)
        fl.addLayout(btn_row)
        fl.addStretch()

        outer.addWidget(form_frame)

        right = QFrame()
        right.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        rl = QVBoxLayout(right)
        rl.setContentsMargins(24, 24, 24, 24)
        rl.setSpacing(16)

        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("Purchase History"))
        hdr.addStretch()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(ghost())
        refresh_btn.clicked.connect(self.refresh)
        hdr.addWidget(refresh_btn)
        rl.addLayout(hdr)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Product", "Code", "Qty", "Cost/Unit", "Total", "Supplier"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_select)
        for col, w in enumerate([36, 140, 0, 90, 60, 80, 80, 120]):
            if w: self.table.setColumnWidth(col, w)
        rl.addWidget(self.table)

        outer.addWidget(right)

    def refresh(self):
        self._products_cache = self.db.get_all_products()
        self._refresh_combo("")
        self._load_history()
        self._clear_form()

    def _filter_products(self, text: str):
        self._refresh_combo(text.lower())

    def _refresh_combo(self, query: str):
        self.product_combo.blockSignals(True)
        self.product_combo.clear()
        has_items = False
        for p in self._products_cache:
            if query in p["name"].lower() or query in p["product_code"].lower():
                self.product_combo.addItem(f"{p['product_code']} \u2013 {p['name']}", p["product_id"])
                has_items = True
        self.product_combo.blockSignals(False)
        if has_items:
            self._on_product_change()
        else:
            self.current_stock_lbl.setText("\u2014")
            self.cost_spin.setValue(0)
            self._update_total()

    def _on_product_change(self):
        pid = self.product_combo.currentData()
        if pid is None:
            self.current_stock_lbl.setText("\u2014")
            return
        for p in self._products_cache:
            if p["product_id"] == pid:
                self.current_stock_lbl.setText(f"{p['quantity']} {p['unit']}")
                self.cost_spin.setValue(float(p["cost_price"]))
                return
        self.current_stock_lbl.setText("\u2014")

    def _update_total(self):
        total = self.qty_spin.value() * self.cost_spin.value()
        self.total_lbl.setText(f"${total:,.2f}")

    def _save(self):
        if len(self._products_cache) == 0:
            QMessageBox.warning(self, "No Products", "No products found. Add products first in the Products tab.")
            return
        pid = self.product_combo.currentData()
        if pid is None:
            QMessageBox.warning(self, "No Product", "Please select a product.")
            return

        from datetime import datetime
        purchase_date = self.date_edit.date().toPyDate()
        purchase = StockPurchase(
            product_id=pid,
            quantity=self.qty_spin.value(),
            cost_per_unit=self.cost_spin.value(),
            supplier=self.supplier_edit.text().strip(),
            notes=self.notes_edit.toPlainText().strip(),
            purchase_date=datetime.combine(purchase_date, datetime.min.time()),
        )
        ok, msg = self.db.record_purchase(purchase.to_dict())
        if ok:
            QMessageBox.information(self, "Success", msg)
            self._clear_form()
            self.refresh()
        else:
            QMessageBox.critical(self, "Error", msg)

    def _clear_form(self):
        self.selected_purchase_id = None
        self.form_title.setText("Record Stock Purchase")
        self.save_btn.setEnabled(True)
        self.update_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.search_edit.clear()
        self.product_combo.setCurrentIndex(0)
        self.qty_spin.setValue(1)
        self.cost_spin.setValue(0)
        self.supplier_edit.clear()
        self.notes_edit.clear()
        self.date_edit.setDate(QDate.currentDate())
        self.table.clearSelection()

    def _on_select(self):
        rows = self.table.selectedItems()
        if not rows:
            return
        row = self.table.currentRow()
        pid = int(self.table.item(row, 0).text())
        p = self.db.get_purchase_by_id(pid)
        if not p:
            return
        self.selected_purchase_id = pid
        self.form_title.setText("Edit Purchase")
        self.save_btn.setEnabled(False)
        self.update_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

        for i in range(self.product_combo.count()):
            if self.product_combo.itemData(i) == p["product_id"]:
                self.product_combo.setCurrentIndex(i)
                break
        self.qty_spin.setValue(int(p["quantity"]))
        self.cost_spin.setValue(float(p["cost_per_unit"]))
        self.supplier_edit.setText(p.get("supplier", ""))
        self.notes_edit.setPlainText(p.get("notes", ""))
        pd = p["purchase_date"]
        if hasattr(pd, "year"):
            self.date_edit.setDate(QDate(pd.year, pd.month, pd.day))
        else:
            self.date_edit.setDate(pd)

    def _update(self):
        if not self.selected_purchase_id:
            return
        pid = self.product_combo.currentData()
        if pid is None:
            QMessageBox.warning(self, "No Product", "Please select a product.")
            return

        from datetime import datetime
        purchase_date = self.date_edit.date().toPyDate()
        qty = self.qty_spin.value()
        cost = self.cost_spin.value()
        data = {
            "product_id": pid,
            "quantity": qty,
            "cost_per_unit": cost,
            "total_cost": qty * cost,
            "supplier": self.supplier_edit.text().strip(),
            "notes": self.notes_edit.toPlainText().strip(),
            "purchase_date": datetime.combine(purchase_date, datetime.min.time()),
        }
        ok, msg = self.db.update_purchase(self.selected_purchase_id, data)
        if ok:
            QMessageBox.information(self, "Success", msg)
            self._clear_form()
            self.refresh()
        else:
            QMessageBox.critical(self, "Error", msg)

    def _delete(self):
        if not self.selected_purchase_id:
            return
        reply = QMessageBox.question(self, "Confirm", "Delete this purchase record? Stock will be reversed.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = self.db.delete_purchase(self.selected_purchase_id)
            if ok:
                QMessageBox.information(self, "Deleted", msg)
                self._clear_form()
                self.refresh()
            else:
                QMessageBox.critical(self, "Error", msg)

    def _load_history(self):
        rows = self.db.get_recent_purchases(60)
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            vals = [
                str(row["purchase_id"]),
                row["purchase_date"].strftime("%Y-%m-%d %H:%M"),
                row["product_name"],
                row["product_code"],
                str(row["quantity"]),
                f"${float(row['cost_per_unit']):,.2f}",
                f"${float(row['total_cost']):,.2f}",
                row.get("supplier", "")
            ]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(str(v))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(r, c, item)
