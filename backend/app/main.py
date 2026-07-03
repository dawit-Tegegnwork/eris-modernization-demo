from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlmodel import Session

from app.api.applications import router as applications_router
from app.api.audit import router as audit_router
from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.core.config import settings
from app.db.session import engine, get_session, init_db
from app.scripts.seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with Session(engine) as session:
        seed(session)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="eRIS Modernization Demo",
        version="1.0.0",
        description=(
            "Synthetic regulatory information system modernization demo. "
            "Portfolio reference implementation only — not a government production system."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    prefix = settings.api_prefix
    app.include_router(auth_router, prefix=prefix)
    app.include_router(applications_router, prefix=prefix)
    app.include_router(dashboard_router, prefix=prefix)
    app.include_router(audit_router, prefix=prefix)

    @app.get("/health")
    def health():
        return {"status": "ok", "service": settings.service_name}

    @app.get("/ready")
    def ready(session: Session = Depends(get_session)):
        session.exec(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}

    return app


app = create_app()
