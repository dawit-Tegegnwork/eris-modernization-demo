#!/usr/bin/env python3
"""Post-seed data integrity checks for the eRIS demo database."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlmodel import Session, select

from app.db.models import (
    ApplicationStatus,
    DocumentChecklistItem,
    RegulatoryApplication,
    StatusHistory,
    User,
)
from app.db.session import engine, init_db
from app.scripts.seed import seed


def main() -> int:
    init_db()
    with Session(engine) as session:
        seed(session)

        errors: list[str] = []

        users = session.exec(select(User)).all()
        if len(users) < 4:
            errors.append(f"Expected at least 4 users, found {len(users)}")

        apps = session.exec(select(RegulatoryApplication)).all()
        if len(apps) < 5:
            errors.append(f"Expected at least 5 applications, found {len(apps)}")

        for app in apps:
            history = session.exec(
                select(StatusHistory).where(StatusHistory.application_id == app.id)
            ).all()
            if not history:
                errors.append(f"Application {app.reference_number} has no status history")

            checklist = session.exec(
                select(DocumentChecklistItem).where(
                    DocumentChecklistItem.application_id == app.id
                )
            ).all()
            if not checklist:
                errors.append(f"Application {app.reference_number} has no checklist items")

            if app.status != ApplicationStatus.DRAFT and not app.submitted_at:
                errors.append(
                    f"Application {app.reference_number} is non-draft but missing submitted_at"
                )

        orphan_ids = {item.application_id for item in session.exec(select(DocumentChecklistItem)).all()}
        app_ids = {app.id for app in apps}
        orphans = orphan_ids - app_ids
        if orphans:
            errors.append(f"Found {len(orphans)} orphan checklist items")

        if errors:
            print("VALIDATION FAILED:")
            for err in errors:
                print(f"  - {err}")
            return 1

        print(f"Validation passed: {len(users)} users, {len(apps)} applications")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
