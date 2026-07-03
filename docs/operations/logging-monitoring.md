# Logging and monitoring

**Synthetic demo reference only.**

## Structured logging

API should emit JSON logs with:

```json
{
  "timestamp": "2026-07-03T08:00:00Z",
  "level": "INFO",
  "service": "eris-api",
  "request_id": "uuid",
  "method": "POST",
  "path": "/api/v1/applications/{id}/transition",
  "user_id": "uuid",
  "duration_ms": 45
}
```

## Audit correlation

Every state change writes to `audit_logs` with:
- `actor_id` — who performed the action
- `action` — what happened (e.g. `application.approve`)
- `entity_type` / `entity_id` — what was affected
- `metadata_json` — before/after status, notes

Audit log reads are restricted to `admin` and `auditor` roles.

## Health monitoring

| Endpoint | Purpose | Alert if |
|----------|---------|----------|
| `GET /health` | Liveness | Non-200 for 3 consecutive checks |
| `GET /ready` | DB connectivity | Non-200 or `database != connected` |

## Recommended alerts (production)

- 5xx error rate > 1% over 5 minutes
- Login failure spike (> 50/min — possible brute force)
- Pending review queue > SLA threshold (e.g. 10 days)
- Database connection pool exhaustion
- Disk usage > 80% on PostgreSQL volume

## Dashboards

- Application counts by status (mirrors `/api/v1/dashboard/summary`)
- Transition throughput per day
- Average time in `under_technical_review`
- Audit events by action type
