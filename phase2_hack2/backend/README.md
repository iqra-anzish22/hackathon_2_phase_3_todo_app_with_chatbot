# Multi-User Todo Backend

FastAPI backend for the Multi-User Todo Web Application with JWT authentication, PostgreSQL storage, and deployment readiness features.

## Features

- ✅ JWT-based authentication with Better Auth
- ✅ Multi-user task isolation
- ✅ Environment variable validation (fail-fast on startup)
- ✅ Health check endpoint for monitoring
- ✅ Structured JSON logging for operational visibility
- ✅ Comprehensive error handling

## Prerequisites

- Python 3.11+
- Neon PostgreSQL account (or local PostgreSQL)
- Virtual environment tool (venv)

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your actual values
```

4. Run database migrations:
```bash
alembic upgrade head
```

## Running the Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

API documentation: http://localhost:8000/docs

## Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── models/              # SQLModel database models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── api/                 # API routes and dependencies
│   └── core/                # Configuration, database, security
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variable template
```

## Environment Variables

**All required variables must be set before starting the server. The application will fail fast with clear error messages if any are missing.**

### Required Variables

- `BETTER_AUTH_SECRET`: JWT signing secret (must match frontend, min 32 chars)
  - Generate with: `openssl rand -base64 32`
- `DATABASE_URL`: PostgreSQL connection string
  - Format: `postgresql+asyncpg://user:password@host/database?sslmode=require`
- `CORS_ORIGINS`: Allowed CORS origins (frontend URL)
  - Example: `http://localhost:3000`

### Optional Variables

- `DEBUG`: Enable debug mode (default: `false`)
- `ENVIRONMENT`: Environment name (default: `development`)

**Example .env file:**
```bash
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-here
DATABASE_URL=postgresql+asyncpg://user:password@host.region.aws.neon.tech/database?sslmode=require
CORS_ORIGINS=http://localhost:3000
DEBUG=true
ENVIRONMENT=development
```

## API Endpoints

### Public Endpoints

- `GET /` - Root endpoint (API info)
- `GET /health` - Health check endpoint (database connectivity)
  - Returns 200 OK when healthy, 503 when unhealthy
  - Does NOT require authentication

### Protected Endpoints

All task endpoints require JWT authentication via `Authorization: Bearer <token>` header.

- `GET /api/tasks` - List user's tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/complete` - Toggle task completion

## Operational Features

### Environment Validation

The application validates all required environment variables at startup and fails fast with clear error messages if any are missing:

```
❌ CONFIGURATION ERROR: Missing or invalid environment variables
================================================================================

  Missing required environment variable: BETTER_AUTH_SECRET
  → Add BETTER_AUTH_SECRET to your .env file or environment

================================================================================
📖 See backend/.env.example for required configuration
================================================================================
```

### Health Check

Monitor service health and database connectivity:

```bash
curl http://localhost:8000/health
```

**Healthy response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-02-05T12:34:56.789Z"
}
```

**Unhealthy response (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "timestamp": "2026-02-05T12:34:56.789Z",
  "error": "Database connection failed"
}
```

### Structured Logging

All operational events are logged in JSON format for machine parsing:

```json
{
  "timestamp": "2026-02-05T12:34:56.789Z",
  "level": "WARNING",
  "message": "JWT token expired",
  "module": "api.dependencies",
  "function": "get_current_user",
  "event_type": "auth_failure"
}
```

**Event types:**
- `auth_failure`: Authentication failures (invalid/expired JWT)
- `authz_failure`: Authorization failures (wrong task owner)
- `db_error`: Database connection or query errors
- `startup_error`: Configuration or startup failures

**Security:** Logs do NOT contain sensitive data (tokens, passwords, credentials).

## Development

Run tests:
```bash
pytest tests/ -v
```

Format code:
```bash
black src/
```

Lint code:
```bash
flake8 src/
```
