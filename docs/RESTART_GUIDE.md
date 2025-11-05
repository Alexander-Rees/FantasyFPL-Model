# How to Restart Spring Boot

## Quick Restart

### Method 1: Stop and Restart (Recommended)

1. **Find the Spring Boot process:**
   ```bash
   ps aux | grep -i "DemoApplication\|spring-boot:run" | grep -v grep
   ```

2. **Stop the process:**
   - Find the terminal where Spring Boot is running
   - Press `Ctrl+C` to stop it gracefully
   - Or kill the process:
     ```bash
     pkill -f "DemoApplication"
     ```

3. **Restart:**
   ```bash
   cd backend
   ./mvnw spring-boot:run
   ```

### Method 2: Kill Process and Restart

```bash
# Kill Spring Boot process
pkill -f "DemoApplication"

# Wait a moment
sleep 2

# Restart
cd backend
./mvnw spring-boot:run
```

### Method 3: Using Port (if process is stuck)

```bash
# Find process on port 8081
lsof -ti:8081

# Kill it
kill -9 $(lsof -ti:8081)

# Restart
cd backend
./mvnw spring-boot:run
```

## Verify Restart

After restarting, test these endpoints:

```bash
# Health check
curl http://localhost:8081/actuator/health

# API endpoint
curl "http://localhost:8081/api/v1/players?page=0&size=5"

# Swagger UI
open http://localhost:8081/swagger-ui.html
```

## Restart with Different Profile

```bash
cd backend
SPRING_PROFILES_ACTIVE=docker ./mvnw spring-boot:run
```

## Troubleshooting

### Port Already in Use

```bash
# Find what's using port 8081
lsof -i:8081

# Kill it
kill -9 $(lsof -ti:8081)
```

### Process Won't Stop

```bash
# Force kill
pkill -9 -f "DemoApplication"
```

### Changes Not Reflecting

1. Make sure you stopped the old process
2. Clean and rebuild:
   ```bash
   cd backend
   ./mvnw clean spring-boot:run
   ```

## Using Docker Compose (Alternative)

If using Docker Compose, restart is simpler:

```bash
cd infra
docker compose restart backend-api

# Or rebuild and restart
docker compose up -d --build backend-api
```

