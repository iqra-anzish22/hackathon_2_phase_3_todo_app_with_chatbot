# API Endpoints Contract

**Feature**: 001-multiuser-todo
**Date**: 2026-02-04
**Purpose**: Define REST API endpoints, request/response formats, and behavior

## Overview

This document specifies the REST API contract for the multi-user Todo application backend. All endpoints require JWT authentication via the `Authorization: Bearer <token>` header. The backend validates JWT tokens and enforces task ownership on all operations.

**Base URL**: `http://localhost:8000` (development)

**Authentication**: All endpoints require valid JWT token in Authorization header

**Content Type**: `application/json`

---

## Authentication

Authentication is handled by Better Auth on the frontend. The backend validates JWT tokens but does not provide authentication endpoints.

**JWT Token Format**:
```
Authorization: Bearer <jwt-token>
```

**JWT Validation**:
- Signature verified using `BETTER_AUTH_SECRET`
- Expiration checked (exp claim)
- User ID extracted from sub claim
- Invalid/expired tokens return 401 Unauthorized

---

## Endpoints

### 1. List Tasks

**Endpoint**: `GET /api/tasks`

**Description**: Retrieve all tasks belonging to the authenticated user, ordered by creation date (newest first).

**Authentication**: Required

**Request Headers**:
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request Body**: None

**Response**: `200 OK`

```json
[
  {
    "id": 1,
    "user_id": "user-uuid-123",
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for the API",
    "completed": false,
    "created_at": "2026-02-04T10:00:00Z",
    "updated_at": "2026-02-04T10:00:00Z"
  },
  {
    "id": 2,
    "user_id": "user-uuid-123",
    "title": "Review pull requests",
    "description": null,
    "completed": true,
    "created_at": "2026-02-03T15:30:00Z",
    "updated_at": "2026-02-04T09:00:00Z"
  }
]
```

**Error Responses**:

- `401 Unauthorized`: Missing or invalid JWT token
```json
{
  "detail": "Invalid token"
}
```

**Notes**:
- Returns empty array `[]` if user has no tasks
- Tasks are filtered by authenticated user_id from JWT
- Ordered by created_at descending (newest first)

---

### 2. Create Task

**Endpoint**: `POST /api/tasks`

**Description**: Create a new task for the authenticated user.

**Authentication**: Required

**Request Headers**:
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the API"
}
```

**Field Validation**:
- `title` (required): 1-200 characters, trimmed
- `description` (optional): 0-2000 characters, trimmed, nullable

**Response**: `201 Created`

```json
{
  "id": 3,
  "user_id": "user-uuid-123",
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the API",
  "completed": false,
  "created_at": "2026-02-04T11:00:00Z",
  "updated_at": "2026-02-04T11:00:00Z"
}
```

**Error Responses**:

- `401 Unauthorized`: Missing or invalid JWT token
```json
{
  "detail": "Invalid token"
}
```

- `422 Unprocessable Entity`: Validation error
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Notes**:
- `user_id` automatically set from authenticated JWT user
- `completed` defaults to `false`
- `created_at` and `updated_at` automatically set to current timestamp

---

### 3. Get Task

**Endpoint**: `GET /api/tasks/{id}`

**Description**: Retrieve a specific task by ID. Task must belong to the authenticated user.

**Authentication**: Required

**Path Parameters**:
- `id` (integer): Task ID

**Request Headers**:
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request Body**: None

**Response**: `200 OK`

```json
{
  "id": 1,
  "user_id": "user-uuid-123",
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the API",
  "completed": false,
  "created_at": "2026-02-04T10:00:00Z",
  "updated_at": "2026-02-04T10:00:00Z"
}
```

**Error Responses**:

- `401 Unauthorized`: Missing or invalid JWT token
```json
{
  "detail": "Invalid token"
}
```

- `403 Forbidden`: Task exists but belongs to different user
```json
{
  "detail": "Not authorized"
}
```

- `404 Not Found`: Task does not exist
```json
{
  "detail": "Task not found"
}
```

**Notes**:
- Ownership verified: task.user_id must match JWT user_id
- Returns 404 for both non-existent tasks and unauthorized access (security best practice)

---

### 4. Update Task

**Endpoint**: `PUT /api/tasks/{id}`

**Description**: Update an existing task. Task must belong to the authenticated user.

**Authentication**: Required

**Path Parameters**:
- `id` (integer): Task ID

**Request Headers**:
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Updated task title",
  "description": "Updated description"
}
```

**Field Validation**:
- `title` (optional): 1-200 characters, trimmed
- `description` (optional): 0-2000 characters, trimmed, nullable
- At least one field must be provided

**Response**: `200 OK`

```json
{
  "id": 1,
  "user_id": "user-uuid-123",
  "title": "Updated task title",
  "description": "Updated description",
  "completed": false,
  "created_at": "2026-02-04T10:00:00Z",
  "updated_at": "2026-02-04T11:30:00Z"
}
```

**Error Responses**:

- `401 Unauthorized`: Missing or invalid JWT token
```json
{
  "detail": "Invalid token"
}
```

- `403 Forbidden`: Task exists but belongs to different user
```json
{
  "detail": "Not authorized"
}
```

- `404 Not Found`: Task does not exist
```json
{
  "detail": "Task not found"
}
```

