from tests.helpers import auth as _auth
from tests.helpers import client, login as _login


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "eRIS" in response.json()["service"]


def test_ready_check():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_login_success():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "applicant@demo.local", "password": "Demo123!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["role"] == "applicant"


def test_login_failure():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "applicant@demo.local", "password": "wrong"},
    )
    assert response.status_code == 401


def test_auth_me():
    response = client.get("/api/v1/auth/me", headers=_auth("reviewer@demo.local"))
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "reviewer@demo.local"
    assert body["role"] == "technical_reviewer"


def test_invalid_token():
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
