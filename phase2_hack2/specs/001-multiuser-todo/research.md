# Research: Multi-User Todo Web Application

**Feature**: 001-multiuser-todo
**Date**: 2026-02-04
**Purpose**: Document technical decisions and resolve clarifications from plan.md

## Overview

This document captures research findings and technical decisions for implementing a secure, full-stack multi-user Todo application with JWT authentication. All decisions align with the project constitution's requirements for security-first design, separation of concerns, and API-centric architecture.

---

## 1. Frontend Testing Framework

### Decision

**Unit/Integration Tests**: Vitest
**E2E Tests**: Playwright

### Rationale

**Vitest**:
- Native ESM support and faster than Jest
- Excellent TypeScript support out of the box
- Compatible with Next.js 16+ App Router
- Vite-powered, aligns with modern tooling
- Drop-in Jest replacement with similar API
- Better performance for large test suites

**Playwright**:
- Official Microsoft support, actively maintained
- Excellent Next.js App Router support
- Built-in test runner with parallel execution
- Cross-browser testing (Chromium, Firefox, WebKit)
- Better debugging experience with trace viewer
- More reliable for async operations and network requests

### Alternatives Considered

- **Jest**: Mature but slower, requires additional configuration for ESM and Next.js App Router
- **Cypress**: Good DX but slower execution, less reliable for network mocking, larger bundle size

### Implementation Notes

- Vitest config: `vitest.config.ts` with Next.js path aliases
- Playwright config: `playwright.config.ts` with baseURL pointing to local dev server
- Test organization: `tests/unit/` for Vitest, `tests/e2e/` for Playwright
- For this hackathon project: Testing is optional per spec, prioritize manual validation

---

## 2. Better Auth JWT Integration

### Decision

**Configuration**: Better Auth with JWT plugin enabled
**Token Storage**: HTTP-only cookies (secure, httpOnly, sameSite)
**Token Access**: Server-side extraction for API calls via middleware

### Rationale

- **HTTP-only cookies**: Most secure option, prevents XSS attacks, automatic inclusion in requests
- **Better Auth JWT plugin**: Provides JWT issuance out of the box, integrates with Next.js middleware
- **Server-side token handling**: Next.js App Router server components can access cookies securely
- **Automatic token refresh**: Better Auth handles token refresh transparently

### Alternatives Considered

- **localStorage**: Vulnerable to XSS attacks, not recommended for sensitive tokens
- **sessionStorage**: Same XSS vulnerability, doesn't persist across tabs
- **Memory-only**: Lost on page refresh, poor UX

### Implementation Notes

**Better Auth Configuration** (`frontend/src/lib/auth.ts`):
```typescript
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  jwt: {
    enabled: true,
    secret: process.env.BETTER_AUTH_SECRET!,
    expiresIn: "24h"
  },
  database: {
    // Better Auth manages its own user table
    // Backend will reference user IDs from JWT
  }
})
```

**Token Extraction for API Calls**:
- Use Next.js middleware to extract JWT from cookies
- Pass token to API client via headers
- Server components: `cookies().get('auth-token')`
- Client components: Use server actions or API routes as proxy

**JWT Payload Structure**:
```json
{
  "sub": "user-id-uuid",
  "email": "user@example.com",
  "iat": 1234567890,
  "exp": 1234654290
}
```

---

## 3. FastAPI JWT Verification

### Decision

**Library**: python-jose[cryptography]
**Approach**: Dependency injection with `Depends()`
**Validation**: Signature, expiration, and required claims

### Rationale

- **python-jose**: More comprehensive than PyJWT, includes cryptography support, better error handling
- **Dependency injection**: FastAPI best practice, reusable across endpoints, testable
- **Centralized verification**: Single source of truth for JWT validation logic
- **Type safety**: Returns typed user object, not raw token

### Alternatives Considered

- **PyJWT**: Simpler but less feature-rich, requires more manual validation
- **Middleware approach**: Less flexible, harder to test, applies globally even where not needed

### Implementation Notes

**JWT Verification Dependency** (`backend/src/api/dependencies.py`):
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

security = HTTPBearer()

class CurrentUser(BaseModel):
    user_id: str
    email: str

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return CurrentUser(user_id=user_id, email=email)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Usage in Endpoints**:
```python
@router.get("/api/tasks")
async def list_tasks(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # current_user.user_id is guaranteed to be from verified JWT
    tasks = db.query(Task).filter(Task.user_id == current_user.user_id).all()
    return tasks
```

**Key Validation Steps**:
1. Extract token from `Authorization: Bearer <token>` header
2. Verify signature using BETTER_AUTH_SECRET
3. Check expiration (exp claim)
4. Extract user_id from sub claim
5. Return typed CurrentUser object

---

## 4. SQLModel with Neon PostgreSQL

### Decision

**Connection**: Async SQLAlchemy engine with asyncpg driver
**Pooling**: Default SQLAlchemy pool (5-20 connections)
**Migrations**: Alembic with SQLModel metadata

### Rationale

- **Async engine**: FastAPI is async, async DB operations prevent blocking
- **asyncpg**: Fastest PostgreSQL driver for Python, native async support
- **Neon compatibility**: Neon supports standard PostgreSQL protocol, no special handling needed
- **Alembic**: Industry standard for migrations, integrates well with SQLModel

### Alternatives Considered

- **Sync engine**: Simpler but blocks event loop, poor performance under load
- **psycopg2**: Sync-only, would require thread pool
- **No migrations**: Manual schema management, error-prone, not reproducible

### Implementation Notes

**Connection String Format**:
```
postgresql+asyncpg://user:password@host/database?sslmode=require
```

