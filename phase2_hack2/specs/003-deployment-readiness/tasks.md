# Tasks: Deployment Readiness

**Input**: Design documents from `/specs/003-deployment-readiness/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL per specification. This implementation focuses on manual validation per quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below follow web application structure from plan.md

---

## Phase 1: Setup (Security & Documentation Foundation)

**Purpose**: Fix security issue and prepare documentation foundation

- [X] T001 [P] Fix backend/.env.example to remove real database credentials (replace with placeholder)
- [X] T002 [P] Verify frontend/.env.local.example contains only placeholder values (no real secrets)

**Checkpoint**: Security fix complete - no real credentials in example files

---

## Phase 2: User Story 1 - Environment Configuration Validation (Priority: P1) 🎯 MVP

**Goal**: Developers and reviewers can quickly identify missing or misconfigured environment variables at startup

**Independent Test**: Start backend/frontend with missing environment variables and verify clear error messages are displayed before the application attempts to run

### Backend Environment Validation

- [X] T003 [US1] Enhance backend/src/core/config.py to use Pydantic Settings with required field validation for BETTER_AUTH_SECRET, DATABASE_URL, CORS_ORIGINS
- [X] T004 [US1] Update backend/src/main.py to catch Pydantic ValidationError at startup and display clear error messages
- [ ] T005 [US1] Test backend startup without BETTER_AUTH_SECRET and verify error message "Missing required environment variable: BETTER_AUTH_SECRET"
- [ ] T006 [US1] Test backend startup without DATABASE_URL and verify error message "Missing required environment variable: DATABASE_URL"
- [ ] T007 [US1] Test backend startup with all required variables and verify successful startup

### Frontend Environment Validation

- [X] T008 [P] [US1] Add environment variable validation check in frontend/src/lib/api.ts or frontend/src/app/layout.tsx for NEXT_PUBLIC_API_URL
- [ ] T009 [US1] Test frontend build/startup without NEXT_PUBLIC_API_URL and verify clear error message
- [ ] T010 [US1] Test frontend startup with all required variables and verify successful startup

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Both backend and frontend fail fast with clear error messages when environment variables are missing.

---

## Phase 3: User Story 2 - Backend Health Monitoring (Priority: P2)

**Goal**: Operators and reviewers can verify backend operational status through a dedicated health-check endpoint

**Independent Test**: Call the health endpoint with various backend states (database connected, database disconnected) and verify appropriate responses

### Health Check Implementation

- [X] T011 [P] [US2] Create backend/src/schemas/health.py with HealthCheckResponse Pydantic schema (status, database, timestamp, error fields)
- [X] T012 [US2] Implement GET /health endpoint in backend/src/main.py that tests database connectivity with SELECT 1 query
- [X] T013 [US2] Configure health endpoint to return 200 OK with status "healthy" when database is connected
- [X] T014 [US2] Configure health endpoint to return 503 Service Unavailable with status "unhealthy" when database is disconnected
- [X] T015 [US2] Ensure health endpoint does NOT require authentication (public endpoint)
- [ ] T016 [US2] Test health endpoint with database connected and verify 200 OK response with correct JSON structure
- [ ] T017 [US2] Test health endpoint with database disconnected and verify 503 response with error details
- [ ] T018 [US2] Verify health endpoint responds within 2 seconds

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Health endpoint is operational and provides accurate service status.

---

## Phase 4: User Story 3 - Structured Operational Logging (Priority: P3)

**Goal**: Operators can diagnose authentication failures, authorization issues, and database problems through structured logs

**Independent Test**: Trigger various error conditions (invalid JWT, expired token, database error) and verify appropriate log entries are created with sufficient context

### Logging Infrastructure

- [X] T019 [P] [US3] Create JSON log formatter in backend/src/core/logging.py with JSONFormatter class (timestamp, level, message, module, function, event_type fields)
- [X] T020 [US3] Configure Python logger in backend/src/main.py to use JSONFormatter and output to stdout

### Authentication Logging

- [X] T021 [P] [US3] Add structured logging to backend/src/api/dependencies.py get_current_user function for JWT verification failures (event_type: auth_failure)
- [X] T022 [US3] Ensure JWT token values are NOT logged (only error type and timestamp)
- [ ] T023 [US3] Test authentication failure logging by sending invalid JWT and verifying log entry without token value

### Authorization Logging

- [X] T024 [P] [US3] Add structured logging to backend/src/core/authorization.py get_user_task_or_404 function for ownership check failures (event_type: authz_failure)
- [X] T025 [US3] Include user_id and resource_id in authorization failure logs (no sensitive data)
- [ ] T026 [US3] Test authorization failure logging by accessing another user's task and verifying log entry with user_id and task_id

### Database Error Logging

- [X] T027 [P] [US3] Add structured logging to backend/src/core/database.py for database connection errors (event_type: db_error)
- [X] T028 [US3] Ensure database connection strings with credentials are NOT logged (sanitize error messages)
- [ ] T029 [US3] Test database error logging by simulating connection failure and verifying sanitized log entry

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Structured logging provides operational visibility without exposing sensitive data.

---

## Phase 5: User Story 4 - Service Independence Verification (Priority: P4)

**Goal**: Reviewers can verify that frontend and backend are truly independent services

**Independent Test**: Start frontend without backend running, and backend without database, verifying appropriate error handling and user feedback

### Service Independence Validation

- [ ] T030 [P] [US4] Verify backend can start and serve API documentation at /docs without frontend running
- [ ] T031 [P] [US4] Verify frontend displays clear error message (not generic error) when backend is unavailable
- [ ] T032 [US4] Test backend startup without database and verify it fails fast with clear database connection error
- [ ] T033 [US4] Test frontend with backend stopped mid-session and verify graceful error handling with user-friendly message
- [ ] T034 [US4] Document service independence testing procedure in quickstart.md troubleshooting section

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 4 should all work independently. Service independence is validated and documented.

---

## Phase 6: User Story 5 - Reviewer Documentation and Setup (Priority: P5)

**Goal**: Reviewers can set up and run the complete application locally within 15 minutes

**Independent Test**: Have a new developer follow the quickstart guide from scratch and successfully run the application

### Documentation Updates

- [X] T035 [P] [US5] Update backend/README.md with deployment readiness features (environment validation, health check, logging)
- [X] T036 [P] [US5] Update frontend/README.md with environment validation information and troubleshooting tips
- [X] T037 [US5] Verify quickstart.md includes all required environment variables with examples (already created in planning phase)
- [X] T038 [US5] Verify quickstart.md includes troubleshooting section for common issues (already created in planning phase)
- [ ] T039 [US5] Test quickstart guide by following it from scratch on a clean environment and verify 15-minute setup time

**Checkpoint**: At this point, ALL user stories (1-5) should be complete and independently testable. Documentation enables reviewers to quickly understand and run the application.

---

## Phase 7: Final Validation & Polish

**Purpose**: Cross-cutting validation and final checks

- [ ] T040 [P] Re-test all User Story 1 acceptance scenarios (environment validation)
- [ ] T041 [P] Re-test all User Story 2 acceptance scenarios (health monitoring)
- [ ] T042 [P] Re-test all User Story 3 acceptance scenarios (structured logging)
- [ ] T043 [P] Re-test all User Story 4 acceptance scenarios (service independence)
- [ ] T044 [P] Re-test all User Story 5 acceptance scenarios (documentation)
- [ ] T045 Verify no sensitive data appears in logs (scan logs for tokens, passwords, credentials)
- [ ] T046 Verify no real credentials in .env.example files (security check)
- [ ] T047 Run complete end-to-end test following quickstart.md from scratch
- [ ] T048 Verify all success criteria from spec.md are met (12 success criteria)

---

## Dependencies & Execution Order

### User Story Completion Order

```
Phase 1 (Setup)
    ↓
