# API endpoints

Base URL: `http://localhost:8000`  
API prefix: `/api/v1`  
Auth: `Authorization: Bearer <token>` (except health/ready/login)

## Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Liveness check |
| GET | `/ready` | No | Database connectivity check |

## Auth

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/login` | No | Login with email/password, returns JWT |
| GET | `/api/v1/auth/me` | Yes | Current user profile |

### Login request

```json
{ "email": "applicant@demo.local", "password": "Demo123!" }
```

### Login response

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "role": "applicant",
  "full_name": "Applicant User"
}
```

## Applications

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| GET | `/api/v1/applications` | All | List applications (role-filtered) |
| POST | `/api/v1/applications` | applicant, reviewer, admin | Create draft application |
| GET | `/api/v1/applications/{id}` | All (scoped) | Detail with checklist, history, comments |
| POST | `/api/v1/applications/{id}/transition` | Role-dependent | Workflow transition |
| POST | `/api/v1/applications/{id}/comments` | All (scoped) | Add comment |
| PATCH | `/api/v1/applications/{id}/checklist/{item_id}` | reviewer, admin | Update checklist item |

### Query parameters (list)

- `status` — filter by application status
- `application_type` — filter by type

### Transition actions

| Action | From status | To status | Roles |
|--------|-------------|-----------|-------|
| `submit` | draft | submitted | applicant, reviewer, admin |
| `pickup` | submitted | under_technical_review | reviewer, admin |
| `request_clarification` | under_technical_review | clarification_requested | reviewer, admin |
| `resubmit` | clarification_requested | under_technical_review | applicant, reviewer, admin |
| `approve` | under_technical_review | approved | reviewer, admin |
| `reject` | under_technical_review | rejected | reviewer, admin |

## Dashboard

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/dashboard/summary` | Yes | Status counts and pending review count |

## Audit

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| GET | `/api/v1/audit` | admin, auditor | List audit events (max 200) |

Query: `action`, `limit`

OpenAPI interactive docs: http://localhost:8000/docs
