from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, func, select

from app.api.deps import get_current_user, require_roles
from app.db.models import (
    ApplicationComment,
    ApplicationCreateInput,
    ApplicationStatus,
    ApplicationType,
    ChecklistUpdateInput,
    CommentInput,
    DocumentChecklistItem,
    RegulatoryApplication,
    Role,
    StatusHistory,
    TransitionInput,
    User,
    DEFAULT_CHECKLIST,
)
from app.db.session import get_session
from app.services.audit import record_audit
from app.services.workflow import apply_transition

router = APIRouter(prefix="/applications", tags=["applications"])


def _next_reference(session: Session) -> str:
    count = session.exec(select(func.count()).select_from(RegulatoryApplication)).one()
    year = datetime.now(UTC).year
    return f"ERIS-{year}-{count + 1:04d}"


def _can_view_application(user: User, app: RegulatoryApplication) -> bool:
    if user.role in {Role.ADMIN, Role.AUDITOR, Role.TECHNICAL_REVIEWER}:
        return True
    return app.applicant_id == user.id


def _application_payload(app: RegulatoryApplication) -> dict:
    return {
        "id": str(app.id),
        "reference_number": app.reference_number,
        "application_type": app.application_type.value,
        "product_name": app.product_name,
        "applicant_org": app.applicant_org,
        "description": app.description,
        "status": app.status.value,
        "applicant_id": str(app.applicant_id),
        "assigned_reviewer_id": str(app.assigned_reviewer_id) if app.assigned_reviewer_id else None,
        "submitted_at": app.submitted_at.isoformat() if app.submitted_at else None,
        "created_at": app.created_at.isoformat(),
        "updated_at": app.updated_at.isoformat(),
    }


def _create_checklist(session: Session, application: RegulatoryApplication) -> None:
    items = DEFAULT_CHECKLIST.get(application.application_type, [])
    for doc_type, label, required in items:
        session.add(
            DocumentChecklistItem(
                application_id=application.id,
                doc_type=doc_type,
                label=label,
                required=required,
            )
        )


@router.get("")
def list_applications(
    status: ApplicationStatus | None = None,
    application_type: ApplicationType | None = None,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    query = select(RegulatoryApplication).order_by(RegulatoryApplication.created_at.desc())
    if user.role == Role.APPLICANT:
        query = query.where(RegulatoryApplication.applicant_id == user.id)
    if status:
        query = query.where(RegulatoryApplication.status == status)
    if application_type:
        query = query.where(RegulatoryApplication.application_type == application_type)
    rows = session.exec(query).all()
    if user.role == Role.TECHNICAL_REVIEWER:
        rows = [
            row
            for row in rows
            if row.status == ApplicationStatus.SUBMITTED
            or row.assigned_reviewer_id == user.id
        ]
    return [_application_payload(row) for row in rows]


@router.post("")
def create_application(
    payload: ApplicationCreateInput,
    session: Session = Depends(get_session),
    user: User = Depends(require_roles(Role.APPLICANT, Role.TECHNICAL_REVIEWER, Role.ADMIN)),
):
    app = RegulatoryApplication(
        reference_number=_next_reference(session),
        application_type=payload.application_type,
        product_name=payload.product_name,
        applicant_org=payload.applicant_org,
        description=payload.description,
        applicant_id=user.id,
        status=ApplicationStatus.DRAFT,
    )
    session.add(app)
    session.commit()
    session.refresh(app)
    _create_checklist(session, app)
    session.add(
        StatusHistory(
            application_id=app.id,
            from_status=None,
            to_status=ApplicationStatus.DRAFT.value,
            actor_id=user.id,
            note="Application created",
        )
    )
    record_audit(
        session,
        "application.create",
        user,
        "regulatory_application",
        str(app.id),
        {"reference_number": app.reference_number},
    )
    session.commit()
    session.refresh(app)
    return _application_payload(app)


@router.get("/{application_id}")
def get_application(
    application_id: UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    app = session.get(RegulatoryApplication, application_id)
    if not app or not _can_view_application(user, app):
        raise HTTPException(status_code=404, detail="Application not found")

    checklist = session.exec(
        select(DocumentChecklistItem)
        .where(DocumentChecklistItem.application_id == application_id)
        .order_by(DocumentChecklistItem.label)
    ).all()
    history = session.exec(
        select(StatusHistory)
        .where(StatusHistory.application_id == application_id)
        .order_by(StatusHistory.created_at.asc())
    ).all()
    comments = session.exec(
        select(ApplicationComment)
        .where(ApplicationComment.application_id == application_id)
        .order_by(ApplicationComment.created_at.asc())
    ).all()

    return {
        **_application_payload(app),
        "checklist": [
            {
                "id": str(item.id),
                "doc_type": item.doc_type,
                "label": item.label,
                "required": item.required,
                "received": item.received,
                "notes": item.notes,
            }
            for item in checklist
        ],
        "history": [
            {
                "id": str(row.id),
                "from_status": row.from_status,
                "to_status": row.to_status,
                "actor_id": str(row.actor_id),
                "note": row.note,
                "created_at": row.created_at.isoformat(),
            }
            for row in history
        ],
        "comments": [
            {
                "id": str(row.id),
                "author_id": str(row.author_id),
                "body": row.body,
                "created_at": row.created_at.isoformat(),
            }
            for row in comments
        ],
    }


@router.post("/{application_id}/transition")
def transition_application(
    application_id: UUID,
    payload: TransitionInput,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    app = session.get(RegulatoryApplication, application_id)
    if not app or not _can_view_application(user, app):
        raise HTTPException(status_code=404, detail="Application not found")

    apply_transition(session, app, user, payload.action, payload.note)
    session.commit()
    session.refresh(app)
    return _application_payload(app)


@router.post("/{application_id}/comments")
def add_comment(
    application_id: UUID,
    payload: CommentInput,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    app = session.get(RegulatoryApplication, application_id)
    if not app or not _can_view_application(user, app):
        raise HTTPException(status_code=404, detail="Application not found")

    comment = ApplicationComment(
        application_id=application_id,
        author_id=user.id,
        body=payload.body,
    )
    session.add(comment)
    record_audit(
        session,
        "application.comment",
        user,
        "regulatory_application",
        str(application_id),
        {"body_preview": payload.body[:120]},
    )
    session.commit()
    session.refresh(comment)
    return {
        "id": str(comment.id),
        "author_id": str(comment.author_id),
        "body": comment.body,
        "created_at": comment.created_at.isoformat(),
    }


@router.patch("/{application_id}/checklist/{item_id}")
def update_checklist_item(
    application_id: UUID,
    item_id: UUID,
    payload: ChecklistUpdateInput,
    session: Session = Depends(get_session),
    user: User = Depends(require_roles(Role.TECHNICAL_REVIEWER, Role.ADMIN)),
):
    app = session.get(RegulatoryApplication, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    item = session.get(DocumentChecklistItem, item_id)
    if not item or item.application_id != application_id:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    item.received = payload.received
    item.notes = payload.notes
    session.add(item)
    record_audit(
        session,
        "checklist.update",
        user,
        "document_checklist_item",
        str(item.id),
        {"received": payload.received, "application_id": str(application_id)},
    )
    session.commit()
    session.refresh(item)
    return {
        "id": str(item.id),
        "doc_type": item.doc_type,
        "label": item.label,
        "required": item.required,
        "received": item.received,
        "notes": item.notes,
    }
