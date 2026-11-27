from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.api import DEMO_EMAIL, get_db
from backend.database import Base, make_engine
from backend.main import app
from backend.models import User, Category, Transaction

@pytest.fixture
def api(tmp_path):
    engine = make_engine(f'sqlite:///{(tmp_path / "api.db").as_posix()}')
    Base.metadata.create_all(engine)
    def override():
        with Session(engine) as db:
            yield db
    app.dependency_overrides[get_db] = override
    try:
        yield TestClient(app), engine
    finally:
        app.dependency_overrides.pop(get_db, None)
        engine.dispose()

@pytest.fixture
def populated(api):
    client, engine = api
    with Session(engine) as db:
        for email, amount in [(DEMO_EMAIL, 10000), ('other@example.com', 99999)]:
            user = User(email=email, password_hash='!test')
            db.add(user)
            db.flush()
            for kind, name, cents in [('income', 'Salary', amount), ('expense', 'Food', 2500)]:
                category = Category(user_id=user.id, kind=kind, name=name)
                db.add(category)
                db.flush()
                db.add(Transaction(user_id=user.id, category_id=category.id, kind=kind, amount_cents=cents, transaction_date=date(2026, 11, 26)))
        db.commit()
    return client

def test_empty(api):
    client, _ = api
    assert client.get('/api/categories').json() == []
    assert client.get('/api/transactions').json() == []
    assert client.get('/api/summary').json() == dict(income_cents=0, expense_cents=0, balance_cents=0, transaction_count=0)

def test_categories(populated):
    assert len(populated.get('/api/categories').json()) == 2
    assert [c['name'] for c in populated.get('/api/categories?kind=expense').json()] == ['Food']

def test_transactions(populated):
    rows = populated.get('/api/transactions').json()
    assert len(rows) == 2
    assert {r['amount_cents'] for r in rows} == {10000, 2500}
    assert populated.get('/api/transactions?kind=income').json()[0]['amount_cents'] == 10000
    assert len(populated.get('/api/transactions?limit=1&offset=1').json()) == 1

def test_summary(populated):
    assert populated.get('/api/summary').json() == dict(income_cents=10000, expense_cents=2500, balance_cents=7500, transaction_count=2)

@pytest.mark.parametrize('query', ['kind=invalid', 'limit=0', 'limit=101', 'offset=-1'])
def test_validation(populated, query):
    assert populated.get('/api/transactions?' + query).status_code == 422
