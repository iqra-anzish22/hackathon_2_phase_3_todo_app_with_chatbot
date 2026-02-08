# Error Response Contracts

**Feature**: 002-todo-robustness
**Date**: 2026-02-05

## Overview

This document defines the standard error response format for all API endpoints. All error responses follow the ErrorResponse schema defined in data-model.md.

---

## Standard Error Response Format

### Structure

```json
{
  "error_code": "string",
  "message": "string",
  "details": [
    {
      "field": "string",
      "message": "string"
    }
  ]
}
```

**Fields**:
- `error_code`: Machine-readable identifier (UPPER_SNAKE_CASE)
- `message`: Human-readable error message
- `details`: Optional array of field-level errors (only for validation errors)

---

## HTTP 401 Unauthorized

**When**: Authentication is missing, invalid, or expired

### Missing Token

```json
{
  "error_code": "MISSING_TOKEN",
  "message": "Authentication required. Please sign in."
}
```

**Trigger**: No Authorization header in request

**Frontend Action**: Redirect to /signin

---

### Expired Token

```json
{
  "error_code": "TOKEN_EXPIRED",
  "message": "Your session has expired. Please sign in again."
}
```

**Trigger**: JWT exp claim is in the past

**Frontend Action**: Redirect to /signin with message "Your session has expired"

---

### Invalid Token

```json
{
  "error_code": "INVALID_TOKEN",
  "message": "Invalid authentication token. Please sign in again."
}
```

**Trigger**: Malformed JWT, invalid signature, or missing required claims

**Frontend Action**: Redirect to /signin with message "Please sign in again"

---

## HTTP 403 Forbidden

**When**: User is authenticated but lacks permission for the requested resource

### Forbidden Access

```json
{
  "error_code": "FORBIDDEN",
  "message": "You don't have permission to access this task"
}
```

**Trigger**: JWT user_id doesn't match task.user_id

**Frontend Action**: Display error message, optionally redirect to task list

---

### Ownership Change Forbidden

```json
{
  "error_code": "OWNERSHIP_CHANGE_FORBIDDEN",
  "message": "Task ownership cannot be changed"
}
```

**Trigger**: Attempt to modify user_id in task update request

**Frontend Action**: Display error message (should not occur in normal UI flow)

---

## HTTP 404 Not Found

**When**: Requested resource doesn't exist

### Task Not Found

```json
{
  "error_code": "TASK_NOT_FOUND",
  "message": "Task with ID 123 not found"
}
```

**Trigger**: Task ID doesn't exist in database (or exists but belongs to another user)

**Frontend Action**: Display "Task not found" message, redirect to task list

**Security Note**: Returns 404 even if task exists but belongs to another user (prevents information leakage)

---

## HTTP 422 Unprocessable Entity

**When**: Request body fails validation

### Validation Error (Single Field)

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid input data",
  "details": [
    {
      "field": "title",
      "message": "Title cannot be empty or whitespace only"
    }
  ]
}
```

**Trigger**: Title field is empty or contains only whitespace

**Frontend Action**: Display inline error message next to title field

---

### Validation Error (Multiple Fields)

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid input data",
  "details": [
    {
      "field": "title",
      "message": "Title must be between 1 and 200 characters"
    },
    {
      "field": "description",
      "message": "Description must be 2000 characters or less"
    }
  ]
}
```

**Trigger**: Multiple fields fail validation

**Frontend Action**: Display inline error messages next to each affected field

---

### Common Validation Errors

| Field | Validation Rule | Error Message |
|-------|----------------|---------------|
| title | Required | "Field required" |
| title | Min length 1 | "Title must be at least 1 character" |
| title | Max length 200 | "Title must be 200 characters or less" |
| title | Not whitespace only | "Title cannot be empty or whitespace only" |
| description | Max length 2000 | "Description must be 2000 characters or less" |

---

## HTTP 500 Internal Server Error

**When**: Unexpected server error occurs

### Internal Error

```json
{
  "error_code": "INTERNAL_ERROR",
  "message": "An unexpected error occurred. Please try again."
}
```

**Trigger**: Unhandled exception, database connection failure, etc.

**Frontend Action**: Display generic error message with retry option

**Security Note**: Never expose stack traces, database errors, or internal paths to clients

---

## Error Response Examples by Endpoint

### POST /api/tasks

**Success**: 201 Created
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-02-05T10:00:00Z",
  "updated_at": "2026-02-05T10:00:00Z"
}
```

**Errors**:
- 401: MISSING_TOKEN, TOKEN_EXPIRED, INVALID_TOKEN
- 422: VALIDATION_ERROR (empty title, title too long, description too long)
- 500: INTERNAL_ERROR

---

### GET /api/tasks

**Success**: 200 OK
```json
[
  {
    "id": 1,
    "user_id": "user123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-02-05T10:00:00Z",
    "updated_at": "2026-02-05T10:00:00Z"
  }
]
```

**Errors**:
- 401: MISSING_TOKEN, TOKEN_EXPIRED, INVALID_TOKEN
- 500: INTERNAL_ERROR

---

### GET /api/tasks/{id}

**Success**: 200 OK
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-02-05T10:00:00Z",
  "updated_at": "2026-02-05T10:00:00Z"
}
```