**Database Configuration** (`backend/src/core/database.py`):
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

**Neon-Specific Considerations**:
- Neon requires SSL: `sslmode=require` in connection string
- Connection pooling: Neon handles pooling at server level, keep client pool small
- Serverless: Connections may be dropped, implement retry logic
- Environment variable: `DATABASE_URL` from Neon dashboard

**Migration Setup**:
```bash
# Initialize Alembic
alembic init alembic

# Configure alembic.ini to use SQLModel metadata
# Generate migration
alembic revision --autogenerate -m "Create tasks table"

# Apply migration
alembic upgrade head
```

---

## 5. Next.js App Router Authentication Patterns

### Decision

**Protected Routes**: Middleware-based route protection
**Component Strategy**: Server components for initial auth check, client components for interactive UI
**Session Persistence**: HTTP-only cookies with Better Auth session management

### Rationale

- **Middleware**: Runs before page render, can redirect unauthenticated users immediately
- **Server components**: Can access cookies securely, no client-side token exposure
- **Better Auth integration**: Handles session persistence automatically
- **Performance**: Server-side auth check is faster than client-side

### Alternatives Considered

- **Client-side only**: Vulnerable to flash of unauthenticated content, slower
- **Higher-order components**: Less idiomatic for App Router, more boilerplate
- **Route groups without middleware**: Requires manual checks in every page

### Implementation Notes

**Middleware** (`frontend/src/middleware.ts`):
```typescript
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')

  // Protected routes
  if (request.nextUrl.pathname.startsWith('/tasks')) {
    if (!token) {
      return NextResponse.redirect(new URL('/signin', request.url))
    }
  }

  // Auth routes (redirect if already authenticated)
  if (request.nextUrl.pathname.startsWith('/signin') ||
      request.nextUrl.pathname.startsWith('/signup')) {
    if (token) {
      return NextResponse.redirect(new URL('/tasks', request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/tasks/:path*', '/signin', '/signup']
}
```

**Protected Layout** (`frontend/src/app/(protected)/layout.tsx`):
```typescript
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

export default async function ProtectedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const token = cookies().get('auth-token')

  if (!token) {
    redirect('/signin')
  }

  return <>{children}</>
}
```

**API Client with JWT** (`frontend/src/lib/api.ts`):
```typescript
async function apiClient(endpoint: string, options: RequestInit = {}) {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include', // Include cookies
  })

  if (response.status === 401) {
    // Token expired, redirect to signin
    window.location.href = '/signin'
  }

  return response
}
```

**Session Persistence**:
- Better Auth automatically manages session cookies
- Cookies persist across browser sessions (until expiration)
- Token refresh handled by Better Auth (if configured)
- No manual token management needed in application code

---

## 6. API Endpoint Design

### Decision

**Pattern**: RESTful with user_id in path for ownership validation
**Format**: `/api/tasks` (list/create), `/api/tasks/{id}` (get/update/delete/complete)

### Rationale

- **RESTful conventions**: Industry standard, predictable, well-documented
- **Explicit user_id validation**: Backend validates JWT user_id matches route parameter
- **Resource-oriented**: Tasks are the primary resource, operations map to HTTP methods
- **Stateless**: Each request contains all necessary information (JWT token)

### Alternatives Considered

- **Query parameters**: Less RESTful, harder to validate ownership
- **GraphQL**: Overkill for simple CRUD, adds complexity
- **RPC-style**: Less standard, harder to cache

### Implementation Notes

**Endpoint Structure**:
```
GET    /api/tasks              - List all tasks for authenticated user
POST   /api/tasks              - Create new task for authenticated user
GET    /api/tasks/{id}         - Get task details (ownership verified)
PUT    /api/tasks/{id}         - Update task (ownership verified)
DELETE /api/tasks/{id}         - Delete task (ownership verified)
PATCH  /api/tasks/{id}/complete - Toggle completion (ownership verified)
```

**Ownership Enforcement Pattern**:
```python
@router.get("/api/tasks/{task_id}")
async def get_task(
    task_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return task
```

---

## 7. Environment Configuration

### Decision

**Frontend**: `.env.local` with `NEXT_PUBLIC_` prefix for client-side vars
**Backend**: `.env` with python-dotenv
**Shared Secret**: `BETTER_AUTH_SECRET` must be identical in both

### Rationale

- **Next.js convention**: `.env.local` for local development, gitignored by default
- **python-dotenv**: Standard Python approach, simple and reliable
- **Shared secret**: Critical for JWT verification, must match exactly
- **Security**: Secrets never committed, documented in .env.example files

### Implementation Notes

**Frontend `.env.local`**:
```
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend `.env`**:
```
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?sslmode=require
DEBUG=true
```

**Secret Generation**:
```bash
# Generate secure random secret
openssl rand -base64 32
```

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Frontend Testing | Vitest + Playwright | Modern, fast, Next.js App Router compatible |
| JWT Storage | HTTP-only cookies | Most secure, prevents XSS |
| JWT Verification | python-jose + Depends() | Comprehensive, testable, type-safe |
| Database | Async SQLAlchemy + asyncpg | Non-blocking, high performance |
| Migrations | Alembic | Industry standard, reproducible |
| Auth Pattern | Middleware + Server Components | Secure, performant, no token exposure |
| API Design | RESTful with ownership checks | Standard, predictable, secure |
| Environment | .env files with examples | Simple, secure, documented |

---

## Next Steps

1. Create data-model.md with Task and User entity definitions
2. Create contracts/ with detailed API endpoint specifications
3. Create quickstart.md with setup instructions
4. Proceed to task breakdown via `/sp.tasks`
