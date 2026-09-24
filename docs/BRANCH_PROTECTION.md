# Branch protection (enable manually on GitHub)

Require these status checks before merging to `main`:

- `unit_backend`
- `unit_flask`
- `unit_frontend`
- `integration_kind`

Recommended settings:

1. Settings → Branches → Add rule for `main`
2. Enable **Require a pull request before merging**
3. Enable **Require status checks to pass before merging**
4. Enable **Require branches to be up to date before merging**
5. Select the four checks above
6. Do **not** allow administrators to bypass for this redesign phase (optional but preferred)

PR CI uses ephemeral Postgres in kind — Supabase secrets are **not** required for merge gates.
