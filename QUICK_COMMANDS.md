# Quick Commands Reference

## Restart Spring Boot

```bash
# Method 1: Stop in terminal (Ctrl+C) then:
cd backend && ./mvnw spring-boot:run

# Method 2: Kill and restart
pkill -f "DemoApplication" && cd backend && ./mvnw spring-boot:run
```

## CI/CD Pipeline

**Location:** `.github/workflows/`

**Workflows:**
- `ci.yml` - Main CI pipeline (tests, builds, Docker images)
- `security.yml` - Security scanning (CodeQL, Dependabot)

**View Results:**
- GitHub → Actions tab
- Or: https://github.com/YOUR_USERNAME/YOUR_REPO/actions

## Common Commands

```bash
# Restart Spring Boot
cd backend && ./mvnw spring-boot:run

# Run tests
cd backend && ./mvnw test

# Verify system
./scripts/verify_system.sh

# Start with Docker Compose
cd infra && make up

# Check what's running
ps aux | grep -E "java|python|node" | grep -v grep
```

## Check if Services are Running

```bash
# Check Spring Boot
curl http://localhost:8081/actuator/health

# Check Flask
curl http://localhost:5001/health

# Check Frontend
curl http://localhost:3000
```
