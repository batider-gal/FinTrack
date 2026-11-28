from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, case
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User, Category, Transaction
from .schemas import CategoryRead, TransactionRead, SummaryRead, Kind

from .auth import DB, CurrentUser, get_db, DEMO_EMAIL
router = APIRouter(prefix='/api')

@router.get('/categories', response_model=list[CategoryRead], tags=['Categories'])
def categories(db: DB, uid: CurrentUser, kind: Kind | None = None):
    stmt = select(Category).where(Category.user_id == uid)
    if kind is not None:
        stmt = stmt.where(Category.kind == kind)
    return db.scalars(stmt.order_by(Category.name, Category.id)).all()

@router.get('/transactions', response_model=list[TransactionRead], tags=['Transactions'])
def transactions(db: DB, uid: CurrentUser, kind: Kind | None = None,
                 limit: Annotated[int, Query(ge=1, le=100)] = 50,
                 offset: Annotated[int, Query(ge=0)] = 0):
    stmt = select(Transaction).where(Transaction.user_id == uid)
    if kind is not None:
        stmt = stmt.where(Transaction.kind == kind)
    return db.scalars(stmt.order_by(Transaction.transaction_date.desc(), Transaction.id.desc()).offset(offset).limit(limit)).all()

@router.get('/summary', response_model=SummaryRead, tags=['Summary'])
def summary(db: DB, uid: CurrentUser):
    income, expense, count = db.execute(select(
        func.coalesce(func.sum(case((Transaction.kind == 'income', Transaction.amount_cents), else_=0)), 0),
        func.coalesce(func.sum(case((Transaction.kind == 'expense', Transaction.amount_cents), else_=0)), 0),
        func.count(Transaction.id),
    ).where(Transaction.user_id == uid)).one()
    return SummaryRead(income_cents=income, expense_cents=expense, balance_cents=income-expense, transaction_count=count)

from fastapi import HTTPException, Response, Path
from sqlalchemy.exc import IntegrityError
from .schemas import TransactionCreate, TransactionUpdate

TransactionId = Annotated[int, Path(gt=0, le=2**63-1)]

def find_transaction(db, uid, transaction_id):
    row = db.scalar(select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == uid))
    if row is None:
        raise HTTPException(404, 'Transaction not found')
    return row

def check_category(db, uid, category_id, kind):
    category = db.scalar(select(Category).where(Category.id == category_id, Category.user_id == uid, Category.kind == kind))
    if category is None:
        raise HTTPException(422, 'Category must belong to the current account and match transaction kind')

def save_changes(db):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Transaction conflicts with database constraints') from None

@router.post('/transactions', response_model=TransactionRead, status_code=201, tags=['Transactions'])
def create_transaction(payload: TransactionCreate, db: DB, uid: CurrentUser):
    check_category(db, uid, payload.category_id, payload.kind)
    row = Transaction(user_id=uid, **payload.model_dump())
    db.add(row)
    save_changes(db)
    db.refresh(row)
    return row

@router.get('/transactions/{transaction_id}', response_model=TransactionRead, tags=['Transactions'])
def read_transaction(transaction_id: TransactionId, db: DB, uid: CurrentUser):
    return find_transaction(db, uid, transaction_id)

@router.patch('/transactions/{transaction_id}', response_model=TransactionRead, tags=['Transactions'])
def update_transaction(transaction_id: TransactionId, payload: TransactionUpdate, db: DB, uid: CurrentUser):
    row = find_transaction(db, uid, transaction_id)
    changes = payload.model_dump(exclude_unset=True)
    check_category(db, uid, changes.get('category_id', row.category_id), changes.get('kind', row.kind))
    for key, value in changes.items():
        setattr(row, key, value)
    save_changes(db)
    db.refresh(row)
    return row

@router.delete('/transactions/{transaction_id}', status_code=204, tags=['Transactions'])
def delete_transaction(transaction_id: TransactionId, db: DB, uid: CurrentUser):
    row = find_transaction(db, uid, transaction_id)
    db.delete(row)
    save_changes(db)
    return Response(status_code=204)
