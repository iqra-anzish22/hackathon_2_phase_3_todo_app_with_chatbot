# Research: Todo Application Production Readiness

**Feature**: 002-todo-robustness
**Date**: 2026-02-05
**Status**: Completed

## Overview

This document captures technical research and decisions for production readiness enhancements to the multi-user todo application. All decisions prioritize simplicity, maintainability, and alignment with existing architecture (FastAPI backend, Next.js frontend, JWT authentication).

---

## Decision 1: Error Response Standardization

**Question**: What is the FastAPI best practice for consistent error response structure across all endpoints?

**Decision**: Use FastAPI's HTTPException with custom exception handlers and Pydantic response models for structured error responses.

**Rationale**:
- FastAPI provides built-in exception handling via `@app.exception_handler()`
- Pydantic models ensure type safety and automatic OpenAPI documentation
- Custom exception classes enable consistent error structure across all endpoints
- Middleware approach would add unnecessary complexity for this use case

**Implementation Approach**:

```python
# schemas/errors.py
class ErrorDetail(BaseModel):
    field: str
    message: str

class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[List[ErrorDetail]] = None

# core/errors.py
class AppException(HTTPException):
    def __init__(self, status_code: int, error_code: str, message: str, details: Optional[List[ErrorDetail]] = None):
        self.error_code = error_code
        self.message = message
        self.details = details
        super().__init__(status_code=status_code, detail=message)

# main.py
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details
        ).dict()
    )
```

**Alternatives Considered**:
- **Middleware-based error handling**: Rejected - adds complexity, harder to customize per endpoint
- **Manual JSONResponse in each endpoint**: Rejected - code duplication, inconsistent structure
- **Third-party error handling library**: Rejected - unnecessary dependency for simple use case

**References**:
- FastAPI Exception Handling: https://fastapi.tiangolo.com/tutorial/handling-errors/
- Pydantic Models for Responses: https://fastapi.tiangolo.com/tutorial/response-model/

---

## Decision 2: Race Condition Prevention

**Question**: How to implement idempotent completion toggle in FastAPI with SQLModel to prevent concurrent request issues?

**Decision**: Use database-level atomic operations with SELECT FOR UPDATE and optimistic locking via version field.

**Rationale**:
- SELECT FOR UPDATE provides row-level locking during transaction
- Prevents concurrent modifications to the same task
- SQLAlchemy (underlying SQLModel) supports this natively
- Simple to implement without external dependencies
- Idempotency achieved by toggling based on current state, not request payload

**Implementation Approach**:

```python
# In tasks.py endpoint
@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Use SELECT FOR UPDATE to lock the row
    statement = select(Task).where(Task.id == task_id).with_for_update()
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise AppException(404, "TASK_NOT_FOUND", "Task not found")

    if task.user_id != current_user:
        raise AppException(403, "FORBIDDEN", "You don't have permission to modify this task")

    # Toggle based on current state (idempotent)
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(task)
    return task
```

**Alternatives Considered**:
- **Optimistic locking with version field**: Considered but rejected - requires schema change, more complex client handling
- **Distributed locks (Redis)**: Rejected - unnecessary infrastructure dependency for this scale
- **Request deduplication via idempotency keys**: Rejected - requires additional storage and complexity
- **Last-write-wins**: Rejected - can cause data loss in concurrent scenarios

**Trade-offs**:
- SELECT FOR UPDATE blocks concurrent requests (acceptable for this use case)
- Slight performance impact under high concurrency (acceptable given scale)
- Simpler than optimistic locking, no schema changes required

**References**:
- SQLAlchemy SELECT FOR UPDATE: https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html#sqlalchemy.orm.Query.with_for_update
- PostgreSQL Row Locking: https://www.postgresql.org/docs/current/explicit-locking.html

---

## Decision 3: Frontend Error Handling

**Question**: What is the Next.js 15 App Router pattern for centralized error handling and user feedback?

**Decision**: Create centralized API client wrapper with error parsing and use React state for error display in components.

**Rationale**:
- Next.js 15 App Router uses Server Components by default, but our API calls are client-side
- Centralized error handling in API client ensures consistency
- Component-level error state provides flexibility for different error displays
- No need for error boundaries (those are for React rendering errors, not API errors)

**Implementation Approach**:

