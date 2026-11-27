# FinTrack

A personal finance management web application, currently in development.

## Current features
- Financial dashboard preview and FastAPI health endpoint.
- SQLite database with SQLAlchemy models for users, categories, transactions and budgets.
- Read-only REST API for demo categories, transactions and financial summaries.
- Automated backend, database and API tests.

Transaction entry, real user authentication and dashboard integration are not implemented yet. The API is for local development only; do not expose it publicly before authentication is implemented.

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

## REST API
Visit `/docs` to try the endpoints.

- `GET /api/categories` — optional `kind` filter.
- `GET /api/transactions` — optional `kind`, `limit`, `offset`.
- `GET /api/summary` — all-time income, expenses, balance and count in integer cents.

These endpoints read only the reserved fictional demo account. With no demo data, they return empty lists and zero totals. To insert optional fictional data locally, run:

```powershell
python -m backend.seed_demo
```

The seed is repeat-safe and does not create a usable login. It does not modify other accounts.
