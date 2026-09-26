#!/usr/bin/env bash
# Boot a kind cluster, apply CI overlay (ephemeral Postgres), run API smoke checks.
# Fail-closed: never exits 0 when the harness cannot run.
#
# Env:
#   SKIP_KIND_BOOTSTRAP=1  — cluster + images already prepared (CI); only apply/wait/smoke
#   KEEP_CLUSTER=1         — do not delete kind cluster on exit
#   KIND_CLUSTER_NAME      — default fpl-ci
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

CLUSTER_NAME="${KIND_CLUSTER_NAME:-fpl-ci}"
KEEP_CLUSTER="${KEEP_CLUSTER:-0}"
SKIP_KIND_BOOTSTRAP="${SKIP_KIND_BOOTSTRAP:-0}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8081}"
FLASK_URL="${FLASK_URL:-http://localhost:5001}"

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "ERROR: required command not found: $1" >&2
    exit 1
  }
}

need kubectl
need curl
need docker
if [[ "$SKIP_KIND_BOOTSTRAP" != "1" ]]; then
  need kind
fi

dump_logs() {
  echo "=== Dumping pod status/logs ==="
  kubectl get pods -n fpl -o wide || true
  for deploy in backend-api flask-ml postgres redis; do
    echo "--- logs: $deploy ---"
    kubectl logs -n fpl "deploy/${deploy}" --tail=80 || true
  done
}

cleanup() {
  local code=$?
  if [[ $code -ne 0 ]]; then
    dump_logs
  fi
  if [[ "$SKIP_KIND_BOOTSTRAP" != "1" && "$KEEP_CLUSTER" != "1" ]]; then
    kind delete cluster --name "$CLUSTER_NAME" >/dev/null 2>&1 || true
  elif [[ "$KEEP_CLUSTER" == "1" ]]; then
    echo "KEEP_CLUSTER=1 — leaving kind cluster '$CLUSTER_NAME' running"
  fi
  exit $code
}
trap cleanup EXIT

if [[ "$SKIP_KIND_BOOTSTRAP" != "1" ]]; then
  echo "==> Building images"
  docker build -t backend-api:ci -f backend/Dockerfile backend
  docker build -t flask-ml:ci -f flask-api/Dockerfile flask-api

  echo "==> Creating kind cluster"
  if kind get clusters 2>/dev/null | grep -qx "$CLUSTER_NAME"; then
    kind delete cluster --name "$CLUSTER_NAME"
  fi
  kind create cluster --name "$CLUSTER_NAME" --config infra/k8s/kind.yaml

  echo "==> Loading images into kind"
  kind load docker-image backend-api:ci --name "$CLUSTER_NAME"
  kind load docker-image flask-ml:ci --name "$CLUSTER_NAME"

  echo "==> Applying CI overlay"
  kubectl apply -k infra/k8s/overlays/ci

  echo "==> Waiting for rollouts"
  kubectl -n fpl rollout status deploy/postgres --timeout=120s
  kubectl -n fpl rollout status deploy/redis --timeout=120s
  kubectl -n fpl rollout status deploy/flask-ml --timeout=180s
  kubectl -n fpl rollout status deploy/backend-api --timeout=240s
fi

wait_http() {
  local url=$1
  local name=$2
  local attempts=${3:-60}
  local i=0
  until curl -fsS "$url" >/dev/null 2>&1; do
    i=$((i + 1))
    if [[ $i -ge $attempts ]]; then
      echo "ERROR: timed out waiting for $name at $url" >&2
      return 1
    fi
    sleep 3
  done
  echo "OK: $name"
}

echo "==> Health checks"
wait_http "${BACKEND_URL}/actuator/health" "backend health"
wait_http "${FLASK_URL}/health" "flask health"

echo "==> Internal token rejection"
status=$(curl -s -o /tmp/flask-opt.json -w "%{http_code}" \
  -X POST "${FLASK_URL}/api/optimize" \
  -H "Content-Type: application/json" \
  -H "X-Internal-Token: bad-token" \
  -d '{"budget":100,"players":[]}')
if [[ "$status" != "401" ]]; then
  echo "ERROR: expected Flask 401 for bad internal token, got $status" >&2
  cat /tmp/flask-opt.json >&2 || true
  exit 1
