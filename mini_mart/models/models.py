"""
Models and Interfaces for Mini Mart Management System.
Pure-Python dataclasses / ABCs - no GUI or DB dependencies.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


# ------------------------------------------------------------------ #
#  Interfaces (Abstract Base Classes)                                 #
# ------------------------------------------------------------------ #

class IProduct(ABC):
    @abstractmethod
    def get_id(self) -> int: ...
    @abstractmethod
    def get_code(self) -> str: ...
    @abstractmethod
    def get_name(self) -> str: ...
    @abstractmethod
    def is_low_stock(self, threshold: int = 10) -> bool: ...


class ISaleable(ABC):
    @abstractmethod
    def calculate_subtotal(self, quantity: int) -> float: ...
    @abstractmethod
    def get_profit_margin(self) -> float: ...


class IReport(ABC):
    @abstractmethod
    def generate(self) -> dict: ...
    @abstractmethod
    def get_title(self) -> str: ...


# ------------------------------------------------------------------ #
#  Concrete Data Classes                                              #
# ------------------------------------------------------------------ #

@dataclass
class Category:
    category_id: int
    name: str
    description: str = ""
    created_at: Optional[datetime] = None

    def __str__(self):
        return self.name


@dataclass
class Product(IProduct, ISaleable):
    product_id: int
    product_code: str
    name: str
    category_id: int
    cost_price: float
    sell_price: float
    quantity: int
    unit: str = "pcs"
    description: str = ""
    category_name: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # IProduct
    def get_id(self) -> int: return self.product_id
    def get_code(self) -> str: return self.product_code
    def get_name(self) -> str: return self.name
    def is_low_stock(self, threshold: int = 10) -> bool:
        return self.quantity <= threshold

    def add_stock(self, amount: int):
        self.quantity += amount

    def remove_stock(self, amount: int):
        self.quantity = max(0, self.quantity - amount)

    # ISaleable
    def calculate_subtotal(self, quantity: int) -> float:
        return round(self.sell_price * quantity, 2)

    def get_profit_margin(self) -> float:
        if self.sell_price == 0:
            return 0.0
        return round((self.sell_price - self.cost_price) / self.sell_price * 100, 2)

    @classmethod
    def from_dict(cls, d: dict) -> "Product":
        return cls(
            product_id=d.get("product_id", 0),
            product_code=d.get("product_code", ""),
            name=d.get("name", ""),
            category_id=d.get("category_id", 0),
            cost_price=float(d.get("cost_price", 0)),
            sell_price=float(d.get("sell_price", 0)),
            quantity=int(d.get("quantity", 0)),
            unit=d.get("unit", "pcs"),
            description=d.get("description", ""),
            category_name=d.get("category_name", ""),
            created_at=d.get("created_at"),
            updated_at=d.get("updated_at"),
        )


@dataclass
class SaleItem:
    product_id: int
    product_name: str
    product_code: str
    quantity: int
    unit_price: float
    cost_price: float

    @property
    def subtotal(self) -> float:
        return round(self.unit_price * self.quantity, 2)

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "cost_price": self.cost_price,
            "subtotal": self.subtotal,
        }


@dataclass
class Sale:
    items: List[SaleItem] = field(default_factory=list)
    discount: float = 0.0
    payment_method: str = "Cash"
    notes: str = ""

    @property
    def subtotal(self) -> float:
        return round(sum(i.subtotal for i in self.items), 2)

    @property
    def total(self) -> float:
        return round(max(0.0, self.subtotal - self.discount), 2)

    def add_item(self, item: SaleItem):
        # Merge if same product
        for existing in self.items:
            if existing.product_id == item.product_id:
                existing.quantity += item.quantity
                return
        self.items.append(item)

    def remove_item(self, product_id: int):
        self.items = [i for i in self.items if i.product_id != product_id]

    def clear(self):
        self.items.clear()
        self.discount = 0.0


@dataclass
class StockPurchase:
    product_id: int
    quantity: int
    cost_per_unit: float
    supplier: str = ""
    notes: str = ""
    purchase_date: Optional[datetime] = None

    @property
    def total_cost(self) -> float:
        return round(self.cost_per_unit * self.quantity, 2)

    def to_dict(self) -> dict:
        d = {
            "product_id": self.product_id,
            "quantity": self.quantity,
            "cost_per_unit": self.cost_per_unit,
            "supplier": self.supplier,
            "notes": self.notes,
        }
        if self.purchase_date:
            d["purchase_date"] = self.purchase_date
        return d


# ------------------------------------------------------------------ #
#  Report Implementations                                             #
# ------------------------------------------------------------------ #

class DailyReport(IReport):
    def __init__(self, db_manager):
        self._db = db_manager

    def get_title(self) -> str:
        return f"Daily Report — {datetime.now().strftime('%A, %B %d, %Y')}"

    def generate(self) -> dict:
        return self._db.get_daily_report()


class WeeklyReport(IReport):
    def __init__(self, db_manager):
        self._db = db_manager

    def get_title(self) -> str:
        return f"Weekly Report — Week of {datetime.now().strftime('%b %d, %Y')}"

    def generate(self) -> dict:
        return self._db.get_weekly_report()


class MonthlyReport(IReport):
    def __init__(self, db_manager):
        self._db = db_manager

    def get_title(self) -> str:
        return f"Monthly Report — {datetime.now().strftime('%B %Y')}"

    def generate(self) -> dict:
        return self._db.get_monthly_report()


class SemiAnnualReport(IReport):
    def __init__(self, db_manager):
        self._db = db_manager

    def get_title(self) -> str:
        now = datetime.now()
        return f"Semi-Annual Report — {now.strftime('%b %Y')} back 6 months"

    def generate(self) -> dict:
        return self._db.get_semiannual_report()


class AnnualReport(IReport):
    def __init__(self, db_manager):
        self._db = db_manager

    def get_title(self) -> str:
        now = datetime.now()
        return f"Annual Report — {now.strftime('%b %Y')} back 12 months"

    def generate(self) -> dict:
        return self._db.get_annual_report()


class IncomeReport(IReport):
    def __init__(self, db_manager):
        self._db = db_manager

    def get_title(self) -> str:
        return f"Income Report — {datetime.now().strftime('%B %d, %Y')}"

    def generate(self) -> dict:
        return self._db.get_income_report()


class ExpenseReport(IReport):
    def __init__(self, db_manager):
        self._db = db_manager

    def get_title(self) -> str:
        return f"Expense Report — {datetime.now().strftime('%B %d, %Y')}"

    def generate(self) -> dict:
        return self._db.get_expense_report()
