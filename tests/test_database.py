from datetime import date
import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from backend.database import Base, make_engine
from backend.models import User, Category, Transaction, Budget

@pytest.fixture
def db(tmp_path):
    engine = make_engine(f'sqlite:///{(tmp_path / "test.db").as_posix()}')
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()

def setup_category(db):
    user = User(email='test@example.com', password_hash='test-placeholder-not-a-real-password')
    db.add(user)
    db.flush()
    category = Category(user_id=user.id, name='Food', kind='expense')
    db.add(category)
    db.flush()
    return user.id, category.id

def test_tables(db):
    assert set(inspect(db.bind).get_table_names()) == {'users', 'categories', 'transactions', 'budgets'}

def test_save_transaction_and_budget(db):
    uid, cid = setup_category(db)
    db.add(Transaction(user_id=uid, category_id=cid, kind='expense', amount_cents=1250, transaction_date=date(2026, 11, 26)))
    db.add(Budget(user_id=uid, category_id=cid, month=date(2026, 11, 1), limit_cents=20000))
    db.commit()
    assert db.query(Transaction).one().amount_cents == 1250
    assert db.query(Budget).one().limit_cents == 20000

@pytest.mark.parametrize('amount,kind', [(0,'expense'),(-1,'expense'),(100,'income')])
def test_invalid_transaction(db, amount, kind):
    uid, cid = setup_category(db)
    db.add(Transaction(user_id=uid, category_id=cid, kind=kind, amount_cents=amount, transaction_date=date(2026, 11, 26)))
    with pytest.raises(IntegrityError):
        db.commit()

def test_cross_user_category_rejected(db):
    uid, cid = setup_category(db)
    other = User(email='other@example.com', password_hash='test-placeholder')
    db.add(other)
    db.flush()
    db.add(Transaction(user_id=other.id, category_id=cid, kind='expense', amount_cents=100, transaction_date=date(2026, 11, 26)))
    with pytest.raises(IntegrityError):
        db.commit()
