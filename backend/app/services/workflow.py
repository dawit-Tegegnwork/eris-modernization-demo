from datetime import UTC, datetime

from fastapi import HTTPException
from sqlmodel import Session

from app.db.models import (
    ApplicationComment,
    ApplicationStatus,
    RegulatoryApplication,
    Role,
    StatusHistory,
    User,
)
from app.services.audit import record_audit


TRANSITIONS: dict[str, dict] = {
    "submit": {
        "from": {ApplicationStatus.DRAFT},
        "to": ApplicationStatus.SUBMITTED,
        "roles": {Role.APPLICANT, Role.TECHNICAL_REVIEWER, Role.ADMIN},
    },
    "pickup": {
        "from": {ApplicationStatus.SUBMITTED},
        "to": ApplicationStatus.UNDER_TECHNICAL_REVIEW,
        "roles": {Role.TECHNICAL_REVIEWER, Role.ADMIN},
        "assign_reviewer": True,
    },
    "request_clarification": {
        "from": {ApplicationStatus.UNDER_TECHNICAL_REVIEW},
        "to": ApplicationStatus.CLARIFICATION_REQUESTED,
        "roles": {Role.TECHNICAL_REVIEWER, Role.ADMIN},
    },
    "resubmit": {
        "from": {ApplicationStatus.CLARIFICATION_REQUESTED},
        "to": ApplicationStatus.UNDER_TECHNICAL_REVIEW,
        "roles": {Role.APPLICANT, Role.TECHNICAL_REVIEWER, Role.ADMIN},
    },
    "approve": {
        "from": {ApplicationStatus.UNDER_TECHNICAL_REVIEW},
        "to": ApplicationStatus.APPROVED,
        "roles": {Role.TECHNICAL_REVIEWER, Role.ADMIN},
    },
    "reject": {
        "from": {ApplicationStatus.UNDER_TECHNICAL_REVIEW},
        "to": ApplicationStatus.REJECTED,
        "roles": {Role.TECHNICAL_REVIEWER, Role.ADMIN},
    },
}


def apply_transition(
    session: Session,
    application: RegulatoryApplication,
    user: User,
    action: str,
    note: str = "",
) -> RegulatoryApplication:
    rule = TRANSITIONS.get(action)
    if not rule:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

    if user.role not in rule["roles"]:
        raise HTTPException(status_code=403, detail="Transition not allowed for your role")

    if application.status not in rule["from"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot {action} from status {application.status.value}",
        )

    if action == "submit" and user.role == Role.APPLICANT and application.applicant_id != user.id:
        raise HTTPException(status_code=403, detail="Applicants can only submit their own applications")

    if action in {"approve", "reject", "request_clarification"}:
        if user.role == Role.TECHNICAL_REVIEWER and application.assigned_reviewer_id != user.id:
            raise HTTPException(status_code=403, detail="Application not assigned to you")

    old_status = application.status
    application.status = rule["to"]
    application.updated_at = datetime.now(UTC)

    if action == "submit" and not application.submitted_at:
        application.submitted_at = datetime.now(UTC)

    if rule.get("assign_reviewer"):
        application.assigned_reviewer_id = user.id

    session.add(application)
    session.add(
        StatusHistory(
            application_id=application.id,
            from_status=old_status.value,
            to_status=application.status.value,
            actor_id=user.id,
            note=note,
        )
    )

    if note:
        session.add(
            ApplicationComment(
                application_id=application.id,
                author_id=user.id,
                body=note,
            )
        )

    record_audit(
        session,
        f"application.{action}",
        user,
        "regulatory_application",
        str(application.id),
        {"from": old_status.value, "to": application.status.value, "note": note},
    )

    return application
