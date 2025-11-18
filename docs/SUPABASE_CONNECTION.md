# Supabase Connection Setup

This document explains how to connect to your Supabase PostgreSQL database.

## Connection Details

### Option 1: Connection Pooler (Recommended - Works with IPv4)
- **Host**: Check Supabase Dashboard → Settings → Database → Connection Pooler
- **Port**: `6543` (connection pooler port) or `5432` (transaction mode)
- **Database**: `postgres`
- **Username**: `postgres.[project-ref]` (with project ref) or `postgres`
- **Password**: `YOUR_DATABASE_PASSWORD` (get from Supabase Settings → Database)

### Option 2: Direct Connection (IPv6 only - requires IPv6 support)
- **Host**: `db.brettblayvzvgswearre.supabase.co`
- **Port**: `5432`
- **Database**: `postgres`
- **Username**: `postgres`
- **Password**: `YOUR_DATABASE_PASSWORD` (get from Supabase Settings → Database)

**Note**: Direct connections only work with IPv6. Use the Connection Pooler for IPv4 compatibility.

## Important: Password URL Encoding

The password contains special characters (`+`, `@`, `!`) that need to be URL-encoded when used in connection strings:

- `+` → `%2B`
- `@` → `%40`
- `!` → `%21`

**URL-encoded password**: `YOUR_PASSWORD_URL_ENCODED` (encode `+` → `%2B`, `@` → `%40`, `!` → `%21`)

## Connection String Formats

### PostgreSQL Connection String (URL-encoded password)
```
postgresql://postgres:YOUR_PASSWORD_URL_ENCODED@db.brettblayvzvgswearre.supabase.co:5432/postgres
```

### JDBC Connection String (Spring Boot)
```
jdbc:postgresql://db.brettblayvzvgswearre.supabase.co:5432/postgres
```

**Note**: When using JDBC with separate username/password parameters (not in URL), use the password as-is without encoding.

### Python psycopg2 Connection
```python
import psycopg2

connection = psycopg2.connect(
    host='db.brettblayvzvgswearre.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='YOUR_DATABASE_PASSWORD'  # Use password as-is, no encoding needed
)
```

## Environment Variables

Create a `.env` file (copy from `env.example`) with:

```bash
DB_HOST=aws-1-us-east-1.pooler.supabase.com
DB_PORT=5432
DB_USER=postgres.brettblayvzvgswearre
DB_PASSWORD=YOUR_DATABASE_PASSWORD
DB_NAME=postgres
```

## GitHub Secrets

For GitHub Actions, add these secrets:
- `DB_HOST`: `aws-1-us-east-1.pooler.supabase.com` (get from Supabase Dashboard → Connection Pooler)
- `DB_PORT`: `5432`
- `DB_USER`: `postgres.brettblayvzvgswearre` (format: `postgres.[project-ref]`)
- `DB_PASSWORD`: `YOUR_DATABASE_PASSWORD` (get from Supabase dashboard)
- `DB_NAME`: `postgres`

## Testing the Connection

### Using psql (PostgreSQL CLI)
```bash
psql "postgresql://postgres:YOUR_PASSWORD_URL_ENCODED@db.brettblayvzvgswearre.supabase.co:5432/postgres"
```

### Using Python
```python
import psycopg2

try:
    conn = psycopg2.connect(
        host='db.brettblayvzvgswearre.supabase.co',
        port=5432,
        database='postgres',
        user='postgres',
        password='YOUR_DATABASE_PASSWORD'
    )
    print("✅ Connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## Security Notes

- ⚠️ **Never commit the `.env` file** - it contains sensitive credentials
- ⚠️ **Never commit the password** to version control
- ✅ Use environment variables for all credentials
- ✅ Use GitHub Secrets for CI/CD workflows