```typescript
// lib/errors.ts
export interface ApiError {
  error_code: string;
  message: string;
  details?: Array<{ field: string; message: string }>;
}

export function parseApiError(response: Response, data: any): ApiError {
  if (data?.error_code) {
    return data as ApiError;
  }
  // Fallback for non-standard errors
  return {
    error_code: `HTTP_${response.status}`,
    message: data?.message || response.statusText || 'An error occurred',
    details: undefined
  };
}

// lib/api.ts (enhanced)
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getToken(); // From Better Auth

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (response.status === 401) {
    // Redirect to signin
    window.location.href = '/signin?error=session_expired';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const apiError = parseApiError(response, errorData);
    throw apiError; // Throw structured error
  }

  return response.json();
}

// Component usage
const [error, setError] = useState<ApiError | null>(null);

try {
  const task = await apiRequest<Task>(`/api/tasks/${id}`);
  setTask(task);
} catch (err) {
  if (err && typeof err === 'object' && 'error_code' in err) {
    setError(err as ApiError);
  } else {
    setError({
      error_code: 'UNKNOWN_ERROR',
      message: 'An unexpected error occurred',
    });
  }
}
```

**Alternatives Considered**:
- **React Error Boundaries**: Rejected - designed for rendering errors, not async API errors
- **Global error state (Context/Redux)**: Rejected - overkill for this use case, component-level is sufficient
- **Toast notifications library**: Considered for future - inline errors are clearer for now
- **Next.js error.tsx files**: Rejected - those are for page-level errors, not API errors

**Trade-offs**:
- Component-level error state requires more boilerplate but provides flexibility
- No global error notification system (can add later if needed)

**References**:
- Next.js 15 App Router: https://nextjs.org/docs/app
- React Error Handling: https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary

---

## Decision 4: JWT Validation Edge Cases

**Question**: How to handle malformed JWT tokens, expired tokens, and missing tokens with clear error messages?

**Decision**: Enhance existing JWT verification in dependencies.py with comprehensive error handling and specific error codes.

**Rationale**:
- python-jose already provides detailed exception types
- Map jose exceptions to specific error codes for frontend
- Dependency injection ensures all endpoints get consistent validation
- Clear error messages help users understand what went wrong

**Implementation Approach**:

```python
# api/dependencies.py (enhanced)
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    if not credentials:
        raise AppException(
            401,
            "MISSING_TOKEN",
            "Authentication required. Please sign in."
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AppException(
                401,
                "INVALID_TOKEN",
                "Invalid authentication token. Please sign in again."
            )
        return user_id

    except ExpiredSignatureError:
        raise AppException(
            401,
            "TOKEN_EXPIRED",
            "Your session has expired. Please sign in again."
        )
    except JWTError:
        raise AppException(
            401,
            "INVALID_TOKEN",
            "Invalid authentication token. Please sign in again."
        )
```

**Alternatives Considered**:
- **Middleware-based JWT validation**: Rejected - dependency injection is more flexible and testable
- **Custom JWT library**: Rejected - python-jose is well-maintained and sufficient
- **Token refresh logic**: Out of scope - Better Auth handles this

**Error Code Mapping**:
- `MISSING_TOKEN`: No Authorization header provided
- `TOKEN_EXPIRED`: JWT exp claim is in the past
- `INVALID_TOKEN`: Malformed JWT, invalid signature, or missing claims

**References**:
- python-jose documentation: https://python-jose.readthedocs.io/
- JWT Best Practices: https://datatracker.ietf.org/doc/html/rfc8725

---

## Decision 5: Validation Patterns

**Question**: What is the best approach for field-level validation in FastAPI with Pydantic that returns structured 422 responses?

**Decision**: Use Pydantic validators with custom exception handler for RequestValidationError to format field-level errors.

**Rationale**:
- Pydantic provides built-in validation with clear error messages
- FastAPI automatically returns 422 for validation errors
- Custom exception handler formats errors into our standard structure
- Field-level validators enable complex validation logic

**Implementation Approach**:

```python
# schemas/task.py (enhanced)
from pydantic import BaseModel, validator, Field

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)

    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

# main.py (add exception handler)
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = []
    for error in exc.errors():
        field = '.'.join(str(loc) for loc in error['loc'] if loc != 'body')
        details.append(ErrorDetail(
            field=field,
            message=error['msg']
        ))

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Invalid input data",
            details=details
        ).dict()
    )
```

**Alternatives Considered**:
- **Manual validation in endpoint**: Rejected - code duplication, loses Pydantic benefits
- **Third-party validation library**: Rejected - Pydantic is sufficient and well-integrated
- **Database constraints only**: Rejected - need to catch errors before database call

**Validation Rules**:
- Title: Required, 1-200 characters, not empty/whitespace
- Description: Optional, max 2000 characters
- All fields: Strip whitespace, sanitize input

**References**:
- Pydantic Validators: https://docs.pydantic.dev/latest/concepts/validators/
- FastAPI Validation: https://fastapi.tiangolo.com/tutorial/body-fields/

---

## Decision 6: Ownership Enforcement

**Question**: How to implement reusable authorization checks in FastAPI that prevent ownership bypass attempts?

**Decision**: Create reusable authorization utility functions that verify ownership after fetching resources.

