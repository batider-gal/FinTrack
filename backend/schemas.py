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

from pydantic import Field, model_validator
from typing import Annotated

Cents = Annotated[int, Field(strict=True, gt=0, le=1_000_000_000_000)]
CategoryId = Annotated[int, Field(strict=True, gt=0, le=2**63-1)]
Description = Annotated[str, Field(max_length=255)]

class TransactionCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    category_id: CategoryId
    kind: Kind
    amount_cents: Cents
    transaction_date: date
    description: Description = ''

class TransactionUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    category_id: CategoryId | None = None
    kind: Kind | None = None
    amount_cents: Cents | None = None
    transaction_date: date | None = None
    description: Description | None = None

    @model_validator(mode='after')
    def validate_patch(self):
        if not self.model_fields_set or any(getattr(self, f) is None for f in self.model_fields_set):
            raise ValueError('Provide at least one field; null values are not supported')
        return self
