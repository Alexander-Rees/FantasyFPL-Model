#!/usr/bin/env bash
# Fail-closed unit tests for backend, flask-api, and frontend.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Backend (JUnit)"
(cd backend && ./mvnw test -q)

echo "==> Flask (pytest)"
(
  cd flask-api
  if [[ -d .venv ]]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
  elif [[ -d venv ]]; then
    # shellcheck disable=SC1091
    source venv/bin/activate
  fi
  INTERNAL_API_TOKEN="${INTERNAL_API_TOKEN:-test-internal-token}" \
  DB_SSLMODE="${DB_SSLMODE:-disable}" \
    python -m pytest
)

echo "==> Frontend (Jest)"
(cd frontend && CI=true npm test -- --watchAll=false)

echo "All unit tests passed."
