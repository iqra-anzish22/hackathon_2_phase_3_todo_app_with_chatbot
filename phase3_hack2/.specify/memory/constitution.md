<!--
Sync Impact Report:
- Version: Initial → 1.0.0
- Type: MAJOR (initial constitution)
- Modified Principles: N/A (new constitution)
- Added Sections: All sections (initial creation)
- Removed Sections: None
- Templates Status:
  ✅ plan-template.md - Constitution Check section present, aligns with principles
  ✅ spec-template.md - User story prioritization aligns with spec-driven approach
  ✅ tasks-template.md - Task organization aligns with separation of concerns
- Follow-up TODOs: None
-->

# Full-Stack Multi-User Todo Web Application Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

Every implementation MUST strictly follow approved specifications. No code may be written without a corresponding spec, plan, and task breakdown. The workflow is mandatory:

1. Write specification (via `/sp.specify`)
2. Generate implementation plan (via `/sp.plan`)
3. Break into tasks (via `/sp.tasks`)
4. Implement (via `/sp.implement`)

**Rationale**: Prevents scope creep, ensures traceability, and maintains alignment between business requirements and technical implementation. All work must be reproducible and auditable.

### II. Security First

User data isolation and authentication enforcement MUST occur at every layer. Security is not optional or deferred—it is foundational.

**Non-negotiable requirements**:
- JWT authentication required on ALL API endpoints
- User ID extraction from verified JWT only (never from request body)
- Task ownership enforcement on every CRUD operation
- Unauthorized requests MUST return HTTP 401
- Shared secrets MUST use environment variables (BETTER_AUTH_SECRET)
- No hardcoded credentials or tokens

**Rationale**: Multi-user applications require absolute data isolation. A single security bypass compromises all users. Defense-in-depth through authentication at every boundary.

### III. Separation of Concerns

Backend logic lives ONLY in `/backend`. Frontend logic lives ONLY in `/frontend`. No mixing, no exceptions.

**Enforcement**:
- Backend: Python FastAPI, SQLModel, database operations, business logic
- Frontend: Next.js, UI components, user interactions, API consumption
- Backend and frontend MUST be independently runnable services
- No shared code between frontend and backend (except API contracts)

**Rationale**: Clear boundaries enable independent development, testing, deployment, and scaling. Prevents tight coupling and enables technology-specific optimizations.

### IV. API-Centric Design

Frontend communicates with backend EXCLUSIVELY via REST APIs. No direct database access, no shared state, no side channels.

**Requirements**:
- RESTful endpoint design mandatory
- All requests include `Authorization: Bearer <token>` header
- Clear request/response schemas for every endpoint
- Backend never trusts client-provided user_id without JWT validation
- API contracts define the integration boundary

**Rationale**: API-first design ensures loose coupling, enables independent evolution of frontend and backend, and provides a clear integration contract that can be tested and versioned.

### V. Reproducibility & Traceability

All decisions, prompts, and iterations MUST be traceable and reviewable. Development is not a black box.

**Requirements**:
- Prompt History Records (PHRs) created for every significant interaction
- Architectural Decision Records (ADRs) for significant design choices
- All changes reference specs, plans, and tasks
- Git commits include context and rationale
- No manual coding—all implementation via Claude Code + Spec-Kit Plus

**Rationale**: Enables learning, debugging, auditing, and knowledge transfer. Future developers (human or AI) can understand why decisions were made and reproduce the development process.

## Architecture Constraints

### Frontend Stack

- **Framework**: Next.js 16+ with App Router
- **Authentication**: Better Auth with JWT enabled
- **API Communication**: fetch with Authorization headers
- **UI**: Responsive design required
- **Location**: All code in `/frontend` folder
- **Independence**: Must be runnable standalone (with backend API available)

### Backend Stack

- **Framework**: Python FastAPI
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT verification middleware (required on all endpoints)
- **API Design**: RESTful conventions
- **Location**: All code in `/backend` folder
- **Independence**: Must be runnable standalone

### Authentication Flow

1. User logs in via Better Auth (frontend)
2. Better Auth issues JWT token
3. Frontend stores token and includes in all API requests: `Authorization: Bearer <token>`
4. FastAPI middleware verifies JWT using `BETTER_AUTH_SECRET`
5. Middleware extracts authenticated user ID from verified token
6. Endpoint logic enforces task ownership using authenticated user ID
7. Unauthorized or invalid tokens return HTTP 401

