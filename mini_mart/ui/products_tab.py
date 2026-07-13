"""
Products Tab - Manage inventory products
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox,
    QPushButton, QTableWidget, QTableWidgetItem,
    QFormLayout, QMessageBox, QFrame,
    QTextEdit, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from models.models import Product
from ui.styles import primary, danger, ghost, small


class ProductsTab(QWidget):
    product_changed = pyqtSignal()

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.selected_product_id = None
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        form_frame = QFrame()
        form_frame.setFixedWidth(380)
        form_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 0px;
                border: 1px solid #e2e8f0;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(14)

        self.form_title = QLabel("Add New Product")
        self.form_title.setStyleSheet("font-size: 17px; font-weight: 700; color: #0f172a;")
        form_layout.addWidget(self.form_title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.code_edit   = QLineEdit(); self.code_edit.setPlaceholderText("e.g. PRD-001")
        self.name_edit   = QLineEdit(); self.name_edit.setPlaceholderText("Product name")
        self.cat_combo   = QComboBox()
        self.cost_spin   = QDoubleSpinBox(); self.cost_spin.setRange(0, 999999); self.cost_spin.setDecimals(2); self.cost_spin.setPrefix("$ ")
        self.sell_spin   = QDoubleSpinBox(); self.sell_spin.setRange(0, 999999); self.sell_spin.setDecimals(2); self.sell_spin.setPrefix("$ ")
        self.qty_spin    = QSpinBox();       self.qty_spin.setRange(0, 999999)
        self.unit_edit   = QLineEdit();      self.unit_edit.setPlaceholderText("pcs / kg / box")
        self.unit_edit.setText("pcs")
        self.desc_edit   = QTextEdit();      self.desc_edit.setFixedHeight(70); self.desc_edit.setPlaceholderText("Optional description")

        code_row = QHBoxLayout()
        code_row.setSpacing(6)
        self.code_edit.setPlaceholderText("Auto-generated")
        gen_btn = QPushButton("Gen")
        gen_btn.setFixedWidth(50)
        gen_btn.setStyleSheet(small())
        gen_btn.clicked.connect(self._generate_code)
        code_row.addWidget(self.code_edit, 1)
        code_row.addWidget(gen_btn)
        form.addRow("Code *", code_row)
        form.addRow("Name *",        self.name_edit)
        form.addRow("Category *",    self.cat_combo)
        form.addRow("Cost Price *",  self.cost_spin)
        form.addRow("Sell Price *",  self.sell_spin)
        form.addRow("Quantity",      self.qty_spin)
        form.addRow("Unit",          self.unit_edit)
        form.addRow("Description",   self.desc_edit)

        form_layout.addLayout(form)
        form_layout.addSpacing(8)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.save_btn   = QPushButton("Save")
        self.clear_btn  = QPushButton("Clear")
        self.delete_btn = QPushButton("Delete")
        self.save_btn.setStyleSheet(primary())
        self.clear_btn.setStyleSheet(ghost())
        self.delete_btn.setStyleSheet(danger())
        self.delete_btn.setEnabled(False)

        self.save_btn.clicked.connect(self._save)
        self.clear_btn.clicked.connect(self._clear_form)
        self.delete_btn.clicked.connect(self._delete)

        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addWidget(self.delete_btn)
        form_layout.addLayout(btn_row)
        form_layout.addStretch()

        layout.addWidget(form_frame)

        right = QFrame()
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

        hdr = QHBoxLayout()
        title2 = QLabel("Product Inventory")
        title2.setStyleSheet("font-size: 17px; font-weight: 700; color: #0f172a;")
        hdr.addWidget(title2)
        hdr.addStretch()
        self.count_label = QLabel("0 products")
        self.count_label.setStyleSheet("color: #64748b; font-size: 13px;")
        hdr.addWidget(self.count_label)
        right_layout.addLayout(hdr)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["ID", "Code", "Name", "Category", "Cost", "Price", "Qty", "Unit"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_select)

        for col, w in enumerate([40, 90, 0, 110, 80, 80, 60, 60]):
            if w: self.table.setColumnWidth(col, w)

        right_layout.addWidget(self.table)
        layout.addWidget(right)

        self._load_categories()

    def _generate_code(self):
        products = self.db.get_all_products()
        max_num = 0
        for p in products:
            code = p.get("product_code", "")
            if code.startswith("PRD-"):
                try:
                    num = int(code.split("-")[1])
                    if num > max_num:
                        max_num = num
                except (ValueError, IndexError):
                    continue
        new_code = f"PRD-{max_num + 1:03d}"
        self.code_edit.setText(new_code)

    def _load_categories(self):
        self.cat_combo.clear()
        cats = self.db.get_all_categories()
        for cat in cats:
            self.cat_combo.addItem(cat["name"], cat["category_id"])

    def refresh(self):
        self._load_categories()
        products = self.db.get_all_products()
        self.table.setRowCount(len(products))
        self.count_label.setText(f"{len(products)} products")

        for r, p in enumerate(products):
            vals = [
                p["product_id"], p["product_code"], p["name"],
                p["category_name"],
                f"${float(p['cost_price']):,.2f}",
                f"${float(p['sell_price']):,.2f}",
                p["quantity"], p["unit"]
            ]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(str(v))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                if c == 6 and int(p["quantity"]) <= 10:
                    item.setForeground(QColor("#ef4444"))
                    item.setFont(QFont("Arial", 10, QFont.Bold))
                self.table.setItem(r, c, item)

    def _on_select(self):
        rows = self.table.selectedItems()
        if not rows:
            return
        row = self.table.currentRow()
        pid = int(self.table.item(row, 0).text())
        p = self.db.get_product_by_id(pid)
        if not p:
            return
        self.selected_product_id = pid
        self.form_title.setText("Edit Product")
        self.code_edit.setText(p["product_code"])
        self.name_edit.setText(p["name"])
        idx = self.cat_combo.findData(p["category_id"])
        if idx >= 0: self.cat_combo.setCurrentIndex(idx)
        self.cost_spin.setValue(float(p["cost_price"]))
        self.sell_spin.setValue(float(p["sell_price"]))
        self.qty_spin.setValue(int(p["quantity"]))
        self.unit_edit.setText(p["unit"])
        self.desc_edit.setPlainText(p.get("description", ""))
        self.delete_btn.setEnabled(True)

    def _save(self):
        code = self.code_edit.text().strip()
        name = self.name_edit.text().strip()
        if not code or not name:
            QMessageBox.warning(self, "Validation", "Product Code and Name are required.")
            return
        data = {
            "product_code": code,
            "name": name,
            "category_id": self.cat_combo.currentData(),
            "cost_price": self.cost_spin.value(),
            "sell_price": self.sell_spin.value(),
            "quantity": self.qty_spin.value(),
            "unit": self.unit_edit.text().strip() or "pcs",
            "description": self.desc_edit.toPlainText().strip(),
        }
        if self.selected_product_id:
            ok, msg = self.db.update_product(self.selected_product_id, data)
        else:
            ok, msg = self.db.add_product(data)

        if ok:
            QMessageBox.information(self, "Success", msg)
            self._clear_form()
            self.refresh()
            self.product_changed.emit()
        else:
            QMessageBox.critical(self, "Error", msg)

    def _delete(self):
        if not self.selected_product_id:
            return
        reply = QMessageBox.question(self, "Confirm", "Delete this product?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = self.db.delete_product(self.selected_product_id)
            if ok:
                QMessageBox.information(self, "Deleted", msg)
                self._clear_form()
                self.refresh()
            else:
                QMessageBox.critical(self, "Error", msg)

    def _clear_form(self):
        self.selected_product_id = None
        self.form_title.setText("Add New Product")
        self._generate_code()
        self.name_edit.clear()
        self.cat_combo.setCurrentIndex(0)
        self.cost_spin.setValue(0)
        self.sell_spin.setValue(0)
        self.qty_spin.setValue(0)
        self.unit_edit.setText("pcs")
        self.desc_edit.clear()
        self.delete_btn.setEnabled(False)
        self.table.clearSelection()
