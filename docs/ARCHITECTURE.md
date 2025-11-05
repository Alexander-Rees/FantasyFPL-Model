# FPL AI Optimization System - Architecture

## Overview

A production-ready microservices architecture for Fantasy Premier League team optimization with ML-powered recommendations.

## System Components

### Services

1. **backend-api** (Spring Boot 3.2, Java 17)
   - Port: 8081
   - Responsibilities: User authentication, team management, player data, optimization orchestration
   - Database: MySQL (via JPA/Hibernate)
   - Cache: Redis

2. **flask-ml** (Python 3.11, Flask)
   - Port: 5001
   - Responsibilities: ML model inference, optimization algorithms
   - Database: MySQL (read-only)
   - Cache: Redis

3. **frontend** (React, Node 20)
   - Port: 3000 (dev) / 80 (docker)
   - Responsibilities: User interface, team visualization

4. **mysql** (MySQL 8.0)
   - Port: 3306
   - Single source of truth for users, teams, players

5. **redis** (Redis 7-alpine)
   - Port: 6379
   - Caching layer, idempotency storage

## API Contracts

### Versioning

All public APIs use `/api/v1/*` prefix. Legacy endpoints (`/api/*`) are deprecated.

### Endpoints

**Public:**
- `POST /api/v1/auth/login` - JWT authentication
- `GET /api/v1/players?page=&size=&team=&position=&gw=` - Paginated player list
- `POST /api/v1/team/optimize?userId=&Idempotency-Key=` - Team optimization

**Internal (backend-api → flask-ml):**
- `POST http://flask-ml:5001/_ml/optimize` - ML optimization (requires `X-Internal-Token`)

**Monitoring:**
- Backend: `/actuator/health`, `/actuator/metrics`, `/actuator/prometheus`
- Flask: `/health`, `/metrics`

## Request Flow

```
1. User → Frontend → backend-api (/api/v1/team/optimize)
2. backend-api → flask-ml (/_ml/optimize) with X-Internal-Token
3. flask-ml → Redis (check cache)
4. flask-ml → MySQL (if cache miss, read player data)
5. flask-ml → ML Model → optimization result
6. flask-ml → Redis (cache result)
7. flask-ml → backend-api (return JSON)
8. backend-api → Redis (idempotency check if Idempotency-Key provided)
9. backend-api → Frontend (return OptimizeResponseDTO)
```

## Caching Strategy

### Cache Keys & TTLs

- `players:all` - TTL 300s (5 min) - All player list
- `optimization:<hash>` - TTL 1800s (30 min) - Optimization results
- `idempotency:<key>` - TTL 300s (5 min) - Idempotency responses

### Cache Invalidation

- Manual eviction via `@CacheEvict` on data updates
- Automatic expiration via TTLs

## Resilience Patterns

### Circuit Breaker (Resilience4j)

- **Name**: `flaskMl`
- **Failure Threshold**: 50% over 10 requests
- **Wait Duration**: 30s
- **Fallback**: Returns to `createFallbackOptimization` method

### Retry

- **Max Attempts**: 2
- **Wait Duration**: 100ms
- **Retry On**: `ResourceAccessException`, `SocketTimeoutException`

### Bulkhead

- **Max Concurrent Calls**: 10
- Prevents thread pool exhaustion

## Security Model

### Authentication

- **JWT Tokens**: User authentication via `/api/v1/auth/login`
- **Service-to-Service**: `X-Internal-Token` header for backend-api ↔ flask-ml

### CORS

- Allowed Origins: `CORS_ALLOWED_ORIGINS` env var (default: localhost:3000, localhost:8081)
- Allowed Headers: `Authorization`, `Content-Type`, `X-Request-Id`, `Idempotency-Key`

### Secrets Management

All secrets via environment variables:
- `DB_PASSWORD`, `JWT_SECRET`, `INTERNAL_API_TOKEN`, `REDIS_PASSWORD`
- Never committed to git (`.env` in `.gitignore`)

## Failure Modes & Resilience

### Flask ML Unavailable

1. Circuit breaker opens after 50% failures
2. Fallback to `createFallbackOptimization` (basic heuristic)
3. Returns valid response without ML optimization

### Redis Unavailable

- Services degrade gracefully (cache misses)
- All requests hit database/Flask directly
- No data loss, only performance impact

### Database Unavailable

- Health checks fail
- Circuit breaker prevents cascading failures
- Services report DOWN status via Actuator

## Observability

### Health Checks

- **Liveness**: `/actuator/health` - Is service running?
- **Readiness**: Includes DB, Redis, Flask dependency checks

### Metrics

- **Backend**: Prometheus format at `/actuator/prometheus`
- **Flask**: Prometheus format at `/metrics`
- Cache hits/misses, request latency, circuit breaker state

### Logging

- Structured JSON logs (Logback)
- `X-Request-Id` propagated across services
- Correlation IDs in MDC for tracing

## Deployment

### Local Development

```bash
make up  # Starts all services via docker-compose
```

### Production

- Services containerized (multi-stage Dockerfiles)
- Non-root users in containers
- Environment-specific configs (`application-docker.properties`)
- Health checks for orchestration (K8s/Docker Swarm ready)

## Schema Migrations

- **Flyway**: Versioned migrations in `src/main/resources/db/migration/`
- **Baseline**: `V1__init.sql` creates user, player, team tables
- **DDL Auto**: Disabled in production profiles (use `validate`)

