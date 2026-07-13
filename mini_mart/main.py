"""
Mini Mart Management System - Main Entry Point
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Mini Mart Management System")
    app.setStyle("Fusion")

    # Apply global stylesheet
    app.setStyleSheet("""
        QMainWindow { background-color: #f1f5f9; }
        QWidget {
            font-family: 'JetBrains Mono', 'DejaVu Sans Mono', 'Consolas', monospace;
            font-size: 12px;
            color: #334155;
        }
        QPushButton {
            background-color: #2563eb;
            color: white;
            border: none;
            border-radius: 0px;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 12px;
            min-height: 24px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #1d4ed8;
        }
        QPushButton:pressed {
            background-color: #1e40af;
            padding-top: 14px;
            padding-bottom: 10px;
        }
        QPushButton:disabled {
            background-color: #e2e8f0;
            color: #94a3b8;
        }
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            border: 1.5px solid #e2e8f0;
            border-radius: 0px;
            padding: 7px 10px;
            background: white;
            color: #1e293b;
            selection-background-color: #dbeafe;
        }
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border-color: #2563eb;
        }
        QComboBox::drop-down {
            border: none;
            padding-right: 8px;
        }
        QTextEdit {
            border: 1.5px solid #e2e8f0;
            border-radius: 0px;
            padding: 6px;
            background: white;
            color: #1e293b;
        }
        QTextEdit:focus { border-color: #2563eb; }
        QTableWidget {
            border: 1px solid #e2e8f0;
            border-radius: 0px;
            gridline-color: #f1f5f9;
            background: white;
            outline: none;
        }
        QTableWidget::item {
            padding: 8px 10px;
            color: #334155;
            border-bottom: 1px solid #f8fafc;
        }
        QTableWidget::item:selected {
            background-color: #eff6ff;
            color: #1d4ed8;
        }
        QHeaderView::section {
            background-color: #f8fafc;
            color: #64748b;
            padding: 10px 10px;
            border: none;
            border-bottom: 2px solid #e2e8f0;
            font-weight: 600;
            font-size: 11px;
            text-transform: uppercase;
        }
        QGroupBox {
            border: 1px solid #e2e8f0;
            border-radius: 0px;
            margin-top: 12px;
            padding-top: 10px;
            font-weight: 600;
            color: #1e293b;
            background: white;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
        }
        QLabel { color: #475569; background: transparent; }
        QScrollBar:vertical {
            width: 8px;
            background: transparent;
            border-radius: 0px;
        }
        QScrollBar::handle:vertical {
            background: #cbd5e1;
            border-radius: 0px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover { background: #94a3b8; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
        }
        QScrollBar:horizontal {
            height: 8px;
            background: transparent;
            border-radius: 0px;
        }
        QScrollBar::handle:horizontal {
            background: #cbd5e1;
            border-radius: 0px;
            min-width: 30px;
        }
        QScrollBar::handle:horizontal:hover { background: #94a3b8; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0;
        }
        QMessageBox {
            background: white;
        }
        QMessageBox QLabel {
            color: #1e293b;
            font-size: 13px;
        }
        QMessageBox QPushButton {
            min-width: 80px;
        }
    """)

    # Initialize database
    db = DatabaseManager()
    if not db.connect():
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Database Error")
        msg.setText("Cannot connect to MySQL database.\n\nPlease ensure MySQL is running and check your connection settings in:\ndatabase/config.py")
        msg.exec_()
        sys.exit(1)

    db.initialize_tables()

    window = MainWindow(db)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
