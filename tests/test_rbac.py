from tests.helpers import auth as _auth, client


def test_applicant_cannot_approve():
    token = _auth("applicant@demo.local")
    apps = client.get("/api/v1/applications", headers=token).json()
    submitted = next((a for a in apps if a["status"] == "submitted"), None)
    assert submitted

    response = client.post(
        f"/api/v1/applications/{submitted['id']}/transition",
        headers=token,
        json={"action": "approve"},
    )
    assert response.status_code == 403


def test_auditor_cannot_create_application():
    response = client.post(
        "/api/v1/applications",
        headers=_auth("auditor@demo.local"),
        json={
            "application_type": "import_permit",
            "product_name": "Test",
            "applicant_org": "Test Org",
            "description": "Should fail",
        },
    )
    assert response.status_code == 403


def test_auditor_can_view_audit():
    response = client.get("/api/v1/audit", headers=_auth("auditor@demo.local"))
    assert response.status_code == 200


def test_applicant_cannot_view_audit():
    response = client.get("/api/v1/audit", headers=_auth("applicant@demo.local"))
    assert response.status_code == 403


def test_reviewer_can_pickup_submitted():
    reviewer = _auth("reviewer@demo.local")
    apps = client.get("/api/v1/applications", headers=reviewer).json()
    submitted = next((a for a in apps if a["status"] == "submitted"), None)
    assert submitted

    response = client.post(
        f"/api/v1/applications/{submitted['id']}/transition",
        headers=reviewer,
        json={"action": "pickup", "note": "Taking for review"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "under_technical_review"