**Shared Secret**:
- Environment variable: `BETTER_AUTH_SECRET`
- MUST be identical in frontend and backend `.env` files
- NEVER committed to version control

## Development Standards

### Workflow (Mandatory)

Follow the Agentic Dev Stack workflow for ALL features:

1. **Specify**: Write feature specification (`/sp.specify`)
2. **Plan**: Generate architectural plan (`/sp.plan`)
3. **Tasks**: Break into testable tasks (`/sp.tasks`)
4. **Implement**: Execute tasks (`/sp.implement`)
5. **Commit & PR**: Document and review (`/sp.git.commit_pr`)

**No manual coding**. All implementation via Claude Code + Spec-Kit Plus.

### Environment Configuration

- All secrets and configuration MUST use environment variables
- `.env` files for local development (never committed)
- Environment variables documented in README or quickstart
- Backend and frontend have separate `.env` files

### Service Independence

- Backend MUST be runnable independently (e.g., `uvicorn main:app`)
- Frontend MUST be runnable independently (e.g., `npm run dev`)
- Services communicate only via HTTP APIs
- No shared runtime dependencies

## API Standards

### Endpoint Design

- RESTful conventions mandatory
- All endpoints require authentication (JWT verification)
- All task operations scoped to authenticated user
- Clear request/response schemas (Pydantic models)

### Task Ownership Enforcement

Every task endpoint MUST enforce ownership:

- **List**: Return only authenticated user's tasks
- **Create**: Associate task with authenticated user
- **Read**: Verify task belongs to authenticated user
- **Update**: Verify task belongs to authenticated user
- **Delete**: Verify task belongs to authenticated user
- **Toggle Completion**: Verify task belongs to authenticated user

Attempting to access another user's task MUST return HTTP 403 Forbidden.

### Error Handling

- **401 Unauthorized**: Missing, invalid, or expired JWT
- **403 Forbidden**: Valid JWT but insufficient permissions (wrong task owner)
- **404 Not Found**: Resource doesn't exist (after ownership check)
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Unexpected server errors (logged)

## Persistence Rules

### Database Requirements

- All data MUST be stored in Neon PostgreSQL
- No in-memory storage (except caching with clear TTL)
- No temporary storage that survives process restart
- Database schema MUST support multi-user task isolation

### Data Model

- Tasks table MUST include `user_id` foreign key
- User authentication handled by Better Auth (separate user table)
- All queries MUST filter by authenticated user_id
- Database constraints enforce referential integrity

## Quality & Validation Standards

### Endpoint Requirements

Each endpoint MUST include:

- Clear request schema (Pydantic model)
- Clear response schema (Pydantic model)
- Authentication verification (JWT middleware)
- Ownership validation (user_id check)
- Error handling (try/except with appropriate HTTP codes)
- Input validation (Pydantic automatic validation)

### Testing Requirements

- API behavior MUST match specification exactly
- Manual testing of authentication flow required
- Manual testing of ownership enforcement required
- Test with multiple users to verify isolation

### Success Criteria

The project is complete when:

- ✅ Multi-user Todo web app with persistent storage
- ✅ Users can only see and modify their own tasks
- ✅ Frontend and backend authenticate independently via JWT
- ✅ All backend logic resides in `/backend`
- ✅ All frontend logic resides in `/frontend`
- ✅ All endpoints reject unauthenticated access
- ✅ Project passes hackathon review for spec-driven rigor

## Governance

### Amendment Process

1. Propose amendment with rationale
2. Document impact on existing specs, plans, and tasks
3. Update constitution with version bump (semantic versioning)
4. Propagate changes to dependent templates
5. Create ADR for significant governance changes

### Versioning Policy

- **MAJOR**: Backward incompatible principle removals or redefinitions
- **MINOR**: New principle/section added or materially expanded guidance
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

### Compliance

- All PRs and reviews MUST verify compliance with this constitution
- Complexity MUST be justified (see plan-template.md Complexity Tracking)
- Violations require explicit justification and approval
- Constitution supersedes all other practices

### Runtime Guidance

For day-to-day development guidance, see `CLAUDE.md` in the repository root.

**Version**: 1.0.0 | **Ratified**: 2026-02-04 | **Last Amended**: 2026-02-04
