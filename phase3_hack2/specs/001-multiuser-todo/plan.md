# Implementation Plan: Multi-User Todo Web Application

**Branch**: `001-multiuser-todo` | **Date**: 2026-02-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-multiuser-todo/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a secure, full-stack multi-user Todo web application with JWT-based authentication. Users can sign up, sign in, and manage their personal tasks (create, read, update, delete, toggle completion) with strict user isolation enforced at the API layer. Frontend (Next.js + Better Auth) and backend (FastAPI + SQLModel + Neon PostgreSQL) operate as independent services communicating via RESTful APIs.

## Technical Context

**Language/Version**:
- Frontend: TypeScript with Next.js 16+
- Backend: Python 3.11+

**Primary Dependencies**:
- Frontend: Next.js 16+ (App Router), Better Auth (JWT plugin), React 18+
- Backend: FastAPI, SQLModel, PyJWT, python-jose, Pydantic, psycopg2-binary

**Storage**: Neon Serverless PostgreSQL (cloud-hosted)

**Testing**:
- Frontend: Vitest (unit/integration tests), Playwright (E2E tests) - optional per spec
- Backend: pytest with pytest-asyncio for async tests

**Target Platform**:
- Frontend: Modern web browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)
- Backend: Linux/Windows server environment (Python runtime)

**Project Type**: Web application (frontend + backend as separate services)

**Performance Goals**:
- API response time: <200ms p95 for task operations
- Page load time: <2 seconds for task list
- JWT validation: <100ms per request
- Support 10+ concurrent users

**Constraints**:
- JWT token must be verified on every API request
- All task queries must filter by authenticated user_id
- No in-memory storage (persistent PostgreSQL only)
- Frontend and backend must be independently runnable
- All secrets via environment variables

**Scale/Scope**:
- Initial deployment: 10-50 concurrent users
- Database: ~1000 tasks per user expected
- API endpoints: 6 task endpoints + authentication endpoints (managed by Better Auth)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Spec-Driven Development (NON-NEGOTIABLE)
- [x] Specification created via `/sp.specify` (spec.md exists)
- [x] Implementation plan being generated via `/sp.plan` (this file)
- [x] Tasks will be broken down via `/sp.tasks` (next step)
- [x] Implementation will follow via `/sp.implement` (final step)

**Status**: PASS - Following mandatory workflow

### ✅ II. Security First
- [x] JWT authentication required on ALL API endpoints
- [x] User ID extraction from verified JWT only (never from request body)
- [x] Task ownership enforcement on every CRUD operation
- [x] Unauthorized requests return HTTP 401
- [x] Shared secret (BETTER_AUTH_SECRET) via environment variables
- [x] No hardcoded credentials or tokens

**Status**: PASS - Security is foundational in design

### ✅ III. Separation of Concerns
- [x] Backend logic only in `/backend` directory
- [x] Frontend logic only in `/frontend` directory
- [x] Backend: Python FastAPI, SQLModel, database operations, business logic
- [x] Frontend: Next.js, UI components, user interactions, API consumption
- [x] Services independently runnable
- [x] No shared code (except API contracts documentation)

**Status**: PASS - Clear boundaries enforced

### ✅ IV. API-Centric Design
- [x] Frontend communicates exclusively via REST APIs
- [x] RESTful endpoint design
- [x] All requests include `Authorization: Bearer <token>` header
- [x] Clear request/response schemas (Pydantic models)
- [x] Backend never trusts client-provided user_id without JWT validation
- [x] API contracts define integration boundary

**Status**: PASS - API-first architecture

### ✅ V. Reproducibility & Traceability
- [x] PHRs created for significant interactions
- [x] ADRs for significant design choices (will be suggested during planning)
- [x] All changes reference specs, plans, and tasks
- [x] Git commits include context and rationale
- [x] No manual coding—all via Claude Code + Spec-Kit Plus

**Status**: PASS - Traceability maintained

**Overall Gate Status**: ✅ PASS - All constitutional requirements satisfied

## Project Structure

### Documentation (this feature)

```text
specs/001-multiuser-todo/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── api-endpoints.md # REST API contract documentation
│   └── jwt-payload.md   # JWT token structure
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py          # Task SQLModel
│   │   └── user.py          # User reference model (if needed)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py  # JWT verification dependency
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── tasks.py     # Task CRUD endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Environment configuration
│   │   ├── database.py      # Database connection
│   │   └── security.py      # JWT verification logic
│   └── schemas/
│       ├── __init__.py
│       └── task.py          # Pydantic request/response schemas
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_auth.py         # JWT verification tests
│   └── test_tasks.py        # Task endpoint tests
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── README.md                # Backend setup instructions

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home/landing page
│   │   ├── (auth)/
│   │   │   ├── signin/
│   │   │   │   └── page.tsx # Sign-in page
│   │   │   └── signup/
│   │   │       └── page.tsx # Sign-up page
│   │   └── (protected)/
│   │       ├── tasks/
│   │       │   ├── page.tsx        # Task list page
│   │       │   └── [id]/
│   │       │       └── page.tsx    # Task detail page
│   │       └── layout.tsx          # Protected route layout
│   ├── components/
│   │   ├── TaskList.tsx     # Task list component
│   │   ├── TaskForm.tsx     # Task create/edit form
│   │   └── TaskItem.tsx     # Individual task component
│   ├── lib/
│   │   ├── auth.ts          # Better Auth configuration
│   │   └── api.ts           # API client with JWT injection
│   └── types/
│       └── task.ts          # TypeScript task types
├── tests/
│   └── (test files)
├── .env.local.example       # Environment variable template
├── package.json             # Node dependencies
├── tsconfig.json            # TypeScript configuration
├── next.config.js           # Next.js configuration
└── README.md                # Frontend setup instructions
```

**Structure Decision**: Web application structure (Option 2) selected based on constitution requirements for strict separation of concerns. Backend and frontend are completely independent services with their own dependencies, configurations, and runtime environments. Communication occurs exclusively via REST APIs with JWT authentication.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitutional requirements are satisfied by the proposed architecture.
