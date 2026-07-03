import os
import sys
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

os.environ.setdefault("ERIS_DATABASE_URL", f"sqlite:///{uuid4().hex}.db")

from app.main import app  # noqa: E402

client = TestClient(app)


def login(email: str) -> str:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "Demo123!"})
    assert response.status_code == 200
    return response.json()["access_token"]


def auth(email: str) -> dict:
    return {"Authorization": f"Bearer {login(email)}"}
