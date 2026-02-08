# API Contract: Health Check Endpoint

**Feature**: 003-deployment-readiness
**Date**: 2026-02-05
**Version**: 1.0.0

## Endpoint Overview

**Purpose**: Provide operational visibility into backend service health and database connectivity for monitoring, load balancers, and operational verification.

**Endpoint**: `GET /health`
**Authentication**: None (public endpoint)
**Rate Limiting**: None

---

## Request

### HTTP Method
```
GET /health
```

### Headers
None required (public endpoint)

### Query Parameters
None

### Request Body
None (GET request)

### Example Request
```bash
curl -X GET http://localhost:8000/health
```

---

## Response

### Success Response (200 OK)

**Status Code**: `200 OK`

**Response Body**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-02-05T12:34:56.789Z"
}
```

**Schema**:
```typescript
{
  status: "healthy",
  database: "connected",
  timestamp: string  // ISO 8601 format
}
```

**Field Descriptions**:
- `status`: Overall service health status (always "healthy" for 200 response)
- `database`: Database connectivity status (always "connected" for 200 response)
- `timestamp`: UTC timestamp of health check in ISO 8601 format

---

### Unhealthy Response (503 Service Unavailable)

**Status Code**: `503 Service Unavailable`

**Response Body**:
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "timestamp": "2026-02-05T12:34:56.789Z",
  "error": "Database connection failed"
}
```

**Schema**:
```typescript
{
  status: "unhealthy",
  database: "disconnected",
  timestamp: string,  // ISO 8601 format
  error: string       // Human-readable error message
}
```

**Field Descriptions**:
- `status`: Overall service health status (always "unhealthy" for 503 response)
- `database`: Database connectivity status (always "disconnected" for 503 response)
- `timestamp`: UTC timestamp of health check in ISO 8601 format
- `error`: Human-readable error message (does not expose sensitive details)

---

## Response Codes

| Status Code | Meaning | When Returned |
|-------------|---------|---------------|
| 200 OK | Service is healthy | Database is connected and responsive |
| 503 Service Unavailable | Service is unhealthy | Database is disconnected or unresponsive |

---

## Behavior Specifications

### Database Connectivity Check
- Executes simple query: `SELECT 1`
- Timeout: 2 seconds maximum
- If query succeeds: Return 200 OK with "connected" status
- If query fails or times out: Return 503 with "disconnected" status

### Response Time
- Target: <2 seconds (including database query)
- If response time exceeds 2 seconds, consider service degraded

### Error Handling
- Database connection errors are caught and returned as 503
- Error messages are sanitized (no connection strings, credentials, or internal paths)
- Unexpected errors return 503 with generic error message

### Security Considerations
- No authentication required (public endpoint for operational use)
- Does not expose sensitive system information
- Error messages do not leak internal implementation details
- Does not log sensitive data

---

## Usage Examples

### Monitoring Script
```bash
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ $response -eq 200 ]; then
  echo "Service is healthy"
  exit 0
else
  echo "Service is unhealthy"
  exit 1
fi
```

### Load Balancer Configuration (Example)
```yaml
health_check:
  path: /health
  interval: 30s
  timeout: 2s
  healthy_threshold: 2
  unhealthy_threshold: 3
```

### Monitoring Tool Integration
```python
import requests

def check_service_health():
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return data["status"] == "healthy" and data["database"] == "connected"
        return False
    except requests.RequestException:
        return False
```

---

## OpenAPI Specification

```yaml
/health:
  get:
    summary: Health check endpoint
    description: Returns the health status of the backend service and database connectivity
    operationId: healthCheck
    tags:
      - Health
    responses:
      '200':
        description: Service is healthy
        content:
          application/json:
            schema:
              type: object
              required:
                - status
                - database
                - timestamp
              properties:
                status:
                  type: string
                  enum: [healthy]
                  example: healthy
                database:
                  type: string
                  enum: [connected]
                  example: connected
                timestamp:
                  type: string
                  format: date-time
                  example: "2026-02-05T12:34:56.789Z"
      '503':
        description: Service is unhealthy
        content:
          application/json:
            schema:
              type: object
              required:
                - status
                - database
                - timestamp
              properties:
                status:
                  type: string
                  enum: [unhealthy]
                  example: unhealthy
                database:
                  type: string
                  enum: [disconnected]
                  example: disconnected
                timestamp:
                  type: string
                  format: date-time
                  example: "2026-02-05T12:34:56.789Z"
                error:
                  type: string
                  example: "Database connection failed"
```

---

## Testing Scenarios

### Test 1: Healthy Service
**Given**: Backend is running with database connected
**When**: GET /health is called
**Then**:
- Response status is 200 OK
- Response body contains `"status": "healthy"`
- Response body contains `"database": "connected"`
- Response includes valid ISO 8601 timestamp

### Test 2: Database Disconnected
**Given**: Backend is running but database is unreachable
**When**: GET /health is called
**Then**:
- Response status is 503 Service Unavailable
- Response body contains `"status": "unhealthy"`
- Response body contains `"database": "disconnected"`
- Response includes error message
- Response includes valid ISO 8601 timestamp

### Test 3: Response Time
**Given**: Backend is running with database connected
**When**: GET /health is called
**Then**:
- Response is received within 2 seconds

### Test 4: No Authentication Required
**Given**: Backend is running
**When**: GET /health is called without Authorization header
**Then**:
- Request succeeds (no 401 error)
- Response is returned normally

---

## Implementation Notes

### Backend Implementation Location
- File: `backend/src/main.py`
- Function: `health_check()`
- Dependencies: Database session, datetime

### Database Query
```python
async with get_session() as session:
    await session.execute(text("SELECT 1"))
```

### Error Handling
```python
try:
    # Database check
    return {"status": "healthy", ...}
except Exception as e:
    logger.error(f"Health check failed: {str(e)}")
    return JSONResponse(
        status_code=503,
        content={"status": "unhealthy", ...}
    )
```

---

## Changelog

### Version 1.0.0 (2026-02-05)
- Initial health check endpoint specification
- Database connectivity check
- 200 OK for healthy, 503 for unhealthy
- Public endpoint (no authentication)
