from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy import Column, JSON, text
from sqlmodel import Field as SQLField, SQLModel

from app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class Role(str, Enum):
    APPLICANT = "applicant"
    TECHNICAL_REVIEWER = "technical_reviewer"
    ADMIN = "admin"
    AUDITOR = "auditor"


class ApplicationType(str, Enum):
    PRODUCT_REGISTRATION = "product_registration"
    IMPORT_PERMIT = "import_permit"
    GMP_CERTIFICATE = "gmp_certificate"
    VARIATION_AMENDMENT = "variation_amendment"


class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_TECHNICAL_REVIEW = "under_technical_review"
    CLARIFICATION_REQUESTED = "clarification_requested"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = SQLField(default_factory=uuid4, primary_key=True)
    email: str = SQLField(unique=True, index=True)
    full_name: str
    role: Role
    organization: str = "Synthetic Pharma Co."
    password_hash: str


class RegulatoryApplication(SQLModel, table=True):
    __tablename__ = "regulatory_applications"

    id: UUID = SQLField(default_factory=uuid4, primary_key=True)
    reference_number: str = SQLField(unique=True, index=True, max_length=50)
    application_type: ApplicationType
    product_name: str = SQLField(max_length=200)
    applicant_org: str = SQLField(max_length=200)
    description: str
    status: ApplicationStatus = ApplicationStatus.DRAFT
    applicant_id: UUID = SQLField(foreign_key="users.id", index=True)
    assigned_reviewer_id: Optional[UUID] = SQLField(default=None, foreign_key="users.id")
    submitted_at: Optional[datetime] = None
    created_at: datetime = SQLField(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = SQLField(default_factory=lambda: datetime.now(UTC))


class DocumentChecklistItem(SQLModel, table=True):
    __tablename__ = "document_checklist_items"

    id: UUID = SQLField(default_factory=uuid4, primary_key=True)
    application_id: UUID = SQLField(foreign_key="regulatory_applications.id", index=True)
    doc_type: str = SQLField(max_length=80)
    label: str = SQLField(max_length=200)
    required: bool = True
    received: bool = False
    notes: str = ""


class StatusHistory(SQLModel, table=True):
    __tablename__ = "status_history"

    id: UUID = SQLField(default_factory=uuid4, primary_key=True)
    application_id: UUID = SQLField(foreign_key="regulatory_applications.id", index=True)
    from_status: Optional[str] = None
    to_status: str
    actor_id: UUID = SQLField(foreign_key="users.id")
    note: str = ""
    created_at: datetime = SQLField(default_factory=lambda: datetime.now(UTC))


class ApplicationComment(SQLModel, table=True):
    __tablename__ = "application_comments"

    id: UUID = SQLField(default_factory=uuid4, primary_key=True)
    application_id: UUID = SQLField(foreign_key="regulatory_applications.id", index=True)
    author_id: UUID = SQLField(foreign_key="users.id")
    body: str
    created_at: datetime = SQLField(default_factory=lambda: datetime.now(UTC))


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: UUID = SQLField(default_factory=uuid4, primary_key=True)
    action: str = SQLField(max_length=100, index=True)
    actor_id: Optional[UUID] = SQLField(default=None, foreign_key="users.id")
    entity_type: str = SQLField(default="", max_length=50)
    entity_id: Optional[str] = SQLField(default=None, max_length=64)
    synthetic_only: bool = True
    metadata_json: dict = SQLField(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = SQLField(default_factory=lambda: datetime.now(UTC))


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "role": user.role.value,
        "exp": datetime.now(UTC) + timedelta(minutes=settings.token_expire_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


class LoginInput(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role
    full_name: str


class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    role: Role
    organization: str


class ApplicationCreateInput(BaseModel):
    application_type: ApplicationType
    product_name: str = Field(min_length=1, max_length=200)
    applicant_org: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=4000)


class TransitionInput(BaseModel):
    action: str = Field(
        description="submit, pickup, request_clarification, resubmit, approve, reject"
    )
    note: str = ""


class CommentInput(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class ChecklistUpdateInput(BaseModel):
    received: bool
    notes: str = ""


DEFAULT_CHECKLIST: dict[ApplicationType, list[tuple[str, str, bool]]] = {
    ApplicationType.PRODUCT_REGISTRATION: [
        ("dossier", "Product dossier (CTD format)", True),
        ("gmp_cert", "GMP certificate copy", True),
        ("labeling", "Proposed labeling", True),
        ("stability", "Stability study summary", False),
    ],
    ApplicationType.IMPORT_PERMIT: [
        ("invoice", "Proforma invoice", True),
        ("coa", "Certificate of analysis", True),
        ("import_license", "Prior import authorization (if applicable)", False),
    ],
    ApplicationType.GMP_CERTIFICATE: [
        ("facility_layout", "Facility layout diagram", True),
        ("validation", "Process validation summary", True),
        ("quality_manual", "Quality management manual excerpt", True),
    ],
    ApplicationType.VARIATION_AMENDMENT: [
        ("change_control", "Change control documentation", True),
        ("risk_assessment", "Risk assessment report", True),
        ("updated_label", "Updated product label", False),
    ],
}
