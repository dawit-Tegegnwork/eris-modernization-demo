from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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

    @app.get("/", response_class=HTMLResponse)
    def landing_page() -> str:
        return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>eRIS Modernization Demo</title>
  <style>
    body { margin: 0; font-family: system-ui, sans-serif; background: #f8fafc; color: #0f172a; line-height: 1.6; }
    main { max-width: 880px; margin: 0 auto; padding: 48px 20px; }
    .card { background: white; border: 1px solid #e2e8f0; border-radius: 18px; padding: 28px; box-shadow: 0 16px 40px rgba(15,23,42,.08); }
    .notice { background: #ecfdf5; border: 1px solid #bbf7d0; color: #166534; padding: 12px 14px; border-radius: 12px; }
    a { color: #2563eb; font-weight: 700; } code { background: #f1f5f9; padding: 2px 6px; border-radius: 6px; }
    .links a { display: inline-block; margin: 8px 14px 8px 0; }
  </style>
</head>
<body>
  <main>
    <section class="card">
      <p><strong>Portfolio modernization lab</strong></p>
      <h1>eRIS Modernization Demo</h1>
      <p>Synthetic regulatory workflow modernization reference with JWT/RBAC, review queues, status transitions, audit trail, PostgreSQL, Docker, and release/migration documentation.</p>
      <p class="notice"><strong>Synthetic data only.</strong> Not real eRIS, not connected to EFDA, and not a government production system.</p>
      <div class="links">
        <a href="/docs">OpenAPI docs</a>
        <a href="/health">Health</a>
        <a href="/ready">Readiness</a>
        <a href="http://localhost:5180">React frontend</a>
        <a href="https://github.com/dawit-Tegegnwork/eris-modernization-demo">GitHub</a>
      </div>
      <h2>3-minute test path</h2>
      <ol>
        <li>Open the React frontend: <code>http://localhost:5180</code></li>
        <li>Login as <code>reviewer@demo.local</code> / <code>Demo123!</code></li>
        <li>Open Applications and review seeded regulatory records.</li>
        <li>Check <code>/api/v1/dashboard/summary</code> and <code>/api/v1/audit</code> in OpenAPI docs.</li>
      </ol>
    </section>
  </main>
</body>
</html>"""

    @app.get("/ready")
    def ready(session: Session = Depends(get_session)):
        session.exec(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}

    return app


app = create_app()
