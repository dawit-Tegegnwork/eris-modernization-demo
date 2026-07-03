from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.api.deps import require_roles
from app.db.models import AuditLog, Role, User
from app.db.session import get_session

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("")
def list_audit(
    action: str | None = None,
    limit: int = Query(default=100, le=200),
    session: Session = Depends(get_session),
    user: User = Depends(require_roles(Role.AUDITOR, Role.ADMIN)),
):
    query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if action:
        query = query.where(AuditLog.action == action)
    events = session.exec(query).all()
    return [
        {
            "id": str(event.id),
            "action": event.action,
            "actor_id": str(event.actor_id) if event.actor_id else None,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "synthetic_only": event.synthetic_only,
            "metadata_json": event.metadata_json,
            "created_at": event.created_at.isoformat(),
        }
        for event in events
    ]
