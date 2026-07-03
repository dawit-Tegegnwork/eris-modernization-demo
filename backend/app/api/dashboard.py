from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select

from app.api.deps import get_current_user
from app.db.models import ApplicationStatus, RegulatoryApplication, Role, User
from app.db.session import get_session

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    counts: dict[str, int] = {}
    for status in ApplicationStatus:
        query = select(func.count()).select_from(RegulatoryApplication).where(
            RegulatoryApplication.status == status
        )
        if user.role == Role.APPLICANT:
            query = query.where(RegulatoryApplication.applicant_id == user.id)
        elif user.role == Role.TECHNICAL_REVIEWER:
            query = query.where(
                (RegulatoryApplication.assigned_reviewer_id == user.id)
                | (RegulatoryApplication.status == ApplicationStatus.SUBMITTED)
            )
        counts[status.value] = session.exec(query).one()

    pending_review = 0
    if user.role in {Role.TECHNICAL_REVIEWER, Role.ADMIN}:
        pending_review = session.exec(
            select(func.count())
            .select_from(RegulatoryApplication)
            .where(RegulatoryApplication.status == ApplicationStatus.SUBMITTED)
        ).one()

    return {
        "counts_by_status": counts,
        "viewer_role": user.role.value,
        "pending_review": pending_review,
    }
