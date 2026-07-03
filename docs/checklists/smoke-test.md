# Smoke test checklist

Run after deploy, restore, or infrastructure change.

## Automated

```bash
bash scripts/smoke_test.sh
```

## Manual checklist

- [ ] `GET /health` returns `{"status":"ok"}`
- [ ] `GET /ready` returns `{"status":"ready","database":"connected"}`
- [ ] Login as `applicant@demo.local` succeeds
- [ ] `GET /api/v1/applications` returns seeded data
- [ ] Login as `reviewer@demo.local` succeeds
- [ ] Reviewer can pick up a submitted application
- [ ] Login as `admin@demo.local` — audit log accessible
- [ ] Frontend loads at http://localhost:5173
- [ ] Frontend login → dashboard → application detail works
- [ ] `python scripts/validate_data.py` passes

## Pass criteria

All automated and manual checks pass with no P1/P2 defects open.