**Errors**:
- 401: MISSING_TOKEN, TOKEN_EXPIRED, INVALID_TOKEN
- 403: FORBIDDEN (task belongs to another user)
- 404: TASK_NOT_FOUND
- 500: INTERNAL_ERROR

---

### PUT /api/tasks/{id}

**Success**: 200 OK
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries and cook dinner",
  "description": "Updated description",
  "completed": false,
  "created_at": "2026-02-05T10:00:00Z",
  "updated_at": "2026-02-05T11:00:00Z"
}
```

**Errors**:
- 401: MISSING_TOKEN, TOKEN_EXPIRED, INVALID_TOKEN
- 403: FORBIDDEN (task belongs to another user), OWNERSHIP_CHANGE_FORBIDDEN (attempt to change user_id)
- 404: TASK_NOT_FOUND
- 422: VALIDATION_ERROR (empty title, title too long, description too long)
- 500: INTERNAL_ERROR

---

### DELETE /api/tasks/{id}

**Success**: 204 No Content
(Empty response body)

**Errors**:
- 401: MISSING_TOKEN, TOKEN_EXPIRED, INVALID_TOKEN
- 403: FORBIDDEN (task belongs to another user)
- 404: TASK_NOT_FOUND
- 500: INTERNAL_ERROR

---

### PATCH /api/tasks/{id}/complete

**Success**: 200 OK
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": true,
  "created_at": "2026-02-05T10:00:00Z",
  "updated_at": "2026-02-05T12:00:00Z"
}
```

**Errors**:
- 401: MISSING_TOKEN, TOKEN_EXPIRED, INVALID_TOKEN
- 403: FORBIDDEN (task belongs to another user)
- 404: TASK_NOT_FOUND
- 500: INTERNAL_ERROR

**Idempotency**: Multiple identical requests toggle the completion state. The operation is based on the current database state, not the request payload.

---

## Frontend Error Handling Guidelines

### Error Display Strategy

| HTTP Status | Display Method | User Action |
|-------------|----------------|-------------|
| 401 | Redirect to /signin | User must sign in again |
| 403 | Inline error message | Display "Permission denied" message |
| 404 | Inline error message | Display "Not found" message, redirect to list |
| 422 | Field-level inline errors | User corrects invalid fields |
| 500 | Modal or toast notification | User can retry operation |

### Error Message Mapping

```typescript
function getErrorMessage(error: ApiError): string {
  const messages: Record<string, string> = {
    MISSING_TOKEN: 'Please sign in to continue',
    TOKEN_EXPIRED: 'Your session has expired. Please sign in again.',
    INVALID_TOKEN: 'Authentication failed. Please sign in again.',
    FORBIDDEN: "You don't have permission to access this task",
    OWNERSHIP_CHANGE_FORBIDDEN: 'Task ownership cannot be changed',
    TASK_NOT_FOUND: 'Task not found',
    VALIDATION_ERROR: 'Please correct the errors below',
    INTERNAL_ERROR: 'An unexpected error occurred. Please try again.',
  };

  return messages[error.error_code] || error.message;
}
```

### Retry Logic

- **401 errors**: Do not retry, redirect to signin
- **403 errors**: Do not retry, display error
- **404 errors**: Do not retry, display error
- **422 errors**: Do not retry, user must fix input
- **500 errors**: Allow retry with exponential backoff (optional)
- **Network errors**: Allow retry with user confirmation

---

## Testing Error Responses

### Manual Testing Checklist

- [ ] Test missing Authorization header → 401 MISSING_TOKEN
- [ ] Test expired JWT → 401 TOKEN_EXPIRED
- [ ] Test malformed JWT → 401 INVALID_TOKEN
- [ ] Test accessing another user's task → 403 FORBIDDEN
- [ ] Test non-existent task ID → 404 TASK_NOT_FOUND
- [ ] Test empty title → 422 VALIDATION_ERROR with field details
- [ ] Test title with whitespace only → 422 VALIDATION_ERROR
- [ ] Test title exceeding 200 chars → 422 VALIDATION_ERROR
- [ ] Test description exceeding 2000 chars → 422 VALIDATION_ERROR
- [ ] Verify all error responses follow ErrorResponse schema
- [ ] Verify error messages are user-friendly (no technical jargon)
- [ ] Verify no sensitive information in error messages

### Automated Testing (Future)

```python
# Example test case
def test_task_not_found_returns_404():
    response = client.get("/api/tasks/99999", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "TASK_NOT_FOUND"
    assert "message" in data
    assert "details" not in data  # 404 errors don't have details
```