- `422 Unprocessable Entity`: Validation error
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Title cannot be empty or whitespace",
      "type": "value_error"
    }
  ]
}
```

**Notes**:
- Only provided fields are updated (partial update)
- `updated_at` automatically set to current timestamp
- `user_id`, `id`, `created_at`, and `completed` cannot be changed via this endpoint
- Ownership verified before update

---

### 5. Delete Task

**Endpoint**: `DELETE /api/tasks/{id}`

**Description**: Permanently delete a task. Task must belong to the authenticated user.

**Authentication**: Required

**Path Parameters**:
- `id` (integer): Task ID

**Request Headers**:
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request Body**: None

**Response**: `204 No Content`

(Empty response body)

**Error Responses**:

- `401 Unauthorized`: Missing or invalid JWT token
```json
{
  "detail": "Invalid token"
}
```

- `403 Forbidden`: Task exists but belongs to different user
```json
{
  "detail": "Not authorized"
}
```

- `404 Not Found`: Task does not exist
```json
{
  "detail": "Task not found"
}
```

**Notes**:
- Permanent deletion (no soft delete)
- Ownership verified before deletion
- Idempotent: deleting non-existent task returns 404

---

### 6. Toggle Task Completion

**Endpoint**: `PATCH /api/tasks/{id}/complete`

**Description**: Toggle the completion status of a task. Task must belong to the authenticated user.

**Authentication**: Required

**Path Parameters**:
- `id` (integer): Task ID

**Request Headers**:
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request Body**: None

**Response**: `200 OK`

```json
{
  "id": 1,
  "user_id": "user-uuid-123",
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the API",
  "completed": true,
  "created_at": "2026-02-04T10:00:00Z",
  "updated_at": "2026-02-04T12:00:00Z"
}
```

**Error Responses**:

- `401 Unauthorized`: Missing or invalid JWT token
```json
{
  "detail": "Invalid token"
}
```

- `403 Forbidden`: Task exists but belongs to different user
```json
{
  "detail": "Not authorized"
}
```

- `404 Not Found`: Task does not exist
```json
{
  "detail": "Task not found"
}
```

**Notes**:
- Toggles boolean: `false` → `true` or `true` → `false`
- `updated_at` automatically set to current timestamp
- Ownership verified before toggle
- Idempotent: calling twice returns to original state

---

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (task created) |
| 204 | No Content | Successful DELETE |
| 401 | Unauthorized | Missing, invalid, or expired JWT |
| 403 | Forbidden | Valid JWT but insufficient permissions |
| 404 | Not Found | Resource doesn't exist or unauthorized |
| 422 | Unprocessable Entity | Validation error in request body |
| 500 | Internal Server Error | Unexpected server error |

---

## Error Response Format

All error responses follow this structure:

```json
{
  "detail": "Error message"
}
```

For validation errors (422):

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error description",
      "type": "error_type"
    }
  ]
}
```

---

## CORS Configuration

**Allowed Origins**: `http://localhost:3000` (Next.js dev server)

**Allowed Methods**: `GET, POST, PUT, PATCH, DELETE, OPTIONS`

**Allowed Headers**: `Authorization, Content-Type`

**Credentials**: Allowed (for cookie-based auth if needed)

---

## Rate Limiting

**Not Implemented**: Rate limiting is not required for this hackathon project.

**Future Consideration**: Implement rate limiting per user_id for production deployment.

---

## API Versioning

**Current Version**: v1 (implicit, no version prefix)

**Future Versioning**: If breaking changes needed, use `/api/v2/` prefix

---

## Example Request Flow

### Complete Task Creation Flow

1. **User authenticates** (Better Auth on frontend)
   - Receives JWT token in HTTP-only cookie

2. **Frontend makes API request**
   ```
   POST /api/tasks
   Authorization: Bearer eyJhbGc...
   Content-Type: application/json

   {
     "title": "New task",
     "description": "Task details"
   }
   ```

3. **Backend validates JWT**
   - Extracts token from Authorization header
   - Verifies signature with BETTER_AUTH_SECRET
   - Checks expiration
   - Extracts user_id from sub claim

4. **Backend creates task**
   - Sets task.user_id = JWT user_id
   - Validates request body
   - Saves to database

5. **Backend returns response**
   ```
   201 Created

   {
     "id": 1,
     "user_id": "user-uuid-123",
     "title": "New task",
     "description": "Task details",
     "completed": false,
     "created_at": "2026-02-04T10:00:00Z",
     "updated_at": "2026-02-04T10:00:00Z"
   }
   ```

---

## Security Considerations

1. **JWT Validation**: Every request validates JWT signature and expiration
2. **Ownership Enforcement**: All operations verify task.user_id matches JWT user_id
3. **No User ID in Request**: user_id never accepted from request body, only from JWT
4. **HTTPS Required**: Production must use HTTPS for token security
5. **Token Expiration**: Tokens expire after 24 hours (configurable)
6. **Error Messages**: Generic messages to prevent information leakage (404 for both not found and unauthorized)

---

## Testing Checklist

- [ ] All endpoints require valid JWT token
- [ ] Invalid/expired tokens return 401
- [ ] Users can only access their own tasks
- [ ] Attempting to access another user's task returns 404
- [ ] Validation errors return 422 with details
- [ ] Created tasks have correct user_id from JWT
- [ ] Timestamps are automatically managed
- [ ] Toggle completion flips boolean correctly
- [ ] Delete is permanent and returns 204
- [ ] Empty task list returns empty array

---

## Summary

**Total Endpoints**: 6
**Authentication**: JWT required on all endpoints
**Ownership Enforcement**: Verified on all task operations
**Error Handling**: Comprehensive with appropriate HTTP codes
**Validation**: Pydantic automatic validation + custom rules
**Security**: User ID from JWT only, never from request
