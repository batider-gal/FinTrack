from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_PATH = Path(__file__).resolve().parent.parent / 'fintrack.db'

class Base(DeclarativeBase):
    pass

def make_engine(url):
    engine = create_engine(url, connect_args={'check_same_thread': False})
    @event.listens_for(engine, 'connect')
    def enable_foreign_keys(connection, _):
        connection.execute('PRAGMA foreign_keys = ON')
    return engine

engine = make_engine(f'sqlite:///{DATABASE_PATH.as_posix()}')
SessionLocal = sessionmaker(bind=engine)

def init_db():
    from . import models
    Base.metadata.create_all(bind=engine)
