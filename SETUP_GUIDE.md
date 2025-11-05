# Quick Setup Guide - Get Everything Working Now

## ✅ Good News: No Environment Variables Needed for Local Dev!

Your application has **sensible defaults** that work out of the box for local development. You don't need to set any environment variables right now.

### Default Values (Already Working)

- **Database**: `localhost:3306`, user `root`, password `NewPassword`, database `fantasy_soccer`
- **Redis**: `localhost:6379` (optional - works without it)
- **Internal API Token**: `dev-internal-token`
- **Flask API**: `http://localhost:5001`

## 🚀 What to Do Right Now

### Option 1: Local Development (No Docker)

**1. Make sure MySQL is running with the default database:**

```bash
# If MySQL is already set up with:
# - Database: fantasy_soccer
# - User: root
# - Password: NewPassword
# Then you're good! Skip to step 2.

# Otherwise, connect to MySQL and create:
mysql -u root -p
CREATE DATABASE IF NOT EXISTS fantasy_soccer;
# Make sure root user can access it
```

**2. Restart your Spring Boot backend (this is the key fix):**

```bash
# Stop the current backend process (Ctrl+C in the terminal running it)
# Then restart it:
cd backend
./mvnw spring-boot:run
```

**3. Your Flask API should already be running** (check with `curl http://localhost:5001/health`)

**4. Test everything:**

```bash
# Test Flask health
curl http://localhost:5001/health

# Test Spring Boot Actuator (after restart)
curl http://localhost:8081/actuator/health

# Test new API endpoints (after restart)
curl "http://localhost:8081/api/v1/players?page=0&size=5"

# Test Swagger UI (after restart)
open http://localhost:8081/swagger-ui.html
```

### Option 2: Docker Compose (Recommended for Full Stack)

**1. Create `.env` file in the root directory (optional, defaults work):**

```bash
# Create .env file with minimal config
cat > .env << 'EOF'
DB_PASSWORD=NewPassword
DB_NAME=fantasy_soccer
DB_USER=root
DB_HOST=localhost

INTERNAL_API_TOKEN=dev-internal-token
JWT_SECRET=your-jwt-secret-change-in-production

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
EOF

# Or just use defaults - no .env file needed!
```

**2. Start everything with Docker Compose:**

```bash
cd infra
make up
# Or: docker compose up -d
```

**3. Wait for services to start (30 seconds), then test:**

```bash
curl http://localhost:8081/actuator/health
curl http://localhost:5001/health
```

## 📝 Optional: Set Environment Variables

If you want to customize settings (different database, passwords, etc.), you can:

**For Local Development:**

1. Create a `.env` file (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

2. **Spring Boot** will read env vars automatically
   ```bash
   # Export in your shell or create .env file
   export DB_PASSWORD=mycustompassword
   export INTERNAL_API_TOKEN=my-custom-token
   ```

3. **Flask** reads from environment variables:
   ```bash
   export DB_PASSWORD=mycustompassword
   export INTERNAL_API_TOKEN=my-custom-token
   python app_with_db.py
   ```

## 🔧 Troubleshooting

### "Actuator endpoints not found (404)"
- **Fix**: Restart Spring Boot backend - Actuator was just added

### "API v1 endpoints returning 403"
- **Fix**: Restart Spring Boot backend - security config was updated

### "Redis unavailable"
- **Not a problem!** Cache degrades gracefully. Everything works without Redis.
- To enable Redis: Install locally or use Docker Compose

### "Database connection failed"
- Check MySQL is running: `mysql -u root -p`
- Verify database exists: `SHOW DATABASES;`
- Check password matches default or your env var

## ✅ Quick Checklist

- [ ] MySQL running with `fantasy_soccer` database
- [ ] Spring Boot restarted (to pick up new config)
- [ ] Flask API running on port 5001
- [ ] Frontend running on port 3000 (optional)

## 🎯 Test Your Setup

After restarting Spring Boot, these should all work:

```bash
# Health checks
curl http://localhost:8081/actuator/health
curl http://localhost:5001/health

# API endpoints
curl "http://localhost:8081/api/v1/players?page=0&size=5"
curl -X POST "http://localhost:8081/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Documentation
open http://localhost:8081/swagger-ui.html
```

**That's it!** You're ready to go. No environment variables needed for local development. 🎉

