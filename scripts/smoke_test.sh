#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8010}"

echo "==> Health check"
curl -sf "$API_URL/health" | grep -q '"status":"ok"'

echo "==> Readiness check"
curl -sf "$API_URL/ready" | grep -q '"status":"ready"'

echo "==> Login as applicant"
TOKEN=$(curl -sf -X POST "$API_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"applicant@demo.local","password":"Demo123!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "==> List applications"
curl -sf -H "Authorization: Bearer $TOKEN" "$API_URL/api/v1/applications" | grep -q 'reference_number'

echo "==> Dashboard summary"
curl -sf -H "Authorization: Bearer $TOKEN" "$API_URL/api/v1/dashboard/summary" | grep -q 'counts_by_status'

echo "==> Login as admin and check audit"
ADMIN_TOKEN=$(curl -sf -X POST "$API_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@demo.local","password":"Demo123!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -sf -H "Authorization: Bearer $ADMIN_TOKEN" "$API_URL/api/v1/audit" | grep -q 'action'

echo ""
echo "All smoke tests passed."