**Rationale**:
- Centralized authorization logic ensures consistency
- Utility functions are reusable across all task endpoints
- Clear separation between authentication (JWT) and authorization (ownership)
- Prevents code duplication and reduces error risk

**Implementation Approach**:

```python
# core/authorization.py (new file)
from typing import Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from .errors import AppException

async def get_user_task_or_404(
    task_id: int,
    user_id: str,
    session: AsyncSession,
    for_update: bool = False
) -> Task:
    """
    Fetch a task and verify ownership.
    Raises 404 if task doesn't exist.
    Raises 403 if user doesn't own the task.
    """
    statement = select(Task).where(Task.id == task_id)
    if for_update:
        statement = statement.with_for_update()

    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    if not task:
        raise AppException(
            404,
            "TASK_NOT_FOUND",
            f"Task with ID {task_id} not found"
        )

    if task.user_id != user_id:
        raise AppException(
            403,
            "FORBIDDEN",
            "You don't have permission to access this task"
        )

    return task

# Usage in endpoints
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    task = await get_user_task_or_404(task_id, current_user, session)
    return task
```

**Alternatives Considered**:
- **Decorator-based authorization**: Rejected - less flexible, harder to test
- **Middleware authorization**: Rejected - can't access route parameters easily
- **Policy-based authorization (Casbin)**: Rejected - overkill for simple ownership checks
- **Inline checks in each endpoint**: Rejected - code duplication, inconsistent error handling

**Security Principles**:
1. Always fetch resource first, then check ownership
2. Return 404 for non-existent resources (don't leak existence)
3. Return 403 for ownership violations (clear authorization failure)
4. Never trust user_id from request body - always use JWT user_id

**References**:
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- OWASP Authorization Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html

---

## Decision 7: Loading States

**Question**: What is the React 18 pattern for managing loading states during async operations with proper error boundaries?

**Decision**: Use React useState for loading/error states with Suspense for future optimization, no error boundaries needed for API errors.

**Rationale**:
- useState is simple and sufficient for component-level loading states
- React 18 Suspense is designed for data fetching but requires framework support (not needed now)
- Error boundaries are for rendering errors, not async API errors
- Component-level state provides fine-grained control

**Implementation Approach**:

```typescript
// Component pattern
'use client';

import { useState, useEffect } from 'react';

export default function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    async function fetchTasks() {
      try {
        setLoading(true);
        setError(null);
        const data = await apiRequest<Task[]>('/api/tasks');
        setTasks(data);
      } catch (err) {
        setError(err as ApiError);
      } finally {
        setLoading(false);
      }
    }
    fetchTasks();
  }, []);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage error={error} onRetry={() => window.location.reload()} />;
  }

  if (tasks.length === 0) {
    return <EmptyState message="No tasks yet. Create your first task!" />;
  }

  return <div>{/* Render tasks */}</div>;
}
```

**Alternatives Considered**:
- **React Suspense**: Considered for future - requires more setup, not needed for MVP
- **SWR/React Query**: Rejected - adds dependency, overkill for simple CRUD
- **Global loading state**: Rejected - component-level is more flexible
- **Loading skeletons**: Considered for future enhancement

**Loading State Patterns**:
- Show spinner during initial load
- Show inline loading for mutations (button disabled state)
- Show error message with retry option
- Show empty state when no data

**References**:
- React 18 Features: https://react.dev/blog/2022/03/29/react-v18
- React Suspense: https://react.dev/reference/react/Suspense

---

## Summary of Decisions

| Decision | Approach | Key Benefit |
|----------|----------|-------------|
| Error Response Standardization | Custom HTTPException + Pydantic models | Consistent structure, type safety |
| Race Condition Prevention | SELECT FOR UPDATE with row locking | Simple, no schema changes |
| Frontend Error Handling | Centralized API client + component state | Consistency, flexibility |
| JWT Validation Edge Cases | Enhanced dependency with specific error codes | Clear user feedback |
| Validation Patterns | Pydantic validators + custom exception handler | Automatic validation, structured errors |
| Ownership Enforcement | Reusable authorization utility functions | DRY, consistent security |
| Loading States | useState with loading/error/empty patterns | Simple, sufficient for use case |

## Implementation Priority

1. **Backend error infrastructure** (Decisions 1, 4, 5, 6) - Foundation for all other work
2. **Race condition prevention** (Decision 2) - Critical for data integrity
3. **Frontend error handling** (Decision 3) - Depends on backend error structure
4. **Loading states** (Decision 7) - UI polish, can be done in parallel with error handling

## Next Steps

Proceed to Phase 1: Design Artifacts
- Create data-model.md with ErrorResponse entity
- Create contracts/error-responses.md with all error formats
- Create contracts/api-endpoints-updated.md with error specifications
- Create quickstart.md with testing guide for error scenarios
