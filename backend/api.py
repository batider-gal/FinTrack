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

from fastapi import HTTPException, Response, Path
from sqlalchemy.exc import IntegrityError
from .schemas import TransactionCreate, TransactionUpdate

TransactionId = Annotated[int, Path(gt=0, le=2**63-1)]

def require_demo_user(db):
    uid = demo_user_id(db)
    if uid is None:
        raise HTTPException(409, 'Demo account missing. Run python -m backend.seed_demo')
    return uid

def find_transaction(db, uid, transaction_id):
    row = db.scalar(select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == uid))
    if row is None:
        raise HTTPException(404, 'Transaction not found')
    return row

def check_category(db, uid, category_id, kind):
    category = db.scalar(select(Category).where(Category.id == category_id, Category.user_id == uid, Category.kind == kind))
    if category is None:
        raise HTTPException(422, 'Category must belong to the demo account and match transaction kind')

def save_changes(db):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Transaction conflicts with database constraints') from None

@router.post('/transactions', response_model=TransactionRead, status_code=201, tags=['Transactions'])
def create_transaction(payload: TransactionCreate, db: DB):
    uid = require_demo_user(db)
    check_category(db, uid, payload.category_id, payload.kind)
    row = Transaction(user_id=uid, **payload.model_dump())
    db.add(row)
    save_changes(db)
    db.refresh(row)
    return row

@router.get('/transactions/{transaction_id}', response_model=TransactionRead, tags=['Transactions'])
def read_transaction(transaction_id: TransactionId, db: DB):
    return find_transaction(db, require_demo_user(db), transaction_id)

@router.patch('/transactions/{transaction_id}', response_model=TransactionRead, tags=['Transactions'])
def update_transaction(transaction_id: TransactionId, payload: TransactionUpdate, db: DB):
    uid = require_demo_user(db)
    row = find_transaction(db, uid, transaction_id)
    changes = payload.model_dump(exclude_unset=True)
    check_category(db, uid, changes.get('category_id', row.category_id), changes.get('kind', row.kind))
    for key, value in changes.items():
        setattr(row, key, value)
    save_changes(db)
    db.refresh(row)
    return row

@router.delete('/transactions/{transaction_id}', status_code=204, tags=['Transactions'])
def delete_transaction(transaction_id: TransactionId, db: DB):
    row = find_transaction(db, require_demo_user(db), transaction_id)
    db.delete(row)
    save_changes(db)
    return Response(status_code=204)
