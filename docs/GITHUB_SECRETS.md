# GitHub Secrets Setup Guide

This guide explains how to add the required secrets to your GitHub repository for CI/CD and data ingestion workflows.

## Required Secrets

You need to add the following secrets to your GitHub repository for the workflows to work:

### Database Connection Secrets (for Data Ingestion)

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
   - Default database name (or your custom database name

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

5. **Repeat for all secrets**:
   - Add all 5 secrets listed above

## Secret Values Summary

| Secret Name | Value |
|------------|-------|
| `DB_HOST` | `aws-1-us-east-1.pooler.supabase.com` (or your pooler hostname) |
| `DB_PORT` | `5432` |
| `DB_USER` | `postgres.brettblayvzvgswearre` (or `postgres.[your-project-ref]`) |
| `DB_PASSWORD` | `YOUR_DATABASE_PASSWORD` (get from Supabase dashboard) |
| `DB_NAME` | `postgres` |

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

