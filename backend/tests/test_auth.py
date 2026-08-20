import os

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_signup_rejects_non_edu_email():
    response = client.post("/auth/signup", json={
        "email": "paul@gmail.com",
        "password": "supersecret123",
        "display_name": "Paul",
    })
    assert response.status_code == 400
    assert "edu" in response.json()["detail"].lower()


def test_signup_rejects_short_password():
    response = client.post("/auth/signup", json={
        "email": "paul@williams.edu",
        "password": "short",
        "display_name": "Paul",
    })
    assert response.status_code == 422


def test_signup_rejects_malformed_email():
    response = client.post("/auth/signup", json={
        "email": "not-an-email",
        "password": "supersecret123",
        "display_name": "Paul",
    })
    assert response.status_code == 422


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
