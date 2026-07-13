"""
Sales Tab - Point-of-Sale style interface
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox,
    QPushButton, QTableWidget, QTableWidgetItem,
    QFrame, QMessageBox,
    QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from models.models import Sale, SaleItem
from ui.styles import primary, danger, success


class SalesTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_sale = Sale()
        self._products_cache = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(20)

        left = QVBoxLayout()
        outer.addLayout(left, 3)

        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        sf_layout = QHBoxLayout(search_frame)
        sf_layout.setContentsMargins(20, 16, 20, 16)
        sf_layout.setSpacing(12)

        sf_layout.addWidget(QLabel("Product:"))
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Type name or code to search")
        self.product_search.textChanged.connect(self._filter_products)
        sf_layout.addWidget(self.product_search, 2)

        self.product_combo = QComboBox()
        self.product_combo.setMinimumWidth(260)
        sf_layout.addWidget(self.product_combo, 2)

        sf_layout.addWidget(QLabel("Qty:"))
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 9999)
        self.qty_spin.setValue(1)
        self.qty_spin.setFixedWidth(70)
        sf_layout.addWidget(self.qty_spin)

        add_btn = QPushButton("Add to Cart")
        add_btn.setStyleSheet(primary())
        add_btn.clicked.connect(self._add_to_cart)
        sf_layout.addWidget(add_btn)
        left.addWidget(search_frame)

        cart_frame = QFrame()
        cart_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        cart_layout = QVBoxLayout(cart_frame)
        cart_layout.setContentsMargins(20, 18, 20, 18)
        cart_layout.setSpacing(12)

        cart_hdr = QHBoxLayout()
        cart_title = QLabel("Shopping Cart")
        cart_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0f172a;")
        cart_hdr.addWidget(cart_title)
        cart_hdr.addStretch()
        clear_btn = QPushButton("Clear All")
        clear_btn.setStyleSheet(danger())
        clear_btn.clicked.connect(self._clear_cart)
        cart_hdr.addWidget(clear_btn)
        cart_layout.addLayout(cart_hdr)

        self.cart_table = QTableWidget(0, 6)
        self.cart_table.setHorizontalHeaderLabels(["Product", "Code", "Unit Price", "Qty", "Subtotal", ""])
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.setMinimumHeight(320)
        self.cart_table.setSelectionMode(QTableWidget.NoSelection)
        for col, w in enumerate([0, 90, 90, 60, 90, 36]):
            if w: self.cart_table.setColumnWidth(col, w)
        cart_layout.addWidget(self.cart_table)
        left.addWidget(cart_frame)

        right = QFrame()
        right.setFixedWidth(340)
        right.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(24, 24, 24, 24)
        right_layout.setSpacing(16)

        title = QLabel("Payment")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #0f172a;")
        right_layout.addWidget(title)

        def sep():
            f = QFrame(); f.setFrameShape(QFrame.HLine)
            f.setStyleSheet("color: #e2e8f0;"); return f

        right_layout.addWidget(sep())

        sub_row = QHBoxLayout()
        sub_row.addWidget(QLabel("Subtotal:"))
        sub_row.addStretch()
        self.lbl_subtotal = QLabel("$0.00")
        self.lbl_subtotal.setStyleSheet("font-weight: 600; font-size: 15px; color: #334155;")
        sub_row.addWidget(self.lbl_subtotal)
        right_layout.addLayout(sub_row)

        disc_row = QHBoxLayout()
        disc_row.addWidget(QLabel("Discount ($):"))
        disc_row.addStretch()
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setRange(0, 999999)
        self.discount_spin.setDecimals(2)
        self.discount_spin.setFixedWidth(100)
        self.discount_spin.valueChanged.connect(self._update_totals)
        disc_row.addWidget(self.discount_spin)
        right_layout.addLayout(disc_row)

        right_layout.addWidget(sep())

        total_row = QHBoxLayout()
        total_lbl = QLabel("TOTAL")
        total_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #0f172a;")
        total_row.addWidget(total_lbl)
        total_row.addStretch()
        self.lbl_total = QLabel("$0.00")
        self.lbl_total.setStyleSheet("font-size: 24px; font-weight: 700; color: #059669;")
        total_row.addWidget(self.lbl_total)
        right_layout.addLayout(total_row)

        right_layout.addWidget(sep())

        right_layout.addWidget(QLabel("Payment Method:"))
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Cash", "Card", "Mobile Pay", "Transfer"])
        right_layout.addWidget(self.payment_combo)

        right_layout.addWidget(QLabel("Notes:"))
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Optional")
        right_layout.addWidget(self.notes_edit)

        right_layout.addStretch()

        complete_btn = QPushButton("Complete Sale")
        complete_btn.setStyleSheet(success())
        complete_btn.clicked.connect(self._complete_sale)
        right_layout.addWidget(complete_btn)

        outer.addWidget(right)

    def refresh(self):
        self._products_cache = self.db.get_all_products()
        self._refresh_product_combo("")

    def _filter_products(self, text: str):
        self._refresh_product_combo(text.lower())

    def _refresh_product_combo(self, query: str):
        self.product_combo.clear()
        for p in self._products_cache:
            if query in p["name"].lower() or query in p["product_code"].lower():
                label = f"{p['product_code']} \u2013 {p['name']}  (Stock: {p['quantity']})"
                self.product_combo.addItem(label, p["product_id"])

    def _get_selected_product(self):
        pid = self.product_combo.currentData()
        if pid is None:
            return None
        for p in self._products_cache:
            if p["product_id"] == pid:
                return p
        return None

    def _add_to_cart(self):
        p = self._get_selected_product()
        if not p:
            QMessageBox.warning(self, "No Product", "Please select a product first.")
            return
        qty = self.qty_spin.value()
        if qty > p["quantity"]:
            QMessageBox.warning(self, "Stock Error", f"Only {p['quantity']} {p['unit']} in stock.")
            return

        item = SaleItem(
            product_id=p["product_id"],
            product_name=p["name"],
            product_code=p["product_code"],
            quantity=qty,
            unit_price=float(p["sell_price"]),
            cost_price=float(p["cost_price"]),
        )
        self.current_sale.add_item(item)
        self._refresh_cart()
        self.product_search.clear()
        self.qty_spin.setValue(1)

    def _refresh_cart(self):
        items = self.current_sale.items
        self.cart_table.setRowCount(len(items))
        for r, it in enumerate(items):
            self.cart_table.setItem(r, 0, QTableWidgetItem(it.product_name))
            self.cart_table.setItem(r, 1, QTableWidgetItem(it.product_code))
            self.cart_table.setItem(r, 2, QTableWidgetItem(f"${it.unit_price:,.2f}"))
            self.cart_table.setItem(r, 3, QTableWidgetItem(str(it.quantity)))
            self.cart_table.setItem(r, 4, QTableWidgetItem(f"${it.subtotal:,.2f}"))

            del_btn = QPushButton(chr(0x2715))
            del_btn.setStyleSheet("""
                QPushButton {
                    background: #fef2f2;
                    color: #ef4444;
                    font-weight: bold;
                    border-radius: 6px;
                    padding: 2px;
                    border: 1px solid #fecaca;
                }
                QPushButton:hover { background: #fee2e2; }
            """)
            del_btn.setFixedSize(28, 24)
            pid = it.product_id
            del_btn.clicked.connect(lambda _, p=pid: self._remove_item(p))
            self.cart_table.setCellWidget(r, 5, del_btn)

        self._update_totals()

    def _remove_item(self, product_id: int):
        self.current_sale.remove_item(product_id)
        self._refresh_cart()

    def _update_totals(self):
        self.current_sale.discount = self.discount_spin.value()
        self.lbl_subtotal.setText(f"${self.current_sale.subtotal:,.2f}")
        self.lbl_total.setText(f"${self.current_sale.total:,.2f}")

    def _clear_cart(self):
        self.current_sale.clear()
        self.discount_spin.setValue(0)
        self._refresh_cart()

    def _complete_sale(self):
        if not self.current_sale.items:
            QMessageBox.warning(self, "Empty Cart", "Add products to the cart first.")
            return

        items_data = [it.to_dict() for it in self.current_sale.items]
        ok, msg = self.db.record_sale(
            items=items_data,
            total=self.current_sale.total,
            discount=self.current_sale.discount,
            payment=self.payment_combo.currentText(),
            notes=self.notes_edit.text(),
        )
        if ok:
            QMessageBox.information(self, "Sale Complete", msg)
            self._clear_cart()
            self.notes_edit.clear()
            self._products_cache = self.db.get_all_products()
        else:
            QMessageBox.critical(self, "Error", msg)
