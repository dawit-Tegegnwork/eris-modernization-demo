from tests.helpers import auth as _auth, client


def test_full_workflow_happy_path():
    applicant = _auth("applicant@demo.local")
    reviewer = _auth("reviewer@demo.local")

    create = client.post(
        "/api/v1/applications",
        headers=applicant,
        json={
            "application_type": "product_registration",
            "product_name": "Workflow Test Product",
            "applicant_org": "Synthetic Pharma Co.",
            "description": "End-to-end workflow test application.",
        },
    )
    assert create.status_code == 200
    app_id = create.json()["id"]
    assert create.json()["status"] == "draft"

    submit = client.post(
        f"/api/v1/applications/{app_id}/transition",
        headers=applicant,
        json={"action": "submit", "note": "Ready for review"},
    )
    assert submit.status_code == 200
    assert submit.json()["status"] == "submitted"

    pickup = client.post(
        f"/api/v1/applications/{app_id}/transition",
        headers=reviewer,
        json={"action": "pickup"},
    )
    assert pickup.status_code == 200
    assert pickup.json()["status"] == "under_technical_review"

    clarify = client.post(
        f"/api/v1/applications/{app_id}/transition",
        headers=reviewer,
        json={"action": "request_clarification", "note": "Need stability data"},
    )
    assert clarify.status_code == 200
    assert clarify.json()["status"] == "clarification_requested"

    resubmit = client.post(
        f"/api/v1/applications/{app_id}/transition",
        headers=applicant,
        json={"action": "resubmit", "note": "Stability data attached"},
    )
    assert resubmit.status_code == 200
    assert resubmit.json()["status"] == "under_technical_review"

    approve = client.post(
        f"/api/v1/applications/{app_id}/transition",
        headers=reviewer,
        json={"action": "approve", "note": "All requirements met"},
    )
    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"

    detail = client.get(f"/api/v1/applications/{app_id}", headers=reviewer)
    assert detail.status_code == 200
    history = detail.json()["history"]
    assert len(history) >= 5
    assert history[-1]["to_status"] == "approved"


def test_status_history_recorded():
    reviewer = _auth("reviewer@demo.local")
    apps = client.get("/api/v1/applications", headers=reviewer).json()
    app = next(a for a in apps if a["reference_number"] == "ERIS-2026-0001")
    detail = client.get(f"/api/v1/applications/{app['id']}", headers=reviewer)
    history = detail.json()["history"]
    assert any(h["to_status"] == "under_technical_review" for h in history)
