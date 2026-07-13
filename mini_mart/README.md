# 🛒 Mini Mart Management System

A full-featured desktop Point-of-Sale and inventory management application
built with **PyQt5** + **MySQL**.

---

## Features

| Feature | Details |
|---|---|
| **Dashboard** | Live stats, today's revenue, low-stock alerts, recent sales |
| **New Sale (POS)** | Search & add products to cart, discount, payment method |
| **Products** | Add / edit / delete products with category, cost & sell price |
| **Stock In** | Record supplier purchases, auto-update inventory |
| **Search** | Search by Product Name, Product Code/ID, or Category |
| **Reports** | Weekly & Monthly income/expenditure with charts & top products |

---

## Tech Stack

- **GUI**: PyQt5 (PyQtChart for bar charts)
- **Database**: MySQL 8.x via `mysql-connector-python`
- **Architecture**: OOP with interfaces (ABCs), models, and separated UI/DB layers

---

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
# For charts (optional but recommended):
pip install PyQtChart
```

### 2. Install & start MySQL

Make sure MySQL is running on `localhost:3306`.

### 3. Configure database credentials

Edit **`database/config.py`**:

```python
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "YOUR_PASSWORD_HERE",   # ← change this
    "database": "mini_mart_db",
    ...
}
```

The app **automatically creates** the database and all tables on first run.

### 4. Run

```bash
python main.py
```

---

## Project Structure

```
mini_mart/
├── main.py                  # Entry point
├── requirements.txt
├── database/
│   ├── config.py            # MySQL credentials
│   └── db_manager.py        # All SQL queries (DatabaseManager class)
├── models/
│   └── models.py            # Interfaces (IProduct, ISaleable, IReport)
│                              and data classes (Product, Sale, SaleItem …)
└── ui/
    ├── main_window.py        # Main window with vertical tab bar
    ├── dashboard_tab.py      # Overview & alerts
    ├── sales_tab.py          # POS / new sale
    ├── products_tab.py       # Product CRUD
    ├── stock_tab.py          # Stock purchase recording
    ├── search_tab.py         # Multi-field product search
    └── reports_tab.py        # Weekly / monthly reports
```

---

## Database Schema

```
categories        — product categories
products          — inventory items (code, name, price, qty …)
sales             — completed transactions
sale_items        — line items per sale
stock_purchases   — supplier purchase records
```

---

## Default Categories (seeded on first run)

Beverages · Snacks · Dairy · Bakery · Frozen Foods ·
Household · Personal Care · Canned Goods · Condiments · Others

---

## Notes

- **Low stock threshold**: products with qty ≤ 10 are flagged in red on the Dashboard and Products tab.
- **Profit margin**: visible in the Search tab per product.
- **Charts**: require `PyQtChart` (`pip install PyQtChart`). If not installed, a plain table is shown instead.
