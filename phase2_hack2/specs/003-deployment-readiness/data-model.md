# Data Model: Deployment Readiness

**Feature**: 003-deployment-readiness
**Date**: 2026-02-05
**Purpose**: Data structures for operational readiness features

## Overview

This feature does not introduce new persistent data entities. It enhances operational aspects of the existing system with configuration validation, health monitoring, and structured logging. The data structures defined here are transient (runtime only) and used for operational visibility.

---

## Existing Entities (No Changes)

### Task
- **Location**: `backend/src/models/task.py`
- **Status**: No changes required
- **Description**: Existing task entity remains unchanged

### User
- **Location**: Better Auth managed (external to application)
- **Status**: No changes required
- **Description**: User authentication handled by Better Auth

---

## New Transient Structures (Runtime Only)

### 1. Health Check Response

**Purpose**: Represent backend service health status for monitoring and operational visibility

**Schema**:
```python
class HealthCheckResponse(BaseModel):
    status: Literal["healthy", "unhealthy", "degraded"]
    database: Literal["connected", "disconnected"]
    timestamp: str  # ISO 8601 format
    error: Optional[str] = None  # Present only when unhealthy
```

**Fields**:
- `status`: Overall service health status
  - `healthy`: All systems operational
  - `unhealthy`: Critical failure (database disconnected)
  - `degraded`: Partial functionality (future use)
- `database`: Database connectivity status
  - `connected`: Database reachable and responsive
  - `disconnected`: Database unreachable or unresponsive
- `timestamp`: UTC timestamp of health check in ISO 8601 format
- `error`: Optional error message (only when status is unhealthy)

**Validation Rules**:
- `status` must be one of: "healthy", "unhealthy", "degraded"
- `database` must be one of: "connected", "disconnected"
- `timestamp` must be valid ISO 8601 format
- `error` is optional, present only when status != "healthy"

**Example Responses**:
```json
// Healthy
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-02-05T12:34:56.789Z"
}

// Unhealthy
{
  "status": "unhealthy",
  "database": "disconnected",
  "timestamp": "2026-02-05T12:34:56.789Z",
  "error": "Database connection failed"
}
```

**Storage**: Not persisted, generated on-demand per request

---

### 2. Structured Log Entry

**Purpose**: Represent operational events in machine-parsable format for debugging and monitoring

**Schema**:
```python
class LogEntry(TypedDict):
    timestamp: str          # ISO 8601 format
    level: str              # INFO, WARNING, ERROR
    message: str            # Human-readable message
    module: str             # Python module name
    function: str           # Function name
    event_type: str         # auth_failure, db_error, etc.
    user_id: Optional[str]  # User ID (when applicable)
    resource_id: Optional[str]  # Resource ID (when applicable)
    exception: Optional[str]  # Exception traceback (when applicable)
```

**Fields**:
- `timestamp`: UTC timestamp in ISO 8601 format
- `level`: Log severity (INFO, WARNING, ERROR)
- `message`: Human-readable description of the event
- `module`: Python module where event occurred
- `function`: Function name where event occurred
- `event_type`: Categorized event type for filtering
  - `auth_failure`: Authentication failure (invalid/expired JWT)
  - `authz_failure`: Authorization failure (wrong task owner)
  - `db_error`: Database connection or query error
  - `validation_error`: Input validation failure
  - `startup_error`: Configuration or startup failure
- `user_id`: User ID involved (sanitized, no PII)
- `resource_id`: Resource ID involved (task ID, etc.)
- `exception`: Exception traceback (sanitized, no sensitive data)

**Validation Rules**:
- `timestamp` must be valid ISO 8601 format
- `level` must be one of: INFO, WARNING, ERROR
- `event_type` must be from predefined list
- `user_id` and `resource_id` are optional (present when applicable)
- `exception` must not contain sensitive data (tokens, passwords, credentials)

