# CI/CD Pipeline Documentation

## Overview

We use **GitHub Actions** for CI/CD with two main workflows:

### 1. CI Pipeline (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` branch
- Pull requests to `main` branch

**Jobs:**

#### Backend Job
- Sets up JDK 17
- Runs tests: `./mvnw test -q`
- Builds JAR: `./mvnw package -DskipTests -q`
- Builds Docker image: `docker build -t backend-api:test`

#### Flask Job
- Sets up Python 3.11
- Installs dependencies
- Runs tests (if available): `pytest`
- Builds Docker image: `docker build -t flask-ml:test`

#### Frontend Job
- Sets up Node.js 20
- Installs dependencies: `npm ci`
- Runs linting (if available)
- Builds production bundle: `npm run build`
- Builds Docker image: `docker build -t frontend:test`

#### Integration Job
- Runs after all individual jobs complete
- Starts services with Docker Compose
- Tests health endpoints
- Tests API endpoints
- Cleans up services

### 2. Security Scan (`.github/workflows/security.yml`)

**Triggers:**
- Push to `main` branch
- Pull requests to `main` branch
- Weekly schedule (Sunday 00:00 UTC)

**Jobs:**

#### CodeQL Analysis
- Scans Java, JavaScript, and Python code
- Runs security analysis
- Reports vulnerabilities

#### Dependabot Check
- Checks for outdated dependencies
- Backend: Maven dependency updates
- Frontend: npm dependency updates

## Viewing CI/CD Results

1. **GitHub UI:**
   - Go to your repository
   - Click "Actions" tab
   - See workflow runs and results

2. **Status Badges:**
   - Add to README: `![CI](https://github.com/your-repo/actions/workflows/ci.yml/badge.svg)`

## Manual Trigger

You can manually trigger workflows:
1. Go to "Actions" tab in GitHub
2. Select the workflow
3. Click "Run workflow"

## Workflow Status

- ✅ **Green**: All checks passed
- ❌ **Red**: Some checks failed
- 🟡 **Yellow**: Workflow in progress

## Local Testing

Test the CI pipeline locally:

```bash
# Test backend build
cd backend
./mvnw test
./mvnw package -DskipTests

# Test Flask build
cd flask-api
pip install -r requirements.txt

# Test frontend build
cd frontend
npm ci
npm run build

# Test Docker builds
docker build -t backend-api:test backend/
docker build -t flask-ml:test flask-api/
docker build -t frontend:test frontend/
```

