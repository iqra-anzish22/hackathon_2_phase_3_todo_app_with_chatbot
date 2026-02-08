# Quickstart: Testing Production Readiness Enhancements

**Feature**: 002-todo-robustness
**Date**: 2026-02-05

## Overview

This guide provides step-by-step instructions for manually testing the production readiness enhancements to the multi-user todo application. Focus areas: error handling, validation, authentication edge cases, and security enforcement.

---

## Prerequisites

### Environment Setup

1. **Backend Running**: FastAPI server running on http://localhost:8000
2. **Frontend Running**: Next.js app running on http://localhost:3000
3. **Database**: Neon PostgreSQL connected and accessible
4. **Test Users**: Two user accounts created for multi-user testing
   - User A: test1@example.com / password123
   - User B: test2@example.com / password456

### Testing Tools

- **Browser**: Chrome/Firefox with DevTools open (Network tab)
- **API Client**: curl, Postman, or Thunder Client for direct API testing
- **JWT Inspector**: https://jwt.io for token inspection
- **Text Editor**: For crafting test payloads

---

## Test Suite 1: Authentication Error Handling

### Test 1.1: Missing Authorization Header

**Objective**: Verify 401 MISSING_TOKEN error when no auth header provided

**Steps**:
1. Open terminal
2. Send request without Authorization header:
```bash
curl -X GET http://localhost:8000/api/tasks
```

**Expected Result**:
- Status: 401 Unauthorized
- Response body:
```json
{
  "error_code": "MISSING_TOKEN",
  "message": "Authentication required. Please sign in."
}
```

**Frontend Test**:
1. Clear browser cookies/localStorage
2. Navigate directly to http://localhost:3000/tasks
3. Should redirect to /signin with message

---

### Test 1.2: Expired JWT Token

**Objective**: Verify 401 TOKEN_EXPIRED error when JWT has expired

**Steps**:
1. Sign in as User A and copy JWT token from browser DevTools (Application > Cookies or localStorage)
2. Decode token at https://jwt.io and note the `exp` claim
3. Wait until token expires OR manually create expired token:
```bash
# Create token with exp in the past (requires jwt.io or python script)
# For testing, modify Better Auth config to issue short-lived tokens (exp: 1 minute)
```
4. Send request with expired token:
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <expired_token>"
```

**Expected Result**:
- Status: 401 Unauthorized
- Response body:
```json
{
  "error_code": "TOKEN_EXPIRED",
  "message": "Your session has expired. Please sign in again."
}
```

**Frontend Test**:
1. Wait for token to expire while on /tasks page
2. Attempt to create a task
3. Should redirect to /signin with "Your session has expired" message

---

### Test 1.3: Malformed JWT Token

**Objective**: Verify 401 INVALID_TOKEN error when JWT is malformed

**Steps**:
1. Send request with invalid JWT:
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer invalid.jwt.token"
```

**Expected Result**:
- Status: 401 Unauthorized
- Response body:
```json
{
  "error_code": "INVALID_TOKEN",
  "message": "Invalid authentication token. Please sign in again."
}
```

**Additional Tests**:
- Token with invalid signature (modify last segment)
- Token missing required claims (modify payload)
- Token with wrong algorithm

---

## Test Suite 2: Authorization & Ownership

### Test 2.1: Access Another User's Task

**Objective**: Verify 403/404 error when accessing task owned by different user

**Steps**:
1. Sign in as User A
2. Create a task and note its ID (e.g., task ID 1)
3. Sign out and sign in as User B
4. Copy User B's JWT token
5. Attempt to access User A's task:
```bash
curl -X GET http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer <user_b_token>"
```

**Expected Result**:
- Status: 404 Not Found (not 403, to prevent information leakage)
- Response body:
```json
{
  "error_code": "TASK_NOT_FOUND",
  "message": "Task with ID 1 not found"
}
```

**Frontend Test**:
1. As User B, navigate directly to http://localhost:3000/tasks/1
2. Should display "Task not found" error message

---

### Test 2.2: Attempt to Change Task Ownership

**Objective**: Verify 403 OWNERSHIP_CHANGE_FORBIDDEN when attempting to modify user_id

**Steps**:
1. Sign in as User A
2. Create a task (ID 1)
3. Attempt to update task with different user_id:
```bash
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer <user_a_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated title",
    "user_id": "different_user_id"
  }'
```

**Expected Result**:
- Status: 403 Forbidden
- Response body:
```json
{
  "error_code": "OWNERSHIP_CHANGE_FORBIDDEN",
  "message": "Task ownership cannot be changed"
}
```

**Note**: This should not occur in normal UI flow, but backend must prevent it.

---

## Test Suite 3: Validation Errors

### Test 3.1: Empty Title

