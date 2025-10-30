import json
import os
import tempfile
import pytest

# Ensure we use a temporary SQLite DB for tests
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("FLASK_ENV", "testing")

from app import app  # noqa: E402

@pytest.fixture()
def client():
    app.config.update({
        "TESTING": True,
    })

    with app.test_client() as client:
        yield client


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("status") == "ok"
    assert "timestamp" in data


def test_index(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("message") == "Adriatic Claim Co API"
    assert "owners" in data.get("endpoints", {})
    assert "claims" in data.get("endpoints", {})