**Example Log Entries**:
```json
// Authentication failure
{
  "timestamp": "2026-02-05T12:34:56.789Z",
  "level": "WARNING",
  "message": "JWT token expired",
  "module": "api.dependencies",
  "function": "get_current_user",
  "event_type": "auth_failure",
  "user_id": null
}

// Authorization failure
{
  "timestamp": "2026-02-05T12:34:56.789Z",
  "level": "WARNING",
  "message": "User attempted to access task owned by another user",
  "module": "api.routes.tasks",
  "function": "get_task",
  "event_type": "authz_failure",
  "user_id": "user-123",
  "resource_id": "task-456"
}

// Database error
{
  "timestamp": "2026-02-05T12:34:56.789Z",
  "level": "ERROR",
  "message": "Database connection failed",
  "module": "core.database",
  "function": "get_session",
  "event_type": "db_error",
  "exception": "OperationalError: could not connect to server"
}
```

**Storage**: Written to stdout/stderr, not persisted by application

**Security Constraints**:
- ❌ MUST NOT log JWT tokens or passwords
- ❌ MUST NOT log full database connection strings with credentials
- ❌ MUST NOT log sensitive user data (email, password hash)
- ✅ MAY log user IDs (non-sensitive identifiers)
- ✅ MAY log resource IDs (task IDs)
- ✅ MAY log sanitized error messages

---

### 3. Configuration Settings

**Purpose**: Validated environment configuration loaded at startup

**Schema**:
```python
class Settings(BaseSettings):
    # Required environment variables
    better_auth_secret: str
    database_url: str
    cors_origins: str

    # Optional with defaults
    debug: bool = False
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False
```

**Fields**:
- `better_auth_secret`: JWT signing secret (min 32 chars)
- `database_url`: PostgreSQL connection string
- `cors_origins`: Comma-separated allowed origins
- `debug`: Enable debug mode (default: False)
- `environment`: Environment name (default: "development")

**Validation Rules**:
- `better_auth_secret`: Required, non-empty string
- `database_url`: Required, valid PostgreSQL connection string format
- `cors_origins`: Required, non-empty string
- `debug`: Boolean (true/false)
- `environment`: String (development/staging/production)

**Validation Behavior**:
- Pydantic validates at startup
- Missing required fields raise ValidationError with clear message
- Application fails fast before accepting requests

**Storage**: Loaded from environment variables, held in memory

---

## Data Flow

### Health Check Flow
```
1. GET /health request received
2. Backend queries database (SELECT 1)
3. HealthCheckResponse generated based on result
4. Response returned (200 OK or 503 Service Unavailable)
5. No persistence
```

### Logging Flow
```
1. Operational event occurs (auth failure, db error, etc.)
2. LogEntry structure created with sanitized data
3. Entry formatted as JSON
4. Written to stdout/stderr
5. No persistence (external log aggregation optional)
```

### Configuration Flow
```
1. Application startup
2. Settings loaded from environment variables
3. Pydantic validates all required fields
4. If validation fails: raise error, exit immediately
5. If validation passes: continue startup
6. Settings held in memory for application lifetime
```

---

## Relationships

**No database relationships**: This feature does not introduce persistent entities or foreign keys.

**Operational relationships**:
- Health check queries database to verify connectivity
- Logging references user IDs and resource IDs from existing entities
- Configuration settings used by existing authentication and database modules

---

## Migration Requirements

**Database migrations**: None required (no schema changes)

**Configuration migrations**:
- Update .env.example to remove real credentials (security fix)
- No changes to actual .env files (user-managed)

---

## Summary

This feature introduces three transient data structures for operational purposes:

1. **HealthCheckResponse**: Runtime health status (not persisted)
2. **LogEntry**: Structured log records (written to stdout/stderr)
3. **Settings**: Validated configuration (loaded at startup)

No persistent data entities are added. No database schema changes required. All structures are runtime-only and support operational visibility without modifying the core data model.
