from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="FinTrack", version="0.1.0")
frontend = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend), name="static")

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(frontend / "index.html")

@app.get("/api/health")
def health():
    return {"status": "ok", "application": "FinTrack"}
