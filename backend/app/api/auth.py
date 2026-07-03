from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.models import LoginInput, TokenResponse, User, UserProfile, verify_password, create_token
from app.db.session import get_session
from app.services.audit import record_audit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginInput, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    record_audit(session, "auth.login", user, "user", str(user.id), {"email": user.email})
    session.commit()
    return TokenResponse(
        access_token=create_token(user),
        role=user.role,
        full_name=user.full_name,
    )


@router.get("/me", response_model=UserProfile)
def me(user: User = Depends(get_current_user)):
    return UserProfile(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        organization=user.organization,
    )