Phase 2 (US1 - Environment Validation) ← MVP
    ↓
Phase 3 (US2 - Health Monitoring)
    ↓
Phase 4 (US3 - Structured Logging)
    ↓
Phase 5 (US4 - Service Independence)
    ↓
Phase 6 (US5 - Documentation)
    ↓
Phase 7 (Final Validation)
```

### Parallel Execution Opportunities

**Within User Story 1 (Environment Validation)**:
- T008 (frontend validation) can run in parallel with T003-T007 (backend validation)

**Within User Story 2 (Health Monitoring)**:
- T011 (schema creation) can run in parallel with other tasks (different file)

**Within User Story 3 (Structured Logging)**:
- T019 (logging infrastructure) can run in parallel with T021, T024, T027 (different files)
- T021 (auth logging), T024 (authz logging), T027 (db logging) can run in parallel (different files)

**Within User Story 4 (Service Independence)**:
- T030, T031, T032, T033 can all run in parallel (validation tasks, different components)

**Within User Story 5 (Documentation)**:
- T035, T036 can run in parallel (different README files)

**Within Phase 7 (Final Validation)**:
- T040, T041, T042, T043, T044, T046 can all run in parallel (independent validation tasks)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Recommended MVP**: User Story 1 only (Environment Configuration Validation)

**Rationale**:
- Environment validation is foundational and prevents most deployment failures
- Can be implemented and tested independently
- Provides immediate value for reviewers
- Enables safe progression to other stories

**MVP Tasks**: T001-T010 (10 tasks)

### Incremental Delivery

1. **Sprint 1**: Setup + US1 (Environment Validation) - Tasks T001-T010
2. **Sprint 2**: US2 (Health Monitoring) - Tasks T011-T018
3. **Sprint 3**: US3 (Structured Logging) - Tasks T019-T029
4. **Sprint 4**: US4 (Service Independence) - Tasks T030-T034
5. **Sprint 5**: US5 (Documentation) - Tasks T035-T039
6. **Sprint 6**: Final Validation - Tasks T040-T048

### Testing Approach

**Manual Validation** (per constitution):
- Each user story has independent test criteria
- Follow quickstart.md for end-to-end testing
- Verify acceptance scenarios from spec.md
- No automated tests required (optional per constitution)

**Test Scenarios**:
- US1: Start services with missing env vars, verify error messages
- US2: Call /health endpoint, verify responses
- US3: Trigger errors, verify log entries
- US4: Run services independently, verify graceful failures
- US5: Follow quickstart guide, verify 15-minute setup

---

## Task Summary

**Total Tasks**: 48
- Phase 1 (Setup): 2 tasks
- Phase 2 (US1 - Environment Validation): 8 tasks
- Phase 3 (US2 - Health Monitoring): 8 tasks
- Phase 4 (US3 - Structured Logging): 11 tasks
- Phase 5 (US4 - Service Independence): 5 tasks
- Phase 6 (US5 - Documentation): 5 tasks
- Phase 7 (Final Validation): 9 tasks

**Parallel Opportunities**: 15 tasks marked with [P] can run in parallel

**MVP Scope**: 10 tasks (T001-T010) for User Story 1

**Estimated Completion**:
- MVP (US1): ~2-3 hours
- Full Feature (US1-US5): ~8-10 hours
- With Final Validation: ~10-12 hours

---

## File Modifications Summary

### Backend Files Modified
- `backend/.env.example` - Remove real credentials (T001)
- `backend/src/core/config.py` - Add Pydantic Settings validation (T003)
- `backend/src/main.py` - Add startup validation, health endpoint (T004, T012, T020)
- `backend/src/schemas/health.py` - NEW FILE - Health check schema (T011)
- `backend/src/core/logging.py` - NEW FILE - JSON log formatter (T019)
- `backend/src/api/dependencies.py` - Add auth failure logging (T021)
- `backend/src/core/authorization.py` - Add authz failure logging (T024)
- `backend/src/core/database.py` - Add db error logging (T027)
- `backend/README.md` - Update with deployment features (T035)

### Frontend Files Modified
- `frontend/.env.local.example` - Verify placeholder values (T002)
- `frontend/src/lib/api.ts` or `frontend/src/app/layout.tsx` - Add env validation (T008)
- `frontend/README.md` - Update with env validation info (T036)

### Documentation Files
- `specs/003-deployment-readiness/quickstart.md` - Already complete from planning phase (T037, T038)

**Total Files Modified**: 11 files (2 new files created)

---

## Success Criteria Validation

Each task maps to success criteria from spec.md:

- **SC-001**: Backend fails fast within 2 seconds → T003-T007
- **SC-002**: Error messages clearly identify missing variables → T003-T010
- **SC-003**: Health endpoint responds within 2 seconds → T018
- **SC-004**: Health endpoint accurately reflects database status → T016-T017
- **SC-005**: Authentication failures logged with context → T021-T023
- **SC-006**: No sensitive data in logs → T022, T028, T045
- **SC-007**: Frontend displays user-friendly errors → T031, T033
- **SC-008**: Backend runs independently → T030
- **SC-009**: Frontend runs independently → T031
- **SC-010**: 15-minute setup time → T039
- **SC-011**: All env variables documented → T037
- **SC-012**: Common issues have solutions → T038

All 12 success criteria are covered by the task breakdown.
