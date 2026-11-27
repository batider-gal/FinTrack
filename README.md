# FinTrack
A personal finance management web application, currently in development.

## Setup (Windows PowerShell)
Run from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000/ for the dashboard or /docs for API documentation.

## Tests
```powershell
.\.venv\Scripts\python.exe -m pytest
```
