# RBAC matrix

| Action | applicant | technical_reviewer | admin | auditor |
|--------|-----------|-------------------|-------|---------|
| Create/submit application | yes | yes | yes | no |
| Pick up for technical review | no | yes | yes | no |
| Request clarification | no | yes | yes | no |
| Approve/reject | no | yes | yes | no |
| View all applications | own only | assigned + submitted queue | yes | read-only |
| Dashboard | yes | yes | yes | yes |
| Audit log | no | no | yes | yes |
| Update checklist | no | yes | yes | no |
