# Logging Format Specification

**Feature**: 003-deployment-readiness
**Date**: 2026-02-05
**Version**: 1.0.0

## Overview

This document specifies the structured logging format for operational events in the backend service. All logs are written to stdout/stderr in JSON format for machine parsing and integration with log aggregation tools.

---

## Log Entry Structure

### Base Schema

All log entries follow this JSON structure:

```json
{
  "timestamp": "2026-02-05T12:34:56.789Z",
  "level": "ERROR",
  "message": "Human-readable description",
  "module": "api.routes.tasks",
  "function": "get_task",
  "event_type": "authz_failure",
  "user_id": "user-123",
  "resource_id": "task-456",
  "exception": "Optional exception traceback"
}
```

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | string | UTC timestamp in ISO 8601 format | `"2026-02-05T12:34:56.789Z"` |
| `level` | string | Log severity level | `"INFO"`, `"WARNING"`, `"ERROR"` |
| `message` | string | Human-readable event description | `"JWT token expired"` |
| `module` | string | Python module where event occurred | `"api.dependencies"` |
| `function` | string | Function name where event occurred | `"get_current_user"` |

### Optional Fields

| Field | Type | Description | When Present |
|-------|------|-------------|--------------|
| `event_type` | string | Categorized event type | All operational events |
| `user_id` | string | User identifier | When user context available |
| `resource_id` | string | Resource identifier | When resource involved |
| `exception` | string | Exception traceback | When exception occurs |

---

## Log Levels

### INFO
- **Purpose**: Informational messages about normal operations
- **Examples**: Application startup, configuration loaded
- **Usage**: Minimal - only for significant operational milestones

### WARNING
- **Purpose**: Potentially problematic situations that don't prevent operation
- **Examples**: Authentication failures, authorization denials
- **Usage**: Authentication/authorization failures, deprecated API usage

### ERROR
- **Purpose**: Error events that might still allow the application to continue
- **Examples**: Database connection failures, unhandled exceptions
- **Usage**: Database errors, unexpected exceptions, critical failures

---

## Event Types

### auth_failure
**Description**: Authentication failure (invalid or expired JWT token)

**Example**:
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

**When Logged**:
- Invalid JWT signature
- Expired JWT token
- Malformed JWT token
- Missing Authorization header

**Security**: MUST NOT log token values

---

### authz_failure
**Description**: Authorization failure (user lacks permission for resource)

**Example**:
```json
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
```

**When Logged**:
- User attempts to access another user's task
- User attempts to modify another user's task
- User attempts to delete another user's task

**Security**: MAY log user_id and resource_id (non-sensitive identifiers)

---

### db_error
**Description**: Database connection or query error

**Example**:
```json
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

**When Logged**:
- Database connection failures
- Query execution errors
- Transaction rollback errors

**Security**: MUST NOT log connection strings with credentials

---

### validation_error
**Description**: Input validation failure (Pydantic validation)

**Example**:
```json
{
  "timestamp": "2026-02-05T12:34:56.789Z",
  "level": "WARNING",
  "message": "Invalid input data: title is required",
  "module": "main",
  "function": "validation_exception_handler",
  "event_type": "validation_error"
}
```

**When Logged**:
- Pydantic validation errors (422 responses)
- Missing required fields
- Invalid field values

**Security**: MAY log field names and validation errors (no sensitive data)

---

### startup_error
**Description**: Configuration or startup failure

**Example**:
```json
{
  "timestamp": "2026-02-05T12:34:56.789Z",
  "level": "ERROR",
  "message": "Missing required environment variable: BETTER_AUTH_SECRET",
  "module": "core.config",
  "function": "__init__",
  "event_type": "startup_error"
}
```

**When Logged**:
- Missing environment variables
- Invalid configuration values
- Startup initialization failures

**Security**: MAY log variable names, MUST NOT log variable values

---

## Security Requirements

### MUST NOT Log (Sensitive Data)

❌ **JWT Tokens**
```json
// WRONG
{"message": "Invalid token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}

// CORRECT
{"message": "Invalid JWT token", "event_type": "auth_failure"}
```

❌ **Passwords**
```json
// WRONG
{"message": "Login failed for password: secret123"}

// CORRECT
{"message": "Authentication failed", "event_type": "auth_failure"}
```

❌ **Database Credentials**
```json
// WRONG
{"message": "Connection failed: postgresql://user:password@host/db"}

// CORRECT
{"message": "Database connection failed", "event_type": "db_error"}
```

❌ **Full Connection Strings**
```json
// WRONG
{"exception": "OperationalError: postgresql://user:pass@host/db"}

// CORRECT
{"exception": "OperationalError: could not connect to server"}
```

### MAY Log (Non-Sensitive Data)

✅ **User IDs** (non-sensitive identifiers)
```json
{"user_id": "user-123"}
```

✅ **Resource IDs** (task IDs, etc.)
```json
{"resource_id": "task-456"}
```

✅ **Sanitized Error Messages**
```json
{"exception": "OperationalError: could not connect to server"}
```

✅ **Field Names** (for validation errors)
```json
{"message": "Validation error: title is required"}
```

---

## Implementation

### Python Logger Configuration

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }

        # Add optional fields from extra
        if hasattr(record, 'event_type'):
            log_data['event_type'] = record.event_type
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'resource_id'):
            log_data['resource_id'] = record.resource_id

        # Add exception if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)

# Configure logger
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Usage Examples

**Authentication Failure**:
```python
logger.warning(
    "JWT token expired",
    extra={"event_type": "auth_failure"}
)
```

**Authorization Failure**:
```python
logger.warning(
    "User attempted to access task owned by another user",
    extra={
        "event_type": "authz_failure",
        "user_id": str(current_user.id),
        "resource_id": str(task_id)
    }
)
```

**Database Error**:
```python
try:
    await session.execute(query)
except Exception as e:
    logger.error(
        "Database query failed",
        extra={"event_type": "db_error"},
        exc_info=True
    )
```

---

## Log Output Destination

### Development
- **Destination**: stdout/stderr
- **Format**: JSON (one line per entry)
- **Viewing**: Terminal output or `uvicorn` logs

### Production
- **Destination**: stdout/stderr
- **Format**: JSON (one line per entry)
- **Aggregation**: External log aggregation tool (optional)
  - CloudWatch Logs
  - Datadog
  - Elasticsearch
  - Splunk

---

## Performance Considerations

### Overhead
- Target: <10ms per log entry
- Asynchronous logging where possible
- No blocking I/O for log writes

### Volume
- Log only significant events (not every request)
- Use appropriate log levels to control verbosity
- Avoid logging in tight loops

---

## Testing

### Validation Tests

**Test 1: JSON Format**
```python
def test_log_format():
    log_output = capture_log()
    log_entry = json.loads(log_output)
    assert "timestamp" in log_entry
    assert "level" in log_entry
    assert "message" in log_entry
```

**Test 2: No Sensitive Data**
```python
def test_no_token_in_logs():
    trigger_auth_failure()
    log_output = capture_log()
    assert "eyJ" not in log_output  # JWT prefix
    assert "Bearer" not in log_output
```

**Test 3: Event Types**
```python
def test_event_types():
    trigger_auth_failure()
    log_entry = json.loads(capture_log())
    assert log_entry["event_type"] == "auth_failure"
```

---

## Changelog

### Version 1.0.0 (2026-02-05)
- Initial structured logging specification
- JSON format with required and optional fields
- Event types: auth_failure, authz_failure, db_error, validation_error, startup_error
- Security requirements for sensitive data handling
