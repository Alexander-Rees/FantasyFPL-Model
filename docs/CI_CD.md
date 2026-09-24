# CI/CD Pipeline Documentation

## Overview

We use **GitHub Actions** for CI/CD with fail-closed gates on every PR.

### 1. CI Pipeline (`.github/workflows/ci.yml`)

**Triggers:** push / pull_request to `main`

**Jobs (required merge checks):**

| Job | What it does |
|-----|----------------|
| `unit_backend` | `./mvnw test` — no soft-skip |
| `unit_flask` | `pytest` — no `\|\| echo skip` |
| `unit_frontend` | `npm test -- --watchAll=false` + production build |
| `build_images` | Docker images for backend + flask (after units) |
| `integration_kind` | kind cluster + `infra/k8s/overlays/ci` + smoke script |

**Rules:**

- Missing secrets do **not** skip integration. PR CI uses in-cluster Postgres.
- Supabase credentials are for local/dev overlays and optional live/nightly jobs only.
- See `docs/BRANCH_PROTECTION.md` to require the four gate jobs on `main`.

### 2. Security Scan (`.github/workflows/security.yml`)

CodeQL + dependency checks. Does not replace the unit/integration merge gates.

## Local commands

```bash
# Unit (fast)
make test

# Integration (kind)
make test-integration
```

## Kind layout

```
infra/k8s/
  kind.yaml
  base/           # redis, backend-api, flask-ml
  overlays/ci/    # ephemeral Postgres + CI env
  overlays/dev/   # Supabase Secret example
```
