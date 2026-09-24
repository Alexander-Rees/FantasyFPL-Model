# Agent guidance — fantasy-soccer-app

## Always verify with tests before returning

Before you finish a coding task (or claim it is done), **run the relevant tests and fix failures**. Do not return with untested changes when tests exist for the area you touched.

### Default gate

```bash
make test
# or
./scripts/test-unit.sh
```

This runs backend JUnit, Flask pytest, and frontend Jest. It must exit non-zero on failure — never soft-skip.

### Scope the suite when appropriate

| Touched area | Minimum verification |
|--------------|----------------------|
| `backend/**` | `cd backend && ./mvnw test -q` |
| `flask-api/**` | `cd flask-api && INTERNAL_API_TOKEN=test-internal-token DB_SSLMODE=disable python -m pytest -q` |
| `frontend/**` | `cd frontend && CI=true npm test -- --watchAll=false` |
| CI / k8s / scripts | Prefer full `make test`; for kind smoke use `make test-integration` when Docker/kind are available |

If you changed more than one package, run `make test` (or each package’s suite) before returning.

### Rules

1. **Fail closed** — do not use `|| true`, `|| echo skip`, or similar to hide test/CI failures.
2. **Fix or flag** — if tests fail because of your changes, fix them before finishing. If failures are pre-existing and unrelated, say so explicitly and still show the command output.
3. **No “tests should pass” without running them** — do not claim green without executing the commands above in this session.
4. **Integration optional locally** — kind/integration (`make test-integration`) is required when you change `infra/k8s/**`, `scripts/test-integration-kind.sh`, or CI integration jobs; otherwise unit tests are enough unless the user asks for integration.

## Never commit secrets

Before staging or pushing, treat credential leakage as a hard stop. Real API keys, passwords, tokens, and private keys must never enter git history.

### Do not commit

- `.env`, `.env.*` (except committed `*.example` / `env.example` templates with placeholders only)
- Filled-in k8s Secrets (especially real values in `infra/k8s/overlays/dev/secret-example.yaml`)
- Cloud keys: OpenAI/Anthropic (`sk-…` / `sk-ant-…`), Supabase service-role/anon keys, GitHub PATs (`ghp_…`), AWS (`AKIA…`), JWTs (`eyJ…`)
- Private keys / certs (`-----BEGIN … PRIVATE KEY-----`)
- Production DB passwords, connection strings with embedded credentials, webhook secrets

### Allowed placeholders only

| OK in repo | Not OK |
|------------|--------|
| `your_database_password_here`, `replace-me`, `YOUR_HOST` | Real Supabase host/password/keys |
| `dev-internal-token`, `test-internal-token`, `ci-internal-token` | Production `INTERNAL_API_TOKEN` |
| `fpl-ci-password` (ephemeral kind CI only) | Reusing CI creds against a long-lived/public cluster |
| Commented examples like `# LLM_API_KEY=sk-your-api-key-here` | Live `sk-…` / `sk-ant-…` values |

`.env` is gitignored — keep it that way. Copy from `env.example` / `.env.example` locally; never `git add -f .env`.

### Pre-commit / pre-push checklist for agents

1. Run `git status` and confirm `.env`, `.env.bak`, and any `*secret*` files with real values are **not** staged.
2. Scan staged paths for secret-like patterns before committing:
   ```bash
   git diff --cached | rg -i 'sk-[A-Za-z0-9]|sk-ant-|ghp_|github_pat_|AKIA|eyJ[A-Za-z0-9_-]+\.|BEGIN .*PRIVATE KEY|SERVICE_ROLE|supabase\.co/|password\s*=\s*\S{12,}' || true
   ```
   If anything real matches, **unstage and stop** — do not commit.
3. Never paste production credentials into tracked YAML/docs/examples. For local Supabase, use a gitignored secret or `kubectl create secret` instead of editing `secret-example.yaml`.
4. Prefer env vars / Secret Manager over hardcoding. Test fixtures may use obvious fake tokens (`test-token`, `Password1`) only.

### Related docs

- `docs/CI_CD.md` — CI jobs and fail-closed rules
- `docs/BRANCH_PROTECTION.md` — required status checks on `main`
- `README.md` — Testing section
- `env.example` — placeholder env template (safe to commit)
