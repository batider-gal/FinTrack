from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict

Kind = Literal['income', 'expense']

class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    kind: Kind

class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: int
    kind: Kind
    amount_cents: int
    transaction_date: date
    description: str

class SummaryRead(BaseModel):
    income_cents: int
    expense_cents: int
    balance_cents: int
    transaction_count: int
