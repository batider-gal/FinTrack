from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "application": "FinTrack"}

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome back" in response.text
    assert "transaction-form" in response.text
    assert "/static/script.js" in response.text
