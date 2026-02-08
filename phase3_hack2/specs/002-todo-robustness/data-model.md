# Data Model: Production Readiness Enhancements

**Feature**: 002-todo-robustness
**Date**: 2026-02-05

## Overview

This document defines the data structures for error handling and validation enhancements. No changes to existing Task or User entities are required. All additions are for error response standardization.

---

## New Entities

### ErrorResponse

**Purpose**: Standardized error response structure returned by all API endpoints when errors occur.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| error_code | string | Yes | Machine-readable error identifier (e.g., "TASK_NOT_FOUND", "VALIDATION_ERROR") |
| message | string | Yes | Human-readable error message for display to users |
| details | ErrorDetail[] | No | Optional array of field-level error details (used for validation errors) |

**Constraints**:
- error_code: UPPER_SNAKE_CASE format, alphanumeric with underscores
- message: Plain language, 1-500 characters
- details: Only present for validation errors (HTTP 422)

**Example**:
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

---

### ErrorDetail

**Purpose**: Field-level validation error information, used within ErrorResponse.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| field | string | Yes | Name of the field that failed validation (e.g., "title", "description") |
| message | string | Yes | Specific validation error message for this field |

**Constraints**:
- field: Matches request body field names, dot notation for nested fields
- message: Plain language, specific to the validation failure

**Example**:
```json
{
  "field": "title",
  "message": "Title must be between 1 and 200 characters"
}
```

---

## Enhanced Existing Entities

### Task (No Schema Changes)

**Validation Rules** (enforced at application layer, not database):

| Field | Validation Rule | Error Message |
|-------|----------------|---------------|
| title | Required, 1-200 characters, not empty/whitespace | "Title cannot be empty or whitespace only" |
| description | Optional, max 2000 characters | "Description must be 2000 characters or less" |
| user_id | Immutable after creation | "Task ownership cannot be changed" |
| completed | Boolean only | "Completed must be true or false" |

**Business Rules**:
- Task ownership (user_id) cannot be modified after creation
- Only the task owner can read, update, delete, or toggle completion
- Attempting to access another user's task returns 403 Forbidden
- Attempting to access non-existent task returns 404 Not Found

---

## Error Code Taxonomy

### Authentication Errors (HTTP 401)

| Error Code | Message | Trigger Condition |
|------------|---------|-------------------|
| MISSING_TOKEN | Authentication required. Please sign in. | No Authorization header provided |
| TOKEN_EXPIRED | Your session has expired. Please sign in again. | JWT exp claim is in the past |
| INVALID_TOKEN | Invalid authentication token. Please sign in again. | Malformed JWT, invalid signature, or missing claims |

### Authorization Errors (HTTP 403)

| Error Code | Message | Trigger Condition |
|------------|---------|-------------------|
| FORBIDDEN | You don't have permission to access this task | JWT user_id doesn't match task.user_id |
| OWNERSHIP_CHANGE_FORBIDDEN | Task ownership cannot be changed | Attempt to modify user_id in update request |

### Resource Errors (HTTP 404)

| Error Code | Message | Trigger Condition |
|------------|---------|-------------------|
| TASK_NOT_FOUND | Task with ID {id} not found | Task ID doesn't exist in database |

### Validation Errors (HTTP 422)

| Error Code | Message | Trigger Condition |
|------------|---------|-------------------|
| VALIDATION_ERROR | Invalid input data | One or more fields failed validation (details array populated) |

### Server Errors (HTTP 500)

| Error Code | Message | Trigger Condition |
|------------|---------|-------------------|
| INTERNAL_ERROR | An unexpected error occurred. Please try again. | Unhandled exception, database connection failure, etc. |

---

## State Transitions

### Task Completion Toggle

**Current State** → **Action** → **New State**

- `completed: false` → PATCH /api/tasks/{id}/complete → `completed: true`
- `completed: true` → PATCH /api/tasks/{id}/complete → `completed: false`

**Idempotency**: Multiple identical requests produce the same final state. The toggle is based on the current database state, not the request payload.

**Concurrency Handling**: SELECT FOR UPDATE ensures only one request modifies the task at a time. Concurrent requests are serialized.

---

## Validation Rules Summary

### TaskCreate Schema

```python
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)

    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()
```

### TaskUpdate Schema

```python
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)

    @validator('title')
    def title_not_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip() if v else v
```

**Note**: user_id is never accepted in request bodies. It is always extracted from the verified JWT token.

---

## Relationships

```
ErrorResponse
├── error_code: string
├── message: string
└── details: ErrorDetail[] (optional)
    └── ErrorDetail
        ├── field: string
        └── message: string

Task (existing, no changes)
├── id: int
├── user_id: string (immutable, from JWT only)
├── title: string (validated)
├── description: string | null (validated)
├── completed: boolean
├── created_at: datetime
└── updated_at: datetime
```

---

## Implementation Notes

1. **No Database Migrations**: All validation is application-layer only. Existing database schema remains unchanged.

2. **Error Response Consistency**: All endpoints must return ErrorResponse structure for errors. No plain text or unstructured JSON errors.

3. **Field Names**: Error detail field names must match request body field names exactly for frontend to map errors to form fields.

4. **Security**: Error messages must not leak sensitive information (database structure, internal paths, stack traces).

5. **Localization**: Error messages are currently English-only. Future enhancement could add i18n support.

---

## Testing Considerations

### Validation Testing

- Test empty title → expect 422 with field-level error
- Test title with only whitespace → expect 422
- Test title exceeding 200 characters → expect 422
- Test description exceeding 2000 characters → expect 422

### Authorization Testing

- Test accessing another user's task → expect 403 with FORBIDDEN error
- Test modifying user_id in update request → expect 403 with OWNERSHIP_CHANGE_FORBIDDEN

### Authentication Testing

- Test missing Authorization header → expect 401 with MISSING_TOKEN
- Test expired JWT → expect 401 with TOKEN_EXPIRED
- Test malformed JWT → expect 401 with INVALID_TOKEN

### Concurrency Testing

- Send multiple simultaneous completion toggle requests → verify final state is consistent
- Verify no data corruption occurs under concurrent load
