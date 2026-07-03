from tests.helpers import auth as _auth, client


def test_list_applications_seeded():
    response = client.get("/api/v1/applications", headers=_auth("admin@demo.local"))
    assert response.status_code == 200
    apps = response.json()
    assert len(apps) >= 5


def test_application_detail_includes_checklist():
    response = client.get("/api/v1/applications", headers=_auth("admin@demo.local"))
    app_id = response.json()[0]["id"]
    detail = client.get(f"/api/v1/applications/{app_id}", headers=_auth("admin@demo.local"))
    assert detail.status_code == 200
    body = detail.json()
    assert "checklist" in body
    assert len(body["checklist"]) > 0


def test_dashboard_summary():
    response = client.get("/api/v1/dashboard/summary", headers=_auth("admin@demo.local"))
    assert response.status_code == 200
    body = response.json()
    assert "counts_by_status" in body
    assert body["viewer_role"] == "admin"


def test_checklist_update():
    admin = _auth("admin@demo.local")
    apps = client.get("/api/v1/applications", headers=admin).json()
    app_id = apps[0]["id"]
    detail = client.get(f"/api/v1/applications/{app_id}", headers=admin).json()
    item_id = detail["checklist"][0]["id"]

    response = client.patch(
        f"/api/v1/applications/{app_id}/checklist/{item_id}",
        headers=admin,
        json={"received": True, "notes": "Verified in demo"},
    )
    assert response.status_code == 200
    assert response.json()["received"] is True


def test_add_comment():
    admin = _auth("admin@demo.local")
    apps = client.get("/api/v1/applications", headers=admin).json()
    app_id = apps[0]["id"]

    response = client.post(
        f"/api/v1/applications/{app_id}/comments",
        headers=admin,
        json={"body": "Internal review note for demo"},
    )
    assert response.status_code == 200
    assert response.json()["body"] == "Internal review note for demo"
