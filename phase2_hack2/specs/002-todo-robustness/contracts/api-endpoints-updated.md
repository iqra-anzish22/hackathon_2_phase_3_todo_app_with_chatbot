# API Endpoints: Updated with Error Handling

**Feature**: 002-todo-robustness
**Date**: 2026-02-05

## Overview

This document updates the existing API endpoint contracts from 001-multiuser-todo with comprehensive error response specifications. All endpoints now include detailed error scenarios and response formats.

---

## Authentication

All endpoints require JWT authentication via the Authorization header:

```
Authorization: Bearer <jwt_token>
```

**Missing or invalid authentication returns HTTP 401** with appropriate error code (MISSING_TOKEN, TOKEN_EXPIRED, or INVALID_TOKEN).

---

## Endpoint: List Tasks

### GET /api/tasks

**Description**: Retrieve all tasks belonging to the authenticated user.

**Authentication**: Required

**Request**:
- Headers: `Authorization: Bearer <token>`
- Body: None

**Success Response** (200 OK):
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
  },
  {
    "id": 2,
    "user_id": "user123",
    "title": "Finish project",
    "description": null,
    "completed": true,
    "created_at": "2026-02-04T15:30:00Z",
    "updated_at": "2026-02-05T09:00:00Z"
  }
]
```

**Empty List** (200 OK):
```json
[]
```

**Error Responses**:

| Status | Error Code | Message | Trigger |
|--------|------------|---------|---------|
| 401 | MISSING_TOKEN | Authentication required. Please sign in. | No Authorization header |
| 401 | TOKEN_EXPIRED | Your session has expired. Please sign in again. | JWT expired |
| 401 | INVALID_TOKEN | Invalid authentication token. Please sign in again. | Malformed/invalid JWT |
| 500 | INTERNAL_ERROR | An unexpected error occurred. Please try again. | Server error |

**Notes**:
- Returns only tasks where `user_id` matches the authenticated user
- Empty array if user has no tasks (not an error)
- Tasks are ordered by creation date (newest first)

---

## Endpoint: Create Task

### POST /api/tasks

**Description**: Create a new task for the authenticated user.

**Authentication**: Required

**Request**:
- Headers: `Authorization: Bearer <token>`, `Content-Type: application/json`
- Body:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Request Schema**:
- `title` (string, required): 1-200 characters, cannot be empty or whitespace only
- `description` (string, optional): Max 2000 characters, can be null

**Success Response** (201 Created):
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

**Error Responses**:

| Status | Error Code | Message | Trigger | Details |
|--------|------------|---------|---------|---------|
| 401 | MISSING_TOKEN | Authentication required. Please sign in. | No Authorization header | - |
| 401 | TOKEN_EXPIRED | Your session has expired. Please sign in again. | JWT expired | - |
| 401 | INVALID_TOKEN | Invalid authentication token. Please sign in again. | Malformed/invalid JWT | - |
| 422 | VALIDATION_ERROR | Invalid input data | Title missing | `[{"field": "title", "message": "Field required"}]` |
| 422 | VALIDATION_ERROR | Invalid input data | Title empty/whitespace | `[{"field": "title", "message": "Title cannot be empty or whitespace only"}]` |
| 422 | VALIDATION_ERROR | Invalid input data | Title too long | `[{"field": "title", "message": "Title must be 200 characters or less"}]` |
| 422 | VALIDATION_ERROR | Invalid input data | Description too long | `[{"field": "description", "message": "Description must be 2000 characters or less"}]` |
| 500 | INTERNAL_ERROR | An unexpected error occurred. Please try again. | Server error | - |

**Validation Examples**:

Empty title:
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

Multiple validation errors:
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid input data",
  "details": [
    {
      "field": "title",
      "message": "Title must be 200 characters or less"
    },
    {
      "field": "description",
      "message": "Description must be 2000 characters or less"
    }
  ]
}
```

**Notes**:
- `user_id` is automatically set from JWT, never from request body
- `completed` defaults to `false`
- `created_at` and `updated_at` are automatically set
- Title is trimmed of leading/trailing whitespace

