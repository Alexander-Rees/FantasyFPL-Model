# Supabase Database Setup Guide

This guide will walk you through setting up a PostgreSQL database on Supabase and configuring your GitHub repository secrets for the data ingestion workflow.

## Step 1: Create a PostgreSQL Database on Supabase

1. **Log in to Supabase**: Go to [https://supabase.com](https://supabase.com) and log in to your account.
2. **Create a New Project**:
   - From your dashboard, click "New Project".
   - Enter a project name (e.g., `fantasy-soccer`).
   - Enter a database password (save this - you'll need it later).
   - Select a region closest to your users or GitHub Actions runners (e.g., "US East (N. Virginia)").
   - Click "Create new project".
3. **Wait for Setup**: Supabase will provision your PostgreSQL database (this takes a few minutes).

## Step 2: Get Connection Details from Supabase

Once your Supabase project is ready:

1. **Navigate to your Project**: From your Supabase dashboard, click on your project.
2. **Go to Settings → Database**:
   - Click "Settings" in the left sidebar.
   - Click "Database" in the settings menu.
3. **Note the Connection Details**: You'll find:
   - **Host**: `db.brettblayvzvgswearre.supabase.co` (or similar, with `db.` prefix)
   - **Port**: `5432` (default PostgreSQL port)
   - **Database**: `postgres` (default) or your custom database name
   - **User**: `postgres` (default)
   - **Password**: The password you set when creating the project (or reset it here)

## Step 3: Initialize the Database Schema (Flyway Migrations)

Your Spring Boot backend is configured to use [Flyway](https://flywaydb.org/) for database migrations. When the backend service starts and connects to a new, empty database, Flyway will automatically apply the necessary schema.

**To initialize the schema:**

- **Deploy your Spring Boot Backend**: Once your Supabase database is ready and GitHub secrets are set, you can deploy your Spring Boot backend (e.g., via Docker Compose pointing to the Supabase DB, or directly on a cloud service). Flyway will run on startup.
- **Manual Run (Optional)**: If you want to run migrations manually, you would typically connect to the Supabase database using a PostgreSQL client (like pgAdmin, DBeaver, or the `psql` CLI) and execute the SQL scripts located in `backend/src/main/resources/db/migration/`. However, letting Spring Boot handle it is usually simpler.

## Step 4: Add GitHub Secrets

To securely use your Supabase database credentials in GitHub Actions, you need to add them as repository secrets.

1. **Go to your GitHub Repository**: Open your `fantasy-soccer-app` repository on GitHub.
2. **Navigate to Secrets**: Go to `Settings` → `Secrets and variables` → `Actions`.
3. **Add New Repository Secrets**: Click "New repository secret" and add the following, using the values you obtained from Supabase:
   - **Name**: `DB_HOST` → **Value**: Your Supabase database host (e.g., `db.brettblayvzvgswearre.supabase.co`)
   - **Name**: `DB_PORT` → **Value**: `5432` (default PostgreSQL port)
   - **Name**: `DB_USER` → **Value**: `postgres` (default)
   - **Name**: `DB_PASSWORD` → **Value**: Your Supabase database password (the one you set when creating the project)
   - **Name**: `DB_NAME` → **Value**: `postgres` (default) or your custom database name

## Step 5: Test the Connection

Once you've added the secrets, you can test the GitHub Actions workflow:

1. **Go to your GitHub Repository**: Open your repository on GitHub.
2. **Go to Actions Tab**: Click "Actions" in the top navigation.
3. **Find "FPL Data Ingestion" Workflow**: Look for the workflow named "FPL Data Ingestion".
4. **Run Workflow Manually**: Click "Run workflow" → "Run workflow" (manual trigger).

This will test if the connection works and the ingestion script runs successfully.

## Step 6: Update Local Development (Optional)

If you want to use Supabase for local development instead of Docker Compose:

1. **Update `backend/src/main/resources/application.properties`**:
   ```properties
   spring.datasource.url=jdbc:postgresql://db.brettblayvzvgswearre.supabase.co:5432/postgres
   spring.datasource.username=postgres
   spring.datasource.password=YOUR_DATABASE_PASSWORD
   ```

2. **Or use environment variables**:
   ```bash
   export SPRING_DATASOURCE_URL="jdbc:postgresql://db.brettblayvzvgswearre.supabase.co:5432/postgres"
   export SPRING_DATASOURCE_USERNAME="postgres"
   export SPRING_DATASOURCE_PASSWORD="YOUR_DATABASE_PASSWORD"
   ```

## Troubleshooting

- **Connection refused**: Check that Supabase database is running and the host/port are correct. Make sure you're using the `db.` prefix in the host (e.g., `db.brettblayvzvgswearre.supabase.co`).
- **Authentication failed**: Verify the username and password in GitHub secrets. Make sure you're using the database password, not the API key.
- **Database not found**: Make sure the database name matches exactly (usually `postgres`).
- **Schema errors**: Ensure Flyway migrations have run or run them manually.
- **SSL connection required**: Supabase requires SSL connections. The Spring Boot application should handle this automatically, but if you encounter SSL errors, you may need to add `?sslmode=require` to the connection URL.

## Next Steps

Once you have completed these steps, your Supabase PostgreSQL database will be set up and ready for use by your application and GitHub Actions. You can then proceed to:

- **Test the Data Ingestion Workflow**: Manually trigger the `FPL Data Ingestion` GitHub Actions workflow to populate your new database with player data.
- **Deploy your Backend**: Update your backend's `application.properties` or environment variables to point to the Supabase database if you're running it outside Docker Compose, or ensure your Docker Compose setup uses the new `DB_HOST` and `DB_PORT` for the backend service.

