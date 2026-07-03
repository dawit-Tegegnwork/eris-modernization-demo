# Architecture

Synthetic regulatory information system modernization demo — portfolio reference implementation only.

```mermaid
flowchart TB
  subgraph client [React_Vite_SPA]
    Login[Login]
    Dashboard[Dashboard]
    AppList[Application_List]
    AppDetail[Application_Detail]
    AuditView[Audit_Log]
  end

  subgraph api [FastAPI_Backend]
    Auth[JWT_Auth]
    RBAC[Role_Guards]
    AppsAPI[Applications_API]
    Workflow[Review_Transitions]
    AuditSvc[Audit_Service]
    Health[Health_Readiness]
  end

  subgraph data [PostgreSQL]
    Users[(users)]
    Apps[(regulatory_applications)]
    Checklist[(document_checklist_items)]
    History[(status_history)]
    Audit[(audit_logs)]
  end

  client -->|REST_Bearer_JWT| api
  api --> data
```

## Components

| Layer | Technology | Responsibility |
|-------|------------|----------------|
| Frontend | React 19 + Vite + TypeScript | Login, dashboard, application workflow UI |
| API | FastAPI + SQLModel | REST endpoints, JWT auth, RBAC |
| Database | PostgreSQL 16 | Persistent storage for users, applications, audit |
| Ops | Docker Compose | Local full-stack run with health checks |

## Workflow

```mermaid
stateDiagram-v2
  [*] --> draft
  draft --> submitted: submit
  submitted --> under_technical_review: pickup
  under_technical_review --> clarification_requested: request_clarification
  clarification_requested --> under_technical_review: resubmit
  under_technical_review --> approved: approve
  under_technical_review --> rejected: reject
  approved --> [*]
  rejected --> [*]
```

## Security model

- JWT bearer tokens (HS256) with configurable expiry
- Role-based access on every mutating endpoint
- Audit log records actor_id on all state changes
- CORS restricted to configured frontend origins
