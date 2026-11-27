from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect
from .database import engine, init_db

@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app = FastAPI(title='FinTrack', version='0.2.0', lifespan=lifespan)
frontend = Path(__file__).resolve().parent.parent / 'frontend'
app.mount('/static', StaticFiles(directory=frontend), name='static')

@app.get('/', include_in_schema=False)
def home():
    return FileResponse(frontend / 'index.html')

@app.get('/api/health')
def health():
    return {'status': 'ok', 'application': 'FinTrack'}

@app.get('/api/database/health')
def database_health():
    tables = sorted(inspect(engine).get_table_names())
    expected = {'users', 'categories', 'transactions', 'budgets'}
    return {'status': 'ok' if expected.issubset(tables) else 'incomplete', 'tables': tables}
