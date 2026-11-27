# FinTrack

A personal finance management web application, currently in development.

## Current features
- Financial dashboard preview and FastAPI health endpoint.
- SQLite database with SQLAlchemy models for users, categories, transactions and budgets.
- REST API for demo categories, transaction CRUD and financial summaries.
- Automated backend, database and API tests.

Transaction entry is supported through the API. Real user authentication and dashboard integration are not implemented yet. The API is for local development only; do not expose it publicly before authentication is implemented.

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

These endpoints operate only on the reserved fictional demo account. With no demo data, list and summary endpoints return empty lists and zero totals; individual transaction operations require the demo account. To insert optional fictional data locally, run:

```powershell
python -m backend.seed_demo
```

The seed is repeat-safe and does not create a usable login. It does not modify other accounts.

## Transaction management
- `POST /api/transactions` — create a transaction (201).
- `GET /api/transactions/{transaction_id}` — retrieve one transaction.
- `PATCH /api/transactions/{transaction_id}` — update supplied fields.
- `DELETE /api/transactions/{transaction_id}` — delete a transaction (204).

Use `/api/categories` to find a category ID. The category must match the transaction kind. Example POST body (replace category_id with an existing expense category ID):

```json
{"category_id": 2, "kind": "expense", "amount_cents": 1500, "transaction_date": "2026-11-26", "description": "Sample lunch"}
```

Amounts must be positive integer cents. PATCH accepts any nonempty subset of the create fields, without null values. Invalid input returns 422; missing transactions return 404; missing demo account returns 409. All changes persist in SQLite. This is not an authenticated API: use fictional data on localhost only.
