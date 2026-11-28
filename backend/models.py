from datetime import date
from sqlalchemy import CheckConstraint, Date, ForeignKey, ForeignKeyConstraint, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))

class Category(Base):
    __tablename__ = 'categories'
    __table_args__ = (
        CheckConstraint("kind IN ('income', 'expense')"),
        UniqueConstraint('user_id', 'name', 'kind'),
        UniqueConstraint('id', 'user_id', 'kind'),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    name: Mapped[str] = mapped_column(String(80))
    kind: Mapped[str] = mapped_column(String(7))

class Transaction(Base):
    __tablename__ = 'transactions'
    __table_args__ = (
        CheckConstraint('amount_cents > 0'),
        ForeignKeyConstraint(['category_id', 'user_id', 'kind'], ['categories.id', 'categories.user_id', 'categories.kind']),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    category_id: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String(7))
    amount_cents: Mapped[int] = mapped_column(Integer)
    transaction_date: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(String(255), default='')

class Budget(Base):
    __tablename__ = 'budgets'
    __table_args__ = (
        CheckConstraint('limit_cents > 0'),
        CheckConstraint("kind = 'expense'"),
        CheckConstraint("strftime('%d', month) = '01'"),
        UniqueConstraint('user_id', 'category_id', 'month'),
        ForeignKeyConstraint(['category_id', 'user_id', 'kind'], ['categories.id', 'categories.user_id', 'categories.kind']),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    category_id: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String(7), default='expense')
    month: Mapped[date] = mapped_column(Date)
    limit_cents: Mapped[int] = mapped_column(Integer)

class AuthSession(Base):
    __tablename__ = 'auth_sessions'
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    expires_at: Mapped[int] = mapped_column(Integer, index=True)
