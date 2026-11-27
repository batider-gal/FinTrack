"""Optional fictional local demo data. Run: python -m backend.seed_demo"""
from datetime import date
from sqlalchemy import select
from .api import DEMO_EMAIL
from .database import SessionLocal, init_db
from .models import User, Category, Transaction

def seed_demo():
    init_db()
    with SessionLocal() as db:
        if db.scalar(select(User.id).where(User.email == DEMO_EMAIL)) is not None:
            print('Demo account already exists; no changes made.')
            return
        user = User(email=DEMO_EMAIL, password_hash='!disabled-demo-account')
        db.add(user)
        db.flush()
        salary = Category(user_id=user.id, name='Salary', kind='income')
        food = Category(user_id=user.id, name='Food', kind='expense')
        db.add_all([salary, food])
        db.flush()
        db.add_all([
            Transaction(user_id=user.id, category_id=salary.id, kind='income', amount_cents=200000, transaction_date=date.today(), description='Sample salary'),
            Transaction(user_id=user.id, category_id=food.id, kind='expense', amount_cents=4500, transaction_date=date.today(), description='Sample groceries'),
        ])
        db.commit()
        print('Fictional demo data created.')

if __name__ == '__main__':
    seed_demo()
