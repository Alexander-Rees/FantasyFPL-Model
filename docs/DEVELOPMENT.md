# Development Guide

## Running Tests

### Backend Tests

```bash
cd backend
./mvnw test
```

### Run Specific Test Class

```bash
./mvnw test -Dtest=PlayerDataServiceTest
```

### Run Tests with Coverage

```bash
./mvnw test jacoco:report
# View coverage report: open backend/target/site/jacoco/index.html
```

## Testing Strategy

### Unit Tests
- **Location**: `backend/src/test/java/com/example/demo/service/`
- **Purpose**: Test individual service methods in isolation
- **Example**: `PlayerDataServiceTest.java`

### Controller Tests
- **Location**: `backend/src/test/java/com/example/demo/controller/`
- **Purpose**: Test REST endpoints with mocked dependencies
- **Example**: `PlayerV1ControllerTest.java`

### Integration Tests
- **Location**: `backend/src/test/java/com/example/demo/integration/`
- **Purpose**: Test full request flow with real database
- **Uses**: H2 in-memory database for fast tests

## Test Profiles

Tests use the `test` profile with:
- H2 in-memory database (no MySQL required)
- Simple cache (no Redis required)
- Disabled Flyway migrations
- Reduced logging

## Verification Script

Run the system verification script to test all endpoints:

```bash
./scripts/verify_system.sh
```

This script tests:
- Service health endpoints
- API endpoints
- Monitoring endpoints
- Documentation endpoints

## Code Quality

### Linting
```bash
# Check for linting errors
cd backend
./mvnw checkstyle:check
```

### Format Code
```bash
cd backend
./mvnw formatter:format
```

## Debugging

### Enable Debug Logging

Add to `application.properties`:
```properties
logging.level.com.example.demo=DEBUG
logging.level.org.springframework.web=DEBUG
```

### Run with Debug Port

```bash
./mvnw spring-boot:run -Dspring-boot.run.jvmArguments="-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=5005"
```

Then attach debugger to port 5005.

## Common Issues

### Tests Failing with Database Connection
- **Solution**: Tests use H2, not MySQL. Check `application-test.properties`.

### Redis Connection Errors in Tests
- **Solution**: Tests use simple cache. Check test profile configuration.

### Port Already in Use
- **Solution**: Kill existing processes or change ports in `application.properties`.