---

## Endpoint: Get Task

### GET /api/tasks/{id}

**Description**: Retrieve a specific task by ID. User must own the task.

**Authentication**: Required

**Request**:
- Headers: `Authorization: Bearer <token>`
- Path Parameters: `id` (integer) - Task ID
- Body: None

**Success Response** (200 OK):
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

**Error Responses**:

| Status | Error Code | Message | Trigger |
|--------|------------|---------|---------|
| 401 | MISSING_TOKEN | Authentication required. Please sign in. | No Authorization header |
| 401 | TOKEN_EXPIRED | Your session has expired. Please sign in again. | JWT expired |
| 401 | INVALID_TOKEN | Invalid authentication token. Please sign in again. | Malformed/invalid JWT |
| 403 | FORBIDDEN | You don't have permission to access this task | Task exists but belongs to another user |
| 404 | TASK_NOT_FOUND | Task with ID {id} not found | Task doesn't exist |
| 500 | INTERNAL_ERROR | An unexpected error occurred. Please try again. | Server error |

**Security Note**: Returns 404 (not 403) when task exists but belongs to another user to prevent information leakage about task existence.

---

## Endpoint: Update Task

### PUT /api/tasks/{id}

**Description**: Update an existing task. User must own the task.

**Authentication**: Required

**Request**:
- Headers: `Authorization: Bearer <token>`, `Content-Type: application/json`
- Path Parameters: `id` (integer) - Task ID
- Body:
```json
{
  "title": "Buy groceries and cook dinner",
  "description": "Updated description"
}
```

**Request Schema**:
- `title` (string, optional): 1-200 characters if provided, cannot be empty or whitespace only
- `description` (string, optional): Max 2000 characters, can be null

**Success Response** (200 OK):
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

**Error Responses**:

| Status | Error Code | Message | Trigger |
|--------|------------|---------|---------|
| 401 | MISSING_TOKEN | Authentication required. Please sign in. | No Authorization header |
| 401 | TOKEN_EXPIRED | Your session has expired. Please sign in again. | JWT expired |
| 401 | INVALID_TOKEN | Invalid authentication token. Please sign in again. | Malformed/invalid JWT |
| 403 | FORBIDDEN | You don't have permission to access this task | Task belongs to another user |
| 403 | OWNERSHIP_CHANGE_FORBIDDEN | Task ownership cannot be changed | Request includes user_id field |
| 404 | TASK_NOT_FOUND | Task with ID {id} not found | Task doesn't exist |
| 422 | VALIDATION_ERROR | Invalid input data | Title empty/whitespace or too long | Field-level details provided |
| 422 | VALIDATION_ERROR | Invalid input data | Description too long | Field-level details provided |
| 500 | INTERNAL_ERROR | An unexpected error occurred. Please try again. | Server error |

**Notes**:
- Only provided fields are updated (partial update)
- `user_id` cannot be changed (returns 403 if attempted)
- `completed` is not updated via this endpoint (use PATCH /complete)
- `updated_at` is automatically updated
- Title is trimmed of leading/trailing whitespace if provided

---

## Endpoint: Delete Task

### DELETE /api/tasks/{id}

**Description**: Permanently delete a task. User must own the task.

**Authentication**: Required

**Request**:
- Headers: `Authorization: Bearer <token>`
- Path Parameters: `id` (integer) - Task ID
- Body: None

**Success Response** (204 No Content):
- Empty response body

**Error Responses**:

| Status | Error Code | Message | Trigger |
|--------|------------|---------|---------|
| 401 | MISSING_TOKEN | Authentication required. Please sign in. | No Authorization header |
| 401 | TOKEN_EXPIRED | Your session has expired. Please sign in again. | JWT expired |
| 401 | INVALID_TOKEN | Invalid authentication token. Please sign in again. | Malformed/invalid JWT |
| 403 | FORBIDDEN | You don't have permission to access this task | Task belongs to another user |
| 404 | TASK_NOT_FOUND | Task with ID {id} not found | Task doesn't exist |
| 500 | INTERNAL_ERROR | An unexpected error occurred. Please try again. | Server error |