fi

echo "==> Register + login"
EMAIL="ci-$(date +%s)@example.com"
REGISTER_STATUS=$(curl -s -o /tmp/register.json -w "%{http_code}" \
  -X POST "${BACKEND_URL}/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"CI User\",\"email\":\"${EMAIL}\",\"password\":\"Password1\"}")
if [[ "$REGISTER_STATUS" != "200" ]]; then
  echo "ERROR: register failed ($REGISTER_STATUS)" >&2
  cat /tmp/register.json >&2 || true
  exit 1
fi

LOGIN_STATUS=$(curl -s -o /tmp/login.json -w "%{http_code}" \
  -X POST "${BACKEND_URL}/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"Password1\"}")
if [[ "$LOGIN_STATUS" != "200" ]]; then
  echo "ERROR: login failed ($LOGIN_STATUS)" >&2
  cat /tmp/login.json >&2 || true
  exit 1
fi

if command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  PY=python
fi
TOKEN=$($PY -c "import json; print(json.load(open('/tmp/login.json'))['token'])")
USER_ID=$($PY -c "import json; print(json.load(open('/tmp/login.json'))['id'])")
if [[ -z "$TOKEN" || "$TOKEN" == "None" ]]; then
  echo "ERROR: login response missing token" >&2
  cat /tmp/login.json >&2
  exit 1
fi

echo "==> Seed fixture players"
kubectl -n fpl exec deploy/postgres -- \
  psql -U fpl -d fpl -v ON_ERROR_STOP=1 -c "
INSERT INTO player (name, position, team, fpl_id, value, total_points, weekly_points, predicted_points)
SELECT * FROM (VALUES
  ('GK One', 'GK', 'ARS', 9001::bigint, 4.5::float8, 40, 2, 4.0::float8),
  ('DEF One', 'DEF', 'CHE', 9002::bigint, 4.5::float8, 50, 3, 5.0::float8),
  ('MID One', 'MID', 'LIV', 9003::bigint, 7.0::float8, 80, 5, 8.0::float8)
) AS v(name, position, team, fpl_id, value, total_points, weekly_points, predicted_points)
WHERE NOT EXISTS (SELECT 1 FROM player p WHERE p.fpl_id = v.fpl_id);
"

echo "==> GET /api/v1/players"
PLAYERS_STATUS=$(curl -s -o /tmp/players.json -w "%{http_code}" \
  "${BACKEND_URL}/api/v1/players?page=0&size=5")
if [[ "$PLAYERS_STATUS" =~ ^5 ]]; then
  echo "ERROR: players endpoint returned $PLAYERS_STATUS" >&2
  cat /tmp/players.json >&2 || true
  exit 1
fi
if [[ "$PLAYERS_STATUS" != "200" ]]; then
  echo "ERROR: unexpected players status $PLAYERS_STATUS" >&2
  cat /tmp/players.json >&2 || true
  exit 1
fi

echo "==> Optimize rejects missing JWT"
UNAUTH_OPT=$(curl -s -o /tmp/optimize-unauth.json -w "%{http_code}" \
  -X POST "${BACKEND_URL}/api/v1/team/optimize?userId=${USER_ID}" \
  -H "Content-Type: application/json" \
  -d '{"budget":100.0,"freeTransfers":1,"formation":"3-4-3"}')
if [[ "$UNAUTH_OPT" != "401" ]]; then
  echo "ERROR: expected optimize 401 without JWT, got $UNAUTH_OPT" >&2
  cat /tmp/optimize-unauth.json >&2 || true
  exit 1
fi

echo "==> Optimize (expects 200 or 202)"
OPT_STATUS=$(curl -s -o /tmp/optimize.json -w "%{http_code}" \
  -X POST "${BACKEND_URL}/api/v1/team/optimize?userId=${USER_ID}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{"budget":100.0,"freeTransfers":1,"formation":"3-4-3"}')
if [[ "$OPT_STATUS" != "200" && "$OPT_STATUS" != "202" ]]; then
  echo "ERROR: optimize returned $OPT_STATUS" >&2
  cat /tmp/optimize.json >&2 || true
  exit 1
fi

echo "Integration smoke checks passed."
