from datetime import date
from typing import Literal

from pydantic import BaseModel, field_validator

CATEGORIES = {
    "sales", "other_income", "rent", "payroll", "supplies", "inventory",
    "utilities", "loan_payment", "insurance", "marketing", "fees",
    "taxes", "equipment", "other",
}


class Transaction(BaseModel):
    date: date
    type: Literal["sale", "expense"]
    category: str
    amount: float
    note: str = ""
    recurring: Literal["yes", "no"] = "no"

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value):
        if value < 0:                       
            raise ValueError("amount must be positive")
        return value

    @field_validator("category")
    @classmethod
    def unknown_category_becomes_other(cls, value):
        return value if value in CATEGORIES else "other"