**Objective**: Verify 422 VALIDATION_ERROR when title is empty

**Steps**:
1. Sign in as User A
2. Attempt to create task with empty title:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "",
    "description": "Test description"
  }'
```

**Expected Result**:
- Status: 422 Unprocessable Entity
- Response body:
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

**Frontend Test**:
1. Navigate to /tasks
2. Click "Create Task"
3. Leave title empty and submit
4. Should display inline error: "Title is required"

---

### Test 3.2: Whitespace-Only Title

**Objective**: Verify validation rejects whitespace-only titles

**Steps**:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "   ",
    "description": "Test"
  }'
```

**Expected Result**:
- Status: 422 Unprocessable Entity
- Field error: "Title cannot be empty or whitespace only"

---

### Test 3.3: Title Too Long

**Objective**: Verify validation enforces 200 character limit

**Steps**:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "'"$(python3 -c "print('a' * 201)")"'",
    "description": "Test"
  }'
```

**Expected Result**:
- Status: 422 Unprocessable Entity
- Field error: "Title must be 200 characters or less"

---

### Test 3.4: Description Too Long

**Objective**: Verify validation enforces 2000 character limit

**Steps**:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Valid title",
    "description": "'"$(python3 -c "print('a' * 2001)")"'"
  }'
```

**Expected Result**:
- Status: 422 Unprocessable Entity
- Field error: "Description must be 2000 characters or less"

---

### Test 3.5: Multiple Validation Errors

**Objective**: Verify multiple field errors are returned together

**Steps**:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "'"$(python3 -c "print('a' * 201)")"'",
    "description": "'"$(python3 -c "print('b' * 2001)")"'"
  }'
```

**Expected Result**:
- Status: 422 Unprocessable Entity
- Response includes errors for both title and description fields

---

## Test Suite 4: Resource Not Found

### Test 4.1: Non-Existent Task ID

**Objective**: Verify 404 TASK_NOT_FOUND for non-existent tasks

**Steps**:
```bash
curl -X GET http://localhost:8000/api/tasks/99999 \
  -H "Authorization: Bearer <token>"
```

**Expected Result**:
- Status: 404 Not Found
- Response body:
```json
{
  "error_code": "TASK_NOT_FOUND",
  "message": "Task with ID 99999 not found"
}
```

**Test All Operations**:
- GET /api/tasks/99999 → 404
- PUT /api/tasks/99999 → 404
- DELETE /api/tasks/99999 → 404
- PATCH /api/tasks/99999/complete → 404

---

## Test Suite 5: Race Conditions & Concurrency

### Test 5.1: Concurrent Completion Toggle

**Objective**: Verify idempotent behavior under concurrent requests

**Steps**:
1. Create a task (ID 1, completed: false)
2. Send multiple simultaneous completion toggle requests:
```bash
# Terminal 1
curl -X PATCH http://localhost:8000/api/tasks/1/complete \
  -H "Authorization: Bearer <token>"

# Terminal 2 (run simultaneously)
curl -X PATCH http://localhost:8000/api/tasks/1/complete \
  -H "Authorization: Bearer <token>"

# Terminal 3 (run simultaneously)
curl -X PATCH http://localhost:8000/api/tasks/1/complete \
  -H "Authorization: Bearer <token>"
