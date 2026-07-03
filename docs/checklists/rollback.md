# Rollback checklist

Trigger rollback if smoke tests fail or P1 defect found within 72 hours of release.

## Steps

1. [ ] Announce rollback to stakeholders
2. [ ] Stop current API and frontend containers
3. [ ] Re-deploy previous container image tag
4. [ ] Restore database from pre-release backup if schema/data changed
5. [ ] Run `python scripts/validate_data.py`
6. [ ] Run `bash scripts/smoke_test.sh`
7. [ ] Verify `/health` and `/ready`
8. [ ] Confirm frontend loads and login works
9. [ ] Document incident and root cause
10. [ ] Schedule fix-forward release

## Rollback decision criteria

- Authentication broken for all users
- Data integrity failure (orphan records, missing audit entries)
- Regulatory submission workflow blocked
- Error rate > 5% on critical endpoints for 15+ minutes

## Docker rollback example

```bash
docker compose down
git checkout v1.0.0
docker compose up --build -d
bash scripts/smoke_test.sh
```
