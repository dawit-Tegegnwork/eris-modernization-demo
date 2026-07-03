from datetime import UTC, datetime

from sqlmodel import Session, select

from app.db.models import (
    ApplicationStatus,
    ApplicationType,
    DEFAULT_CHECKLIST,
    DocumentChecklistItem,
    RegulatoryApplication,
    Role,
    StatusHistory,
    User,
    hash_password,
)


def seed_users(session: Session) -> None:
    if session.exec(select(User)).first():
        return
    users = [
        ("applicant@demo.local", "Applicant User", Role.APPLICANT, "Synthetic Pharma Co."),
        ("reviewer@demo.local", "Technical Reviewer", Role.TECHNICAL_REVIEWER, "EFDA Demo Authority"),
        ("admin@demo.local", "System Admin", Role.ADMIN, "EFDA Demo Authority"),
        ("auditor@demo.local", "Compliance Auditor", Role.AUDITOR, "EFDA Demo Authority"),
    ]
    for email, name, role, org in users:
        session.add(
            User(
                email=email,
                full_name=name,
                role=role,
                organization=org,
                password_hash=hash_password("Demo123!"),
            )
        )
    session.commit()


def _add_checklist(session: Session, application: RegulatoryApplication) -> None:
    items = DEFAULT_CHECKLIST.get(application.application_type, [])
    for doc_type, label, required in items:
        session.add(
            DocumentChecklistItem(
                application_id=application.id,
                doc_type=doc_type,
                label=label,
                required=required,
                received=application.status != ApplicationStatus.DRAFT,
            )
        )


def seed_applications(session: Session) -> None:
    if session.exec(select(RegulatoryApplication)).first():
        return

    applicant = session.exec(select(User).where(User.email == "applicant@demo.local")).first()
    reviewer = session.exec(select(User).where(User.email == "reviewer@demo.local")).first()
    if not applicant or not reviewer:
        return

    samples = [
        (
            "ERIS-2026-0001",
            ApplicationType.PRODUCT_REGISTRATION,
            "Amoxicillin 500mg Capsules",
            "Synthetic Pharma Co.",
            "Synthetic product registration dossier for portfolio demo.",
            ApplicationStatus.UNDER_TECHNICAL_REVIEW,
            applicant.id,
            reviewer.id,
            datetime(2026, 1, 15, tzinfo=UTC),
        ),
        (
            "ERIS-2026-0002",
            ApplicationType.IMPORT_PERMIT,
            "Paracetamol API Batch IMP-442",
            "Global Med Imports Ltd.",
            "Synthetic import permit request awaiting technical review pickup.",
            ApplicationStatus.SUBMITTED,
            applicant.id,
            None,
            datetime(2026, 2, 1, tzinfo=UTC),
        ),
        (
            "ERIS-2026-0003",
            ApplicationType.GMP_CERTIFICATE,
            "Addis Synthetic Manufacturing Site",
            "Addis Pharma Manufacturing PLC",
            "Synthetic GMP certificate renewal under review.",
            ApplicationStatus.CLARIFICATION_REQUESTED,
            applicant.id,
            reviewer.id,
            datetime(2026, 1, 20, tzinfo=UTC),
        ),
        (
            "ERIS-2026-0004",
            ApplicationType.VARIATION_AMENDMENT,
            "Metformin 850mg Label Update",
            "Synthetic Pharma Co.",
            "Synthetic variation for labeling change — approved in demo data.",
            ApplicationStatus.APPROVED,
            applicant.id,
            reviewer.id,
            datetime(2025, 12, 10, tzinfo=UTC),
        ),
        (
            "ERIS-2026-0005",
            ApplicationType.PRODUCT_REGISTRATION,
            "Ciprofloxacin 250mg Tablets",
            "Horizon Generics PLC",
            "Synthetic registration rejected due to incomplete stability data.",
            ApplicationStatus.REJECTED,
            applicant.id,
            reviewer.id,
            datetime(2025, 11, 5, tzinfo=UTC),
        ),
        (
            "ERIS-2026-0006",
            ApplicationType.IMPORT_PERMIT,
            "Insulin Glargine Prefilled Pens",
            "MedSupply Ethiopia",
            "Draft import permit — not yet submitted.",
            ApplicationStatus.DRAFT,
            applicant.id,
            None,
            None,
        ),
    ]

    for ref, app_type, product, org, desc, status, applicant_id, reviewer_id, submitted_at in samples:
        app = RegulatoryApplication(
            reference_number=ref,
            application_type=app_type,
            product_name=product,
            applicant_org=org,
            description=desc,
            status=status,
            applicant_id=applicant_id,
            assigned_reviewer_id=reviewer_id,
            submitted_at=submitted_at,
        )
        session.add(app)
        session.commit()
        session.refresh(app)
        _add_checklist(session, app)
        actor = reviewer if reviewer_id else applicant
        session.add(
            StatusHistory(
                application_id=app.id,
                from_status=None,
                to_status=ApplicationStatus.DRAFT.value,
                actor_id=applicant_id,
                note="Application created (seed)",
            )
        )
        if submitted_at:
            session.add(
                StatusHistory(
                    application_id=app.id,
                    from_status=ApplicationStatus.DRAFT.value,
                    to_status=ApplicationStatus.SUBMITTED.value,
                    actor_id=applicant_id,
                    note="Submitted for regulatory review (seed)",
                )
            )
        if status in {
            ApplicationStatus.UNDER_TECHNICAL_REVIEW,
            ApplicationStatus.CLARIFICATION_REQUESTED,
            ApplicationStatus.APPROVED,
            ApplicationStatus.REJECTED,
        }:
            session.add(
                StatusHistory(
                    application_id=app.id,
                    from_status=ApplicationStatus.SUBMITTED.value,
                    to_status=ApplicationStatus.UNDER_TECHNICAL_REVIEW.value,
                    actor_id=reviewer.id,
                    note="Picked up for technical review (seed)",
                )
            )
        if status == ApplicationStatus.CLARIFICATION_REQUESTED:
            session.add(
                StatusHistory(
                    application_id=app.id,
                    from_status=ApplicationStatus.UNDER_TECHNICAL_REVIEW.value,
                    to_status=ApplicationStatus.CLARIFICATION_REQUESTED.value,
                    actor_id=reviewer.id,
                    note="Clarification requested on validation summary (seed)",
                )
            )
        if status == ApplicationStatus.APPROVED:
            session.add(
                StatusHistory(
                    application_id=app.id,
                    from_status=ApplicationStatus.UNDER_TECHNICAL_REVIEW.value,
                    to_status=ApplicationStatus.APPROVED.value,
                    actor_id=reviewer.id,
                    note="Approved — synthetic demo decision",
                )
            )
        if status == ApplicationStatus.REJECTED:
            session.add(
                StatusHistory(
                    application_id=app.id,
                    from_status=ApplicationStatus.UNDER_TECHNICAL_REVIEW.value,
                    to_status=ApplicationStatus.REJECTED.value,
                    actor_id=reviewer.id,
                    note="Rejected — incomplete stability documentation (seed)",
                )
            )
    session.commit()


def seed(session: Session) -> None:
    seed_users(session)
    seed_applications(session)
