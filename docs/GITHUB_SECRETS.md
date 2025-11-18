# GitHub Secrets Setup Guide

This guide explains how to add the required secrets to your GitHub repository for CI/CD and data ingestion workflows.

## Required Secrets

You need to add the following secrets to your GitHub repository for the workflows to work:

### Database Connection Secrets (Required for Data Ingestion & CI Integration Tests)

1. **DB_HOST**: `aws-1-us-east-1.pooler.supabase.com`
   - Your Supabase connection pooler hostname
   - Get this from: Supabase Dashboard → Settings → Database → Connection String → Session pooler
   - Format: `aws-[number]-[region].pooler.supabase.com`

2. **DB_PORT**: `5432`
   - Connection pooler port (5432 for transaction mode, 6543 for session mode)

3. **DB_USER**: `postgres.brettblayvzvgswearre`
   - Username format: `postgres.[project-ref]`
   - Get your project ref from Supabase Dashboard URL or connection string

4. **DB_PASSWORD**: `YOUR_DATABASE_PASSWORD`
   - Your Supabase database password (the one you set when creating the project)
   - ⚠️ **DO NOT** use the example password - get this from your Supabase dashboard

5. **DB_NAME**: `postgres`
   - Default database name (or your custom database name)

### Spring Boot Database Secrets (Optional - NOT NEEDED)

**You don't need to set these!** The Spring Boot backend automatically uses the `DB_*` secrets above. These are only needed if you want to override the defaults:

- **SPRING_DATASOURCE_URL** (Optional): Full JDBC connection string
  - Auto-constructed from `DB_HOST`, `DB_PORT`, `DB_NAME` if not set
  - Example: `jdbc:postgresql://aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require`

- **SPRING_DATASOURCE_USERNAME** (Optional): Uses `DB_USER` if not set
- **SPRING_DATASOURCE_PASSWORD** (Optional): Uses `DB_PASSWORD` if not set

## How to Add Secrets

1. **Go to your GitHub Repository**:
   - Navigate to your repository: `https://github.com/Alexander-Rees/FantasyFPL-Model`

2. **Open Settings**:
   - Click on "Settings" in the repository navigation bar

3. **Navigate to Secrets**:
   - In the left sidebar, click "Secrets and variables"
   - Click "Actions"

4. **Add New Repository Secret**:
   - Click "New repository secret"
   - For each secret:
     - **Name**: Enter the secret name (e.g., `DB_HOST`)
     - **Secret**: Enter the secret value (e.g., `aws-1-us-east-1.pooler.supabase.com`)
     - Click "Add secret"

5. **Repeat for all required secrets**:
   - Add the 5 required secrets: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
   - The Spring Boot secrets (`SPRING_DATASOURCE_*`) are optional and will use the same values

## Secret Values Summary

| Secret Name | Required | Value |
|------------|---------|-------|
| `DB_HOST` | ✅ **Yes** | `aws-1-us-east-1.pooler.supabase.com` (or your pooler hostname) |
| `DB_PORT` | ✅ **Yes** | `5432` |
| `DB_USER` | ✅ **Yes** | `postgres.brettblayvzvgswearre` (or `postgres.[your-project-ref]`) |
| `DB_PASSWORD` | ✅ **Yes** | `YOUR_DATABASE_PASSWORD` (get from Supabase dashboard) |
| `DB_NAME` | ✅ **Yes** | `postgres` |
| `SPRING_DATASOURCE_URL` | ❌ **No** | Auto-constructed from DB_* vars (don't set this) |
| `SPRING_DATASOURCE_USERNAME` | ❌ **No** | Uses DB_USER automatically (don't set this) |
| `SPRING_DATASOURCE_PASSWORD` | ❌ **No** | Uses DB_PASSWORD automatically (don't set this) |
| `INTERNAL_API_TOKEN` | ❌ **No** | Defaults to `dev-internal-token` (only set if you want a custom token) |

## Testing the Secrets

Once you've added the secrets, you can test them by:

1. **Manually trigger the Data Ingestion workflow**:
   - Go to "Actions" tab
   - Select "FPL Data Ingestion" workflow
   - Click "Run workflow" → "Run workflow"

2. **Check the workflow logs**:
   - The workflow should connect to Supabase and ingest player data
   - If successful, you'll see logs showing players being upserted

## Security Notes

- ⚠️ **Never commit secrets to the repository**
- ✅ Secrets are encrypted and only accessible to GitHub Actions
- ✅ Secrets are masked in workflow logs
- ✅ Only repository collaborators with write access can view/manage secrets

## Troubleshooting

- **Connection refused**: Check that `DB_HOST` uses the `db.` prefix
- **Authentication failed**: Verify `DB_PASSWORD` is correct (not the API key)
- **Database not found**: Ensure `DB_NAME` matches your Supabase database name