```

**Expected Result**:
- All requests return 200 OK
- Final task state is consistent (either completed: true or false)
- No data corruption
- `updated_at` reflects the last successful update

**Frontend Test**:
1. Open same task in two browser tabs
2. Toggle completion in both tabs rapidly
3. Verify final state is consistent across tabs

---

### Test 5.2: Concurrent Updates

**Objective**: Verify last-write-wins for concurrent updates

**Steps**:
1. Create a task
2. Send simultaneous update requests with different titles
3. Verify final state matches one of the updates (no data corruption)

---

## Test Suite 6: Frontend Error Display

### Test 6.1: Loading States

**Objective**: Verify loading indicators appear during API calls

**Steps**:
1. Navigate to /tasks
2. Observe loading spinner while tasks are fetching
3. Create a new task and observe button disabled state during creation
4. Toggle task completion and observe loading state

**Expected Behavior**:
- Loading spinner visible during initial fetch
- Buttons disabled during mutations
- Loading states clear after operation completes

---

### Test 6.2: Empty State

**Objective**: Verify empty state message when no tasks exist

**Steps**:
1. Sign in as new user with no tasks
2. Navigate to /tasks

**Expected Result**:
- Display message: "No tasks yet. Create your first task!"
- Show "Create Task" button prominently

---

### Test 6.3: Error Message Display

**Objective**: Verify error messages are user-friendly and actionable

**Steps**:
1. Trigger various errors (401, 403, 404, 422)
2. Verify error messages are displayed clearly
3. Verify technical error codes are not shown to users
4. Verify retry options are available where appropriate

**Error Display Checklist**:
- [ ] 401 errors redirect to /signin with clear message
- [ ] 403 errors show "Permission denied" message
- [ ] 404 errors show "Not found" message
- [ ] 422 errors show field-level inline errors
- [ ] Network errors show retry option

---

## Test Suite 7: Multi-User Isolation

### Test 7.1: Task List Isolation

**Objective**: Verify users only see their own tasks

**Steps**:
1. Sign in as User A, create 3 tasks
2. Sign in as User B, create 2 tasks
3. Verify User A sees only their 3 tasks
4. Verify User B sees only their 2 tasks
5. Verify task counts are correct for each user

---

### Test 7.2: Cross-User Access Prevention

**Objective**: Verify complete isolation between users

**Steps**:
1. As User A, create task (ID 1)
2. As User B, attempt to:
   - View task 1 → 404
   - Update task 1 → 404
   - Delete task 1 → 404
   - Toggle completion of task 1 → 404
3. Verify User A's task remains unchanged

---

## Test Suite 8: Security Testing

### Test 8.1: JWT Tampering

**Objective**: Verify tampered tokens are rejected

**Steps**:
1. Get valid JWT token
2. Decode at https://jwt.io
3. Modify payload (change user_id)
4. Re-encode without proper signature
5. Send request with tampered token

**Expected Result**:
- Status: 401 INVALID_TOKEN
- Request rejected before any business logic executes

---

### Test 8.2: SQL Injection Attempts

**Objective**: Verify input sanitization prevents SQL injection

**Steps**:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test'; DROP TABLE tasks; --",
    "description": "Injection test"
  }'
```

**Expected Result**:
- Task created with literal string (no SQL execution)
- Database remains intact

---

### Test 8.3: XSS Prevention

**Objective**: Verify HTML/JavaScript in input is handled safely

**Steps**:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "<script>alert(\"XSS\")</script>",
    "description": "<img src=x onerror=alert(1)>"
  }'
```

**Expected Result**:
- Task created with literal strings
- Frontend displays escaped HTML (no script execution)

---

## Test Checklist Summary

### Backend Error Handling
- [ ] Missing token → 401 MISSING_TOKEN
- [ ] Expired token → 401 TOKEN_EXPIRED
- [ ] Invalid token → 401 INVALID_TOKEN
- [ ] Cross-user access → 404 TASK_NOT_FOUND
- [ ] Ownership change attempt → 403 OWNERSHIP_CHANGE_FORBIDDEN
- [ ] Non-existent task → 404 TASK_NOT_FOUND
- [ ] Empty title → 422 with field details
- [ ] Title too long → 422 with field details
- [ ] Description too long → 422 with field details
- [ ] Multiple validation errors → 422 with all field details

### Frontend Error Handling
- [ ] 401 errors redirect to /signin
- [ ] 403 errors display permission message
- [ ] 404 errors display not found message
- [ ] 422 errors display inline field errors
- [ ] Loading states visible during operations
- [ ] Empty state displayed when no tasks
- [ ] Error messages are user-friendly

### Security & Isolation
- [ ] Users only see their own tasks
- [ ] Cross-user access prevented on all operations
- [ ] JWT tampering rejected
- [ ] SQL injection prevented
- [ ] XSS prevented
- [ ] Ownership immutable after creation

### Concurrency & Data Integrity
- [ ] Concurrent completion toggles handled correctly
- [ ] No data corruption under concurrent load
- [ ] Idempotent operations work as expected

---

## Troubleshooting

### Issue: 500 Internal Server Error

**Possible Causes**:
- Database connection failure
- Unhandled exception in backend code
- Missing environment variables

**Debug Steps**:
1. Check backend logs for stack traces
2. Verify DATABASE_URL is set correctly
3. Verify BETTER_AUTH_SECRET matches between frontend and backend
4. Check database connectivity

### Issue: CORS Errors

**Possible Causes**:
- Frontend and backend on different origins
- CORS not configured in FastAPI

**Debug Steps**:
1. Verify CORS middleware in backend/src/main.py
2. Check allowed origins include frontend URL
3. Verify preflight OPTIONS requests succeed

### Issue: Token Not Included in Requests

**Possible Causes**:
- Better Auth not configured correctly
- Token not stored in cookies/localStorage
- API client not including Authorization header

**Debug Steps**:
1. Check browser DevTools > Application > Cookies
2. Verify token exists after sign-in
3. Check Network tab for Authorization header in requests
4. Verify api.ts includes token in headers

---

## Next Steps

After completing manual testing:
1. Document any bugs found
2. Verify all test cases pass
3. Proceed to implementation refinements if needed
4. Consider automated test suite for regression testing (future enhancement)
