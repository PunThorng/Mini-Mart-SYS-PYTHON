"""
DatabaseManager - Handles all MySQL operations for Mini Mart
"""
from __future__ import annotations
import mysql.connector
from mysql.connector import Error, MySQLConnection
from typing import Optional, List, Dict, Any, Tuple
from database.config import DB_CONFIG


class DatabaseManager:
    """Central database access object. Owns the connection lifecycle."""

    def __init__(self):
        self._conn: Optional[MySQLConnection] = None

    # ------------------------------------------------------------------ #
    #  Connection                                                          #
    # ------------------------------------------------------------------ #
    def connect(self) -> bool:
        try:
            # First connect without specifying a database to create it if needed
            cfg = dict(DB_CONFIG)
            db_name = cfg.pop("database")
            cfg.pop("autocommit", None)

            tmp = mysql.connector.connect(**cfg)
            cur = tmp.cursor()
            safe_name = "".join(c for c in db_name if c.isalnum() or c in "_")
            cur.execute(
                "CREATE DATABASE IF NOT EXISTS `%s` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci" % safe_name
            )
            cur.close()
            tmp.close()

            # Now connect to the actual DB
            self._conn = mysql.connector.connect(**DB_CONFIG)
            return True
        except Error as e:
            print(f"[DB] Connection error: {e}")
            return False

    def disconnect(self):
        if self._conn and self._conn.is_connected():
            self._conn.close()

    def _cursor(self):
        if not self._conn or not self._conn.is_connected():
            if not self.connect():
                raise RuntimeError("Cannot connect to database")
        return self._conn.cursor(dictionary=True)

    def _commit(self):
        self._conn.commit()

    def _rollback(self):
        self._conn.rollback()

    # ------------------------------------------------------------------ #
    #  Schema initialisation                                               #
    # ------------------------------------------------------------------ #
    def initialize_tables(self):
        ddl_statements = [
            """
            CREATE TABLE IF NOT EXISTS categories (
                category_id   INT AUTO_INCREMENT PRIMARY KEY,
                name          VARCHAR(100) NOT NULL UNIQUE,
                description   TEXT,
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
            """,
            """
            CREATE TABLE IF NOT EXISTS products (
                product_id    INT AUTO_INCREMENT PRIMARY KEY,
                product_code  VARCHAR(50) NOT NULL UNIQUE,
                name          VARCHAR(200) NOT NULL,
                category_id   INT NOT NULL,
                cost_price    DECIMAL(12,2) NOT NULL DEFAULT 0.00,
                sell_price    DECIMAL(12,2) NOT NULL DEFAULT 0.00,
                quantity      INT NOT NULL DEFAULT 0,
                unit          VARCHAR(30) DEFAULT 'pcs',
                description   TEXT,
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            ) ENGINE=InnoDB
            """,
            """
            CREATE TABLE IF NOT EXISTS sales (
                sale_id       INT AUTO_INCREMENT PRIMARY KEY,
                sale_date     DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_amount  DECIMAL(12,2) NOT NULL DEFAULT 0.00,
                discount      DECIMAL(12,2) NOT NULL DEFAULT 0.00,
                payment_method VARCHAR(30) DEFAULT 'Cash',
                notes         TEXT
            ) ENGINE=InnoDB
            """,
            """
            CREATE TABLE IF NOT EXISTS sale_items (
                item_id       INT AUTO_INCREMENT PRIMARY KEY,
                sale_id       INT NOT NULL,
                product_id    INT NOT NULL,
                quantity      INT NOT NULL,
                unit_price    DECIMAL(12,2) NOT NULL,
                cost_price    DECIMAL(12,2) NOT NULL,
                subtotal      DECIMAL(12,2) NOT NULL,
                FOREIGN KEY (sale_id)    REFERENCES sales(sale_id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            ) ENGINE=InnoDB
            """,
            """
            CREATE TABLE IF NOT EXISTS stock_purchases (
                purchase_id   INT AUTO_INCREMENT PRIMARY KEY,
                product_id    INT NOT NULL,
                quantity      INT NOT NULL,
                cost_per_unit DECIMAL(12,2) NOT NULL,
                total_cost    DECIMAL(12,2) NOT NULL,
                purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                supplier      VARCHAR(200),
                notes         TEXT,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            ) ENGINE=InnoDB
            """,
        ]

        cur = self._cursor()
        try:
            for stmt in ddl_statements:
                cur.execute(stmt)
            self._conn.commit()
            self._seed_categories(cur)
            self._conn.commit()
        finally:
            cur.close()

    def _seed_categories(self, cur):
        defaults = [
            ("Beverages", "Drinks and liquid refreshments"),
            ("Snacks", "Chips, cookies and light snacks"),
            ("Dairy", "Milk, cheese, yogurt products"),
            ("Bakery", "Bread, pastries and baked goods"),
            ("Frozen Foods", "Frozen and refrigerated items"),
            ("Household", "Cleaning and household supplies"),
            ("Personal Care", "Hygiene and personal care items"),
            ("Canned Goods", "Canned and preserved foods"),
            ("Condiments", "Sauces, spices and condiments"),
            ("Others", "Miscellaneous products"),
        ]
        cur.executemany(
            "INSERT IGNORE INTO categories (name, description) VALUES (%s, %s)",
            defaults
        )

    # ------------------------------------------------------------------ #
    #  Categories                                                          #
    # ------------------------------------------------------------------ #
    def get_all_categories(self) -> List[Dict]:
        cur = self._cursor()
        cur.execute("SELECT * FROM categories ORDER BY name")
        result = cur.fetchall()
        cur.close()
        return result

    def add_category(self, name: str, description: str = "") -> bool:
        cur = self._cursor()
        try:
            cur.execute("INSERT INTO categories (name, description) VALUES (%s, %s)", (name, description))
            self._commit()
            return True
        except Error:
            self._rollback()
            return False
        finally:
            cur.close()

    # ------------------------------------------------------------------ #
    #  Products                                                            #
    # ------------------------------------------------------------------ #
    def get_all_products(self) -> List[Dict]:
        cur = self._cursor()
        cur.execute("""
            SELECT p.*, c.name AS category_name
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            ORDER BY p.name
        """)
        result = cur.fetchall()
        cur.close()
        return result

    def search_products(self, query: str, field: str = "name") -> List[Dict]:
        """field can be 'name', 'product_code', or 'category'"""
        cur = self._cursor()
        like = f"%{query}%"
        if field == "name":
            sql = """
                SELECT p.*, c.name AS category_name
                FROM products p JOIN categories c ON p.category_id = c.category_id
                WHERE p.name LIKE %s ORDER BY p.name
            """
        elif field == "product_code":
            sql = """
                SELECT p.*, c.name AS category_name
                FROM products p JOIN categories c ON p.category_id = c.category_id
                WHERE p.product_code LIKE %s ORDER BY p.name
            """
        else:  # category
            sql = """
                SELECT p.*, c.name AS category_name
                FROM products p JOIN categories c ON p.category_id = c.category_id
                WHERE c.name LIKE %s ORDER BY p.name
            """
        cur.execute(sql, (like,))
        result = cur.fetchall()
        cur.close()
        return result

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        cur = self._cursor()
        cur.execute("""
            SELECT p.*, c.name AS category_name
            FROM products p JOIN categories c ON p.category_id = c.category_id
            WHERE p.product_id = %s
        """, (product_id,))
        result = cur.fetchone()
        cur.close()
        return result

    def add_product(self, data: Dict) -> Tuple[bool, str]:
        cur = self._cursor()
        try:
            cur.execute("""
                INSERT INTO products (product_code, name, category_id, cost_price, sell_price, quantity, unit, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data["product_code"], data["name"], data["category_id"],
                data["cost_price"], data["sell_price"], data["quantity"],
                data.get("unit", "pcs"), data.get("description", "")
            ))
            self._commit()
            return True, "Product added successfully."
        except Error as e:
            self._rollback()
            return False, str(e)
        finally:
            cur.close()

    def update_product(self, product_id: int, data: Dict) -> Tuple[bool, str]:
        cur = self._cursor()
        try:
            cur.execute("""
                UPDATE products SET product_code=%s, name=%s, category_id=%s,
                cost_price=%s, sell_price=%s, quantity=%s, unit=%s, description=%s
                WHERE product_id=%s
            """, (
                data["product_code"], data["name"], data["category_id"],
                data["cost_price"], data["sell_price"], data["quantity"],
                data.get("unit", "pcs"), data.get("description", ""),
                product_id
            ))
            self._commit()
            return True, "Product updated."
        except Error as e:
            self._rollback()
            return False, str(e)
        finally:
            cur.close()

    def adjust_stock(self, product_id: int, amount: int) -> Tuple[bool, str]:
        """Add or subtract stock directly. Use positive to add, negative to subtract."""
        cur = self._cursor()
        try:
            cur.execute(
                "UPDATE products SET quantity = GREATEST(0, quantity + %s) WHERE product_id = %s",
                (amount, product_id)
            )
            self._commit()
            return True, "Stock adjusted."
        except Error as e:
            self._rollback()
            return False, str(e)
        finally:
            cur.close()

    def delete_product(self, product_id: int) -> Tuple[bool, str]:
        cur = self._cursor()
        try:
            cur.execute("DELETE FROM sale_items WHERE product_id = %s", (product_id,))
            cur.execute("DELETE FROM stock_purchases WHERE product_id = %s", (product_id,))
            cur.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
            self._commit()
            return True, "Product and its transaction history deleted."
        except Error as e:
            self._rollback()
            return False, str(e)
        finally:
            cur.close()

    # ------------------------------------------------------------------ #
    #  Sales                                                               #
    # ------------------------------------------------------------------ #
    def record_sale(self, items: List[Dict], total: float, discount: float, payment: str, notes: str = "") -> Tuple[bool, str]:
        """
        items: list of {product_id, quantity, unit_price, cost_price, subtotal}
        Deducts stock automatically.
        """
        cur = self._cursor()
        try:
            cur.execute("""
                INSERT INTO sales (total_amount, discount, payment_method, notes)
                VALUES (%s, %s, %s, %s)
            """, (total, discount, payment, notes))
            sale_id = cur.lastrowid

            for item in items:
                cur.execute("""
                    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, cost_price, subtotal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    sale_id, item["product_id"], item["quantity"],
                    item["unit_price"], item["cost_price"], item["subtotal"]
                ))
                cur.execute(
                    "UPDATE products SET quantity = quantity - %s WHERE product_id = %s",
                    (item["quantity"], item["product_id"])
                )

            self._commit()
            return True, f"Sale #{sale_id} recorded successfully."
        except Error as e:
            self._rollback()
            return False, str(e)
        finally:
            cur.close()

    def get_recent_sales(self, limit: int = 50) -> List[Dict]:
        cur = self._cursor()
        cur.execute("""
            SELECT s.*, COUNT(si.item_id) AS item_count
            FROM sales s
            LEFT JOIN sale_items si ON s.sale_id = si.sale_id
            GROUP BY s.sale_id
            ORDER BY s.sale_date DESC
            LIMIT %s
        """, (limit,))
        result = cur.fetchall()
        cur.close()
        return result

    def get_sale_details(self, sale_id: int) -> List[Dict]:
        cur = self._cursor()
        cur.execute("""
            SELECT si.*, p.name AS product_name, p.product_code
            FROM sale_items si
            JOIN products p ON si.product_id = p.product_id
            WHERE si.sale_id = %s
        """, (sale_id,))
        result = cur.fetchall()
        cur.close()
        return result

    # ------------------------------------------------------------------ #
    #  Stock Purchases                                                     #
    # ------------------------------------------------------------------ #
    def record_purchase(self, data: Dict) -> Tuple[bool, str]:
        cur = self._cursor()
        try:
            total = data["quantity"] * data["cost_per_unit"]
            has_date = "purchase_date" in data and data["purchase_date"]
            if has_date:
                cur.execute("""
                    INSERT INTO stock_purchases (product_id, quantity, cost_per_unit, total_cost, supplier, notes, purchase_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    data["product_id"], data["quantity"], data["cost_per_unit"],
                    total, data.get("supplier", ""), data.get("notes", ""),
                    data["purchase_date"]
                ))
            else:
                cur.execute("""
                    INSERT INTO stock_purchases (product_id, quantity, cost_per_unit, total_cost, supplier, notes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    data["product_id"], data["quantity"], data["cost_per_unit"],
                    total, data.get("supplier", ""), data.get("notes", "")
                ))
            cur.execute(
                """UPDATE products
                   SET quantity = quantity + %s,
                       cost_price = ROUND((cost_price * quantity + %s * %s) / (quantity + %s), 2)
                   WHERE product_id = %s""",
                (data["quantity"], data["cost_per_unit"], data["quantity"],
                 data["quantity"], data["product_id"])
            )
            self._commit()
            return True, "Stock purchase recorded."
        except Error as e:
            self._rollback()
            return False, str(e)
        finally:
            cur.close()

    def get_recent_purchases(self, limit: int = 50) -> List[Dict]:
        cur = self._cursor()
        cur.execute("""
            SELECT sp.*, p.name AS product_name, p.product_code
            FROM stock_purchases sp
            JOIN products p ON sp.product_id = p.product_id
            ORDER BY sp.purchase_date DESC LIMIT %s
        """, (limit,))
        result = cur.fetchall()
        cur.close()
        return result

    def get_purchase_by_id(self, purchase_id: int) -> Optional[Dict]:
        cur = self._cursor()
        cur.execute("""
            SELECT sp.*, p.name AS product_name, p.product_code
            FROM stock_purchases sp
            JOIN products p ON sp.product_id = p.product_id
            WHERE sp.purchase_id = %s
        """, (purchase_id,))
        result = cur.fetchone()
        cur.close()
        return result

    def update_purchase(self, purchase_id: int, data: Dict) -> Tuple[bool, str]:
        cur = self._cursor()
        try:
            old = self.get_purchase_by_id(purchase_id)
            if not old:
                return False, "Purchase not found."

            old_qty = old["quantity"]
            new_qty = data["quantity"]
            qty_diff = new_qty - old_qty

            cur.execute("""
                UPDATE stock_purchases
                SET quantity=%s, cost_per_unit=%s, total_cost=%s,
                    supplier=%s, notes=%s, purchase_date=%s
                WHERE purchase_id=%s
            """, (
                data["quantity"], data["cost_per_unit"], data["total_cost"],
                data.get("supplier", ""), data.get("notes", ""),
                data["purchase_date"], purchase_id
            ))
            cur.execute(
                "UPDATE products SET quantity = GREATEST(0, quantity + %s) WHERE product_id = %s",
                (qty_diff, data["product_id"])
            )
            self._commit()
            return True, "Purchase updated."
        except Error as e:
            self._rollback()
            return False, str(e)
        finally:
            cur.close()

    def delete_purchase(self, purchase_id: int) -> Tuple[bool, str]:
        cur = self._cursor()
        try:
            old = self.get_purchase_by_id(purchase_id)
            if not old:
                return False, "Purchase not found."
            cur.execute(
                "UPDATE products SET quantity = GREATEST(0, quantity - %s) WHERE product_id = %s",
                (old["quantity"], old["product_id"])
            )
            cur.execute("DELETE FROM stock_purchases WHERE purchase_id = %s", (purchase_id,))
            self._commit()
            return True, "Purchase deleted, stock reversed."
        except Error as e:
            self._rollback()
            return False, str(e)
        finally:
            cur.close()

    # ------------------------------------------------------------------ #
    #  Reports                                                             #
    # ------------------------------------------------------------------ #
    def get_daily_report(self) -> Dict:
        return self._period_report("DAY")

    def get_weekly_report(self) -> Dict:
        return self._period_report("WEEK")

    def get_monthly_report(self) -> Dict:
        return self._period_report("MONTH")

    def get_semiannual_report(self) -> Dict:
        return self._period_report("SEMI_ANNUAL")

    def get_annual_report(self) -> Dict:
        return self._period_report("ANNUAL")

    def _period_report(self, period: str) -> Dict:
        cur = self._cursor()

        if period == "DAY":
            date_cond  = "sale_date = CURDATE()"
            s_date_cond = "s.sale_date = CURDATE()"
            p_date_cond = "purchase_date = CURDATE()"
        elif period == "WEEK":
            date_cond  = "sale_date >= DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY) AND sale_date < DATE_ADD(DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY), INTERVAL 7 DAY)"
            s_date_cond = "s.sale_date >= DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY) AND s.sale_date < DATE_ADD(DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY), INTERVAL 7 DAY)"
            p_date_cond = "purchase_date >= DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY) AND purchase_date < DATE_ADD(DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY), INTERVAL 7 DAY)"
        elif period == "SEMI_ANNUAL":
            date_cond  = "sale_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)"
            s_date_cond = "s.sale_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)"
            p_date_cond = "purchase_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)"
        elif period == "ANNUAL":
            date_cond  = "sale_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)"
            s_date_cond = "s.sale_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)"
            p_date_cond = "purchase_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)"
        else:
            date_cond   = "YEAR(sale_date) = YEAR(CURDATE()) AND MONTH(sale_date) = MONTH(CURDATE())"
            s_date_cond = "YEAR(s.sale_date) = YEAR(CURDATE()) AND MONTH(s.sale_date) = MONTH(CURDATE())"
            p_date_cond = "YEAR(purchase_date) = YEAR(CURDATE()) AND MONTH(purchase_date) = MONTH(CURDATE())"

        # Income (sales)
        cur.execute(f"""
            SELECT
                COALESCE(SUM(total_amount), 0) AS total_income,
                COALESCE(SUM(discount), 0)      AS total_discount,
                COUNT(*)                         AS total_transactions
            FROM sales WHERE {date_cond}
        """)
        income_row = cur.fetchone()

        # Cost of goods sold
        cur.execute(f"""
            SELECT COALESCE(SUM(si.cost_price * si.quantity), 0) AS cogs
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.sale_id
            WHERE {s_date_cond}
        """)
        cogs_row = cur.fetchone()

        # Expenditure (stock purchases)
        cur.execute(f"""
            SELECT COALESCE(SUM(total_cost), 0) AS total_expenditure
            FROM stock_purchases WHERE {p_date_cond}
        """)
        exp_row = cur.fetchone()

        # Top 5 products
        cur.execute(f"""
            SELECT p.name, SUM(si.quantity) AS qty_sold, SUM(si.subtotal) AS revenue
            FROM sale_items si
            JOIN products p ON si.product_id = p.product_id
            JOIN sales s ON si.sale_id = s.sale_id
            WHERE {s_date_cond}
            GROUP BY p.product_id ORDER BY revenue DESC LIMIT 5
        """)
        top_products = cur.fetchall()

        # Daily breakdown
        cur.execute(f"""
            SELECT DATE(sale_date) AS day, SUM(total_amount) AS income, COUNT(*) AS txns
            FROM sales WHERE {date_cond}
            GROUP BY DATE(sale_date) ORDER BY day
        """)
        daily = cur.fetchall()

        cur.close()

        income = float(income_row["total_income"])
        cogs = float(cogs_row["cogs"])
        expenditure = float(exp_row["total_expenditure"])
        gross_profit = income - cogs

        return {
            "period": period,
            "total_income": income,
            "total_discount": float(income_row["total_discount"]),
            "total_transactions": int(income_row["total_transactions"]),
            "cogs": cogs,
            "gross_profit": gross_profit,
            "total_expenditure": expenditure,
            "net_profit": gross_profit,
            "top_products": top_products,
            "daily_breakdown": daily,
        }

    def get_income_report(self) -> Dict:
        cur = self._cursor()

        cur.execute("""
            SELECT
                COALESCE(SUM(total_amount), 0) AS total_income,
                COALESCE(SUM(discount), 0)      AS total_discount,
                COUNT(*)                         AS total_transactions
            FROM sales
        """)
        income_row = cur.fetchone()

        cur.execute("""
            SELECT COALESCE(SUM(si.cost_price * si.quantity), 0) AS cogs
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.sale_id
        """)
        cogs_row = cur.fetchone()

        cur.execute("""
            SELECT DATE(sale_date) AS day, SUM(total_amount) AS income, COUNT(*) AS txns
            FROM sales
            GROUP BY DATE(sale_date) ORDER BY day DESC LIMIT 30
        """)
        daily = cur.fetchall()

        cur.execute("""
            SELECT p.name, SUM(si.quantity) AS qty_sold, SUM(si.subtotal) AS revenue
            FROM sale_items si
            JOIN products p ON si.product_id = p.product_id
            JOIN sales s ON si.sale_id = s.sale_id
            GROUP BY p.product_id ORDER BY revenue DESC LIMIT 5
        """)
        top_products = cur.fetchall()

        cur.execute("""
            SELECT payment_method, COUNT(*) AS count, SUM(total_amount) AS total
            FROM sales
            GROUP BY payment_method
        """)
        payment_breakdown = cur.fetchall()

        cur.close()

        income = float(income_row["total_income"])
        cogs = float(cogs_row["cogs"])
        gross_profit = income - cogs

        return {
            "total_income": income,
            "total_discount": float(income_row["total_discount"]),
            "total_transactions": int(income_row["total_transactions"]),
            "cogs": cogs,
            "gross_profit": gross_profit,
            "daily_breakdown": daily,
            "top_products": top_products,
            "payment_breakdown": payment_breakdown,
        }

    def get_expense_report(self) -> Dict:
        cur = self._cursor()

        cur.execute("""
            SELECT COALESCE(SUM(total_cost), 0) AS total_expenditure,
                   COUNT(*) AS total_purchases
            FROM stock_purchases
        """)
        exp_row = cur.fetchone()

        cur.execute("""
            SELECT DATE(purchase_date) AS day, SUM(total_cost) AS amount, COUNT(*) AS count
            FROM stock_purchases
            GROUP BY DATE(purchase_date) ORDER BY day DESC LIMIT 30
        """)
        daily = cur.fetchall()

        cur.execute("""
            SELECT p.name, sp.supplier, SUM(sp.quantity) AS qty_purchased,
                   SUM(sp.total_cost) AS total_spent
            FROM stock_purchases sp
            JOIN products p ON sp.product_id = p.product_id
            GROUP BY p.product_id, p.name, sp.supplier ORDER BY total_spent DESC LIMIT 5
        """)
        top_purchases = cur.fetchall()

        cur.execute("""
            SELECT COALESCE(supplier, 'Unknown') AS supplier,
                   SUM(total_cost) AS total, COUNT(*) AS count
            FROM stock_purchases
            GROUP BY COALESCE(supplier, 'Unknown') ORDER BY total DESC
        """)
        supplier_breakdown = cur.fetchall()

        cur.execute("""
            SELECT c.name AS category, SUM(sp.total_cost) AS total
            FROM stock_purchases sp
            JOIN products p ON sp.product_id = p.product_id
            JOIN categories c ON p.category_id = c.category_id
            GROUP BY c.category_id ORDER BY total DESC
        """)
        category_breakdown = cur.fetchall()

        cur.close()

        return {
            "total_expenditure": float(exp_row["total_expenditure"]),
            "total_purchases": int(exp_row["total_purchases"]),
            "daily_breakdown": daily,
            "top_purchases": top_purchases,
            "supplier_breakdown": supplier_breakdown,
            "category_breakdown": category_breakdown,
        }

    def get_low_stock_products(self, threshold: int = 10) -> List[Dict]:
        cur = self._cursor()
        cur.execute("""
            SELECT p.*, c.name AS category_name
            FROM products p JOIN categories c ON p.category_id = c.category_id
            WHERE p.quantity <= %s ORDER BY p.quantity ASC
        """, (threshold,))
        result = cur.fetchall()
        cur.close()
        return result
