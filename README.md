# FinTrack

A personal finance management web application, currently in development.

## Current features
- Financial dashboard preview and FastAPI health endpoint.
- SQLite database with SQLAlchemy models for users, categories, transactions and budgets.
- Automated backend and database tests.

Transaction entry, authentication and financial reports are not implemented yet.

## Setup (Windows PowerShell)
Run from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000/ for the dashboard or /docs for API documentation.
The server creates `fintrack.db` on startup. Verify tables at `/api/database/health`.
Amounts are stored as integer cents to avoid floating-point rounding errors.

## Tests
```powershell
.\.venv\Scripts\python.exe -m pytest
```
