# Release checklist

- [ ] All tests pass: `pytest -q`
- [ ] Frontend builds: `cd frontend && npm run build`
- [ ] Data validation passes: `python scripts/validate_data.py`
- [ ] Smoke tests pass: `bash scripts/smoke_test.sh`
- [ ] Environment variables documented in `.env.example`
- [ ] `ERIS_SECRET_KEY` rotated for non-demo environments
- [ ] Database backup taken before deploy
- [ ] `/ready` endpoint verified on staging
- [ ] Release notes updated
- [ ] Git tag created: `vX.Y.Z`
- [ ] Rollback plan reviewed ([rollback.md](rollback.md))
