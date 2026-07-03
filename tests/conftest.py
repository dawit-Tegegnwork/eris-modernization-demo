import os
import sys
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

os.environ.setdefault("ERIS_DATABASE_URL", f"sqlite:///{uuid4().hex}.db")

import app.db.session as db_session
from app.core.config import settings  # noqa: E402
from app.db.session import init_db, reset_engine  # noqa: E402
from app.main import app  # noqa: E402
from app.scripts.seed import seed  # noqa: E402
from sqlmodel import Session


@pytest.fixture(autouse=True)
def fresh_db(tmp_path):
    db_path = tmp_path / "test.db"
    reset_engine(f"sqlite:///{db_path}")
    settings.database_url = f"sqlite:///{db_path}"
    init_db()
    with Session(db_session.engine) as session:
        seed(session)
    yield


client = TestClient(app)


def _login(email: str) -> str:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "Demo123!"})
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth(email: str) -> dict:
    return {"Authorization": f"Bearer {_login(email)}"}
