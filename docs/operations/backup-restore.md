# Backup and restore

**Synthetic demo reference only.**

## Backup strategy

| Item | Method | Frequency | Retention |
|------|--------|-----------|-----------|
| PostgreSQL | `pg_dump -Fc` | Daily 02:00 UTC | 30 days |
| Audit logs | Included in DB dump | Daily | 90 days (compliance) |
| App config | Git + env snapshot | On release | Indefinite |
| Container images | Private registry tags | On release | Last 10 tags |

### Backup command

```bash
pg_dump -h localhost -U eris -d eris -Fc -f "eris_backup_$(date +%Y%m%d).dump"
```

## Restore drill

1. Stop API containers: `docker compose stop api`
2. Restore: `pg_restore -h localhost -U eris -d eris_restore --clean eris_backup_YYYYMMDD.dump`
3. Run validation: `python scripts/validate_data.py`
4. Run smoke tests: `bash scripts/smoke_test.sh`
5. Document RTO/RPO achieved

## Targets (demo assumptions)

- **RPO:** 24 hours (daily backup)
- **RTO:** 4 hours (restore + validation + DNS switch)

## Restore checklist

- [ ] Maintenance window announced
- [ ] Current DB backed up before restore
- [ ] Restore completed without errors
- [ ] Row counts verified
- [ ] Smoke tests pass
- [ ] API `/ready` returns connected
- [ ] Stakeholders notified
