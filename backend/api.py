from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, case
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User, Category, Transaction
from .schemas import CategoryRead, TransactionRead, SummaryRead, Kind

# Temporary local demonstration scope; not an authentication mechanism.
DEMO_EMAIL = 'demo@fintrack.invalid'
router = APIRouter(prefix='/api')

def get_db():
    with SessionLocal() as db:
        yield db

DB = Annotated[Session, Depends(get_db)]

def demo_user_id(db):
    return db.scalar(select(User.id).where(User.email == DEMO_EMAIL))

@router.get('/categories', response_model=list[CategoryRead], tags=['Categories'])
def categories(db: DB, kind: Kind | None = None):
    uid = demo_user_id(db)
    if uid is None:
        return []
    stmt = select(Category).where(Category.user_id == uid)
    if kind is not None:
        stmt = stmt.where(Category.kind == kind)
    return db.scalars(stmt.order_by(Category.name, Category.id)).all()

@router.get('/transactions', response_model=list[TransactionRead], tags=['Transactions'])
def transactions(db: DB, kind: Kind | None = None,
                 limit: Annotated[int, Query(ge=1, le=100)] = 50,
                 offset: Annotated[int, Query(ge=0)] = 0):
    uid = demo_user_id(db)
    if uid is None:
        return []
    stmt = select(Transaction).where(Transaction.user_id == uid)
    if kind is not None:
        stmt = stmt.where(Transaction.kind == kind)
    return db.scalars(stmt.order_by(Transaction.transaction_date.desc(), Transaction.id.desc()).offset(offset).limit(limit)).all()

@router.get('/summary', response_model=SummaryRead, tags=['Summary'])
def summary(db: DB):
    uid = demo_user_id(db)
    if uid is None:
        return SummaryRead(income_cents=0, expense_cents=0, balance_cents=0, transaction_count=0)
    income, expense, count = db.execute(select(
        func.coalesce(func.sum(case((Transaction.kind == 'income', Transaction.amount_cents), else_=0)), 0),
        func.coalesce(func.sum(case((Transaction.kind == 'expense', Transaction.amount_cents), else_=0)), 0),
        func.count(Transaction.id),
    ).where(Transaction.user_id == uid)).one()
    return SummaryRead(income_cents=income, expense_cents=expense, balance_cents=income-expense, transaction_count=count)
