from sqlmodel import Session

from app.db.models import AuditLog, User


def record_audit(
    session: Session,
    action: str,
    actor: User | None,
    entity_type: str,
    entity_id: str,
    metadata: dict | None = None,
) -> None:
    session.add(
        AuditLog(
            action=action,
            actor_id=actor.id if actor else None,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=metadata or {},
            synthetic_only=True,
        )
    )