**Notes**:
- Deletion is permanent and cannot be undone
- Returns 204 even if task was already deleted (idempotent)
- Task is removed from database immediately

---

## Endpoint: Toggle Task Completion

### PATCH /api/tasks/{id}/complete

**Description**: Toggle the completion status of a task. User must own the task.

**Authentication**: Required

**Request**:
- Headers: `Authorization: Bearer <token>`
- Path Parameters: `id` (integer) - Task ID
- Body: None (completion state is toggled based on current database state)

**Success Response** (200 OK):
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

**Error Responses**:

| Status | Error Code | Message | Trigger |
|--------|------------|---------|---------|
| 401 | MISSING_TOKEN | Authentication required. Please sign in. | No Authorization header |
| 401 | TOKEN_EXPIRED | Your session has expired. Please sign in again. | JWT expired |
| 401 | INVALID_TOKEN | Invalid authentication token. Please sign in again. | Malformed/invalid JWT |
| 403 | FORBIDDEN | You don't have permission to access this task | Task belongs to another user |
| 404 | TASK_NOT_FOUND | Task with ID {id} not found | Task doesn't exist |
| 500 | INTERNAL_ERROR | An unexpected error occurred. Please try again. | Server error |

**Idempotency**:
- Operation toggles completion based on current database state
- `completed: false` → `completed: true`
- `completed: true` → `completed: false`
- Multiple identical requests will alternate the state

**Concurrency Handling**:
- Uses SELECT FOR UPDATE to prevent race conditions
- Concurrent requests are serialized
- Final state is consistent regardless of request order

**Notes**:
- No request body required
- `updated_at` is automatically updated
- Returns the updated task with new completion status

---

## Error Response Format

All error responses follow this structure:

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

- `details` array is only present for validation errors (HTTP 422)
- See [error-responses.md](error-responses.md) for complete error documentation

---

## Common Error Scenarios

### Scenario 1: Expired Session

**Request**: Any authenticated endpoint
**Condition**: JWT token has expired
**Response**: 401 TOKEN_EXPIRED
**Frontend Action**: Redirect to /signin with message "Your session has expired"

### Scenario 2: Accessing Another User's Task

**Request**: GET /api/tasks/123
**Condition**: Task 123 belongs to user456, but request is from user123
**Response**: 404 TASK_NOT_FOUND (not 403, to prevent information leakage)
**Frontend Action**: Display "Task not found" message

### Scenario 3: Invalid Input

**Request**: POST /api/tasks with empty title
**Condition**: Title validation fails
**Response**: 422 VALIDATION_ERROR with field details
**Frontend Action**: Display inline error next to title field

### Scenario 4: Concurrent Completion Toggle

**Request**: Multiple PATCH /api/tasks/123/complete requests simultaneously
**Condition**: Race condition
**Response**: All requests succeed with 200, final state is consistent
**Frontend Action**: Display updated task state

---

## Testing Checklist

- [ ] Test all endpoints with missing Authorization header → 401 MISSING_TOKEN
- [ ] Test all endpoints with expired JWT → 401 TOKEN_EXPIRED
- [ ] Test all endpoints with malformed JWT → 401 INVALID_TOKEN
- [ ] Test GET/PUT/DELETE/PATCH with another user's task → 403/404
- [ ] Test GET/PUT/DELETE/PATCH with non-existent task → 404
- [ ] Test POST with empty title → 422 with field details
- [ ] Test POST with title > 200 chars → 422 with field details
- [ ] Test POST with description > 2000 chars → 422 with field details
- [ ] Test PUT with attempt to change user_id → 403 OWNERSHIP_CHANGE_FORBIDDEN
- [ ] Test PATCH completion toggle multiple times → verify state alternates
- [ ] Test concurrent PATCH requests → verify no data corruption
- [ ] Verify all error responses match ErrorResponse schema
