"""Shared test setup. Sets required env vars before any app module is
imported, so the test suite is self-sufficient regardless of how it's
invoked (matches the env vars the CI workflow also sets explicitly)."""
import os
import tempfile

_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_db_fd)

os.environ.setdefault("DATABASE_URL", f"sqlite:///{_db_path}")
os.environ.setdefault("JWT_SECRET", "test-only-secret-please-do-not-use-in-production-32bytes")
os.environ.setdefault("ORGANIZER_EMAIL", "")
os.environ.setdefault("ORGANIZER_APP_PASSWORD", "")
os.environ.setdefault("ORGANIZER_BOOTSTRAP_EMAIL", "test-admin@example.com")
os.environ.setdefault("ORGANIZER_BOOTSTRAP_PASSWORD", "TestAdminPass123!")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000")
os.environ.setdefault("LOGIN_RATE_LIMIT", "10")
os.environ.setdefault("OTP_RATE_LIMIT", "5")
os.environ.setdefault("RATE_LIMIT_WINDOW_MINUTES", "15")

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def organizer_token(client):
    r = client.post("/api/v1/auth/login", json={
        "email": os.environ["ORGANIZER_BOOTSTRAP_EMAIL"],
        "password": os.environ["ORGANIZER_BOOTSTRAP_PASSWORD"],
    })
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


import uuid
def unique_email(prefix="user"):
    return f"{prefix}-{uuid.uuid4().hex[:10]}@example.com"


@pytest.fixture(autouse=True)
def _reset_rate_limits():
    from app.security import _hits
    _hits.clear()
    yield
    _hits.clear()
