# FinTrack

A personal finance management web application in development, built with Python, FastAPI, SQLAlchemy, SQLite, HTML, CSS and JavaScript.

## Features
- User registration, Argon2 password hashing, JWT bearer authentication and revocable sessions.
- Account-specific categories, transaction CRUD and financial summaries.
- Integer-cent monetary amounts and input validation.
- Interactive dashboard, browser registration and login, transaction management, interactive API documentation and automated tests.

## Setup (Windows PowerShell)
From the project root:
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```
Open http://127.0.0.1:8000/docs for API documentation. Startup creates the new auth_sessions table without deleting existing data. The original demo account remains disabled; new accounts have six default categories and no transactions.

## Authentication
In Swagger, execute POST /api/auth/register and then POST /api/auth/login with the same JSON body, for example:
```json
{"email":"student@example.com","password":"FinTrackTest123!"}
```
Use fictional credentials for local testing. Copy the access_token value (without quotes), click Authorize, paste the token without a Bearer prefix, and confirm. GET /api/auth/me returns your account. POST /api/auth/logout revokes the current token; Swagger's Authorize dialog can also clear its local token.

## REST API
- Public: GET /api/health, GET /api/database/health, POST /api/auth/register, POST /api/auth/login.
- Protected: GET /api/auth/me, POST /api/auth/logout, GET /api/categories, GET /api/summary, GET and POST /api/transactions, GET/PATCH/DELETE /api/transactions/{transaction_id}.
- Use GET /api/categories to find a category ID belonging to your account. Example create body (replace category_id with your expense category ID):
```json
{"category_id":3,"kind":"expense","amount_cents":1500,"transaction_date":"2026-11-27","description":"Sample lunch"}
```
- PATCH accepts a nonempty subset of create fields; amounts are positive integer cents. Unauthorized requests return 401; other accounts' transactions return 404.

## Tests
```powershell
python -m pytest
```

## Development limitations
Local demonstration only. JWTs expire after one hour and the signing key is randomly generated at process startup; restarting or reloading requires a new login. No multi-worker support, rate limiting, verified email, password reset or production HTTPS configuration yet. Do not expose this version publicly or use actual financial information. The browser stores its access token in memory only; refreshing the page requires login again. Monthly charts and budgets are not yet implemented.

## Browser interface
Open http://127.0.0.1:8000/ and create an account with a fictional email and password of at least 12 characters. Sign in, add an income or expense, edit or delete it, and verify the totals update. The transaction list is paginated. Sign out when finished. Refreshing the page clears the in-memory token; use Sign out to revoke the server session before leaving.
