# Tasks: Todo Application Production Readiness

**Input**: Design documents from `/specs/002-todo-robustness/`
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

## Phase 1: Foundational (Blocking Prerequisites)

**Purpose**: Backend error handling infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T001 [P] Create backend/src/core/errors.py with AppException class and error code constants
- [x] T002 [P] Create backend/src/schemas/errors.py with ErrorResponse and ErrorDetail Pydantic schemas
- [x] T003 Create backend/src/core/authorization.py with get_user_task_or_404 utility function for ownership checks
- [x] T004 Enhance backend/src/api/dependencies.py with improved get_current_user error handling (MISSING_TOKEN, TOKEN_EXPIRED, INVALID_TOKEN)
- [x] T005 Enhance backend/src/main.py with global exception handlers for AppException and RequestValidationError

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 2: User Story 1 - Clear Error Feedback (Priority: P1) 🎯 MVP

**Goal**: Users receive clear, actionable feedback for authentication, authorization, and validation errors

**Independent Test**: Trigger various error conditions (expired JWT, accessing another user's task, submitting invalid data) and verify appropriate error messages are displayed in the UI

### Implementation for User Story 1

#### Frontend Error Infrastructure

- [x] T006 [P] [US1] Create frontend/src/types/errors.ts with ApiError interface
- [x] T007 [P] [US1] Create frontend/src/lib/errors.ts with parseApiError and getErrorMessage utility functions
- [x] T008 [US1] Enhance frontend/src/lib/api.ts with error parsing, 401 redirect, and structured error throwing
- [x] T009 [P] [US1] Create frontend/src/components/ErrorMessage.tsx reusable error display component

#### Frontend Error Display Integration

- [x] T010 [US1] Enhance frontend/src/app/(protected)/tasks/page.tsx with error state, loading state, and empty state handling
- [x] T011 [US1] Enhance frontend/src/app/(protected)/tasks/[id]/page.tsx with 403/404 error handling and error display
- [x] T012 [P] [US1] Enhance frontend/src/components/TaskList.tsx with loading spinner, empty state message, and error display
- [x] T013 [P] [US1] Enhance frontend/src/components/TaskItem.tsx with error handling for delete and toggle operations
- [x] T014 [P] [US1] Enhance frontend/src/components/TaskForm.tsx with validation feedback and error display
- [x] T015 [US1] Enhance frontend/src/app/(auth)/signin/page.tsx with error feedback for authentication failures
- [x] T016 [US1] Enhance frontend/src/app/(auth)/signup/page.tsx with error feedback for registration failures

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 3: User Story 2 - Backend Validation and Consistency (Priority: P2)

**Goal**: Backend enforces data integrity with consistent, well-structured error responses

**Independent Test**: Send API requests directly (via curl or Postman) with invalid data and verify appropriate HTTP status codes and error structures are returned

### Implementation for User Story 2

#### Backend Validation Enhancement

- [x] T017 [US2] Enhance backend/src/schemas/task.py with validation rules (title: 1-200 chars, not empty/whitespace; description: max 2000 chars)
- [x] T018 [US2] Enhance GET /api/tasks endpoint in backend/src/api/routes/tasks.py with error handling (401, 500)
- [x] T019 [US2] Enhance POST /api/tasks endpoint in backend/src/api/routes/tasks.py with validation, error handling (401, 422, 500)
- [x] T020 [US2] Enhance GET /api/tasks/{id} endpoint in backend/src/api/routes/tasks.py with ownership check using get_user_task_or_404 (401, 403, 404, 500)
- [x] T021 [US2] Enhance PUT /api/tasks/{id} endpoint in backend/src/api/routes/tasks.py with validation, ownership check, prevent user_id changes (401, 403, 404, 422, 500)
- [x] T022 [US2] Enhance DELETE /api/tasks/{id} endpoint in backend/src/api/routes/tasks.py with ownership check (401, 403, 404, 500)
- [x] T023 [US2] Enhance PATCH /api/tasks/{id}/complete endpoint in backend/src/api/routes/tasks.py with SELECT FOR UPDATE for idempotent toggle, ownership check (401, 403, 404, 500)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 4: User Story 3 - Security Enforcement (Priority: P3)

**Goal**: Strict authentication and authorization rules prevent cross-user data access and ownership manipulation

**Independent Test**: Attempt to manipulate JWT tokens, modify user_id in requests, and access other users' resources, verifying all attempts are rejected with appropriate error codes

### Implementation for User Story 3

#### Security Hardening Verification

- [x] T024 [P] [US3] Verify JWT verification is enforced on all 6 task endpoints (already implemented in dependencies.py)
- [x] T025 [P] [US3] Verify user_id extraction from JWT only (never from request body) in all endpoints
- [x] T026 [P] [US3] Verify ownership enforcement on all task operations using get_user_task_or_404
- [x] T027 [US3] Verify ownership change prevention in PUT /api/tasks/{id} endpoint (reject user_id in request body)
- [x] T028 [US3] Test JWT tampering scenarios (malformed token, invalid signature, expired token) and verify 401 responses
- [x] T029 [US3] Test cross-user access scenarios (User A accessing User B's tasks) and verify 404 responses
- [x] T030 [US3] Test ownership bypass attempts (modifying user_id in request) and verify backend ignores client-provided user_id

**Checkpoint**: All user stories should now be independently functional

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T031 [P] Add loading states to frontend/src/components/TaskList.tsx (spinner during fetch)
- [x] T032 [P] Add loading states to frontend/src/components/TaskItem.tsx (disabled buttons during delete/toggle)
- [x] T033 [P] Add loading states to frontend/src/components/TaskForm.tsx (disabled submit button during creation)
- [x] T034 [P] Add empty state message to frontend/src/components/TaskList.tsx ("No tasks yet. Create your first task!")
- [x] T035 [P] Verify all backend endpoints return proper HTTP status codes (200, 201, 204, 401, 403, 404, 422, 500)
- [x] T036 [P] Verify error messages are user-friendly (no stack traces, internal paths, or technical jargon)
- [x] T037 [P] Verify responsive design works on mobile devices for all error states and loading states
- [x] T038 Manual testing: Authentication error scenarios per quickstart.md Test Suite 1 (missing token, expired token, malformed token)
- [x] T039 Manual testing: Authorization & ownership scenarios per quickstart.md Test Suite 2 (cross-user access, ownership change attempts)
- [x] T040 Manual testing: Validation error scenarios per quickstart.md Test Suite 3 (empty title, whitespace title, title too long, description too long)
- [x] T041 Manual testing: Resource not found scenarios per quickstart.md Test Suite 4 (non-existent task ID)
- [x] T042 Manual testing: Race condition & concurrency scenarios per quickstart.md Test Suite 5 (concurrent completion toggle)
- [x] T043 Manual testing: Frontend error display per quickstart.md Test Suite 6 (loading states, empty state, error messages)
- [x] T044 Manual testing: Multi-user isolation per quickstart.md Test Suite 7 (task list isolation, cross-user access prevention)
- [x] T045 Manual testing: Security testing per quickstart.md Test Suite 8 (JWT tampering, SQL injection, XSS prevention)
- [x] T046 Verify all success criteria from spec.md (SC-001 through SC-010)
- [x] T047 Verify constitution compliance (security first, separation of concerns, API-centric design)
- [x] T048 Run quickstart.md validation to ensure all test scenarios pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: No dependencies - can start immediately - BLOCKS all user stories
- **User Stories (Phase 2+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 1) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 1) - Independent of US1 (backend-only changes)
- **User Story 3 (P3)**: Can start after Foundational (Phase 1) - Verifies security from US2 but is independently testable

### Within Each User Story

- Backend infrastructure before frontend integration
- Error handling utilities before component enhancements
- Core implementation before polish
- Story complete before moving to next priority

### Parallel Opportunities

- All Foundational tasks marked [P] can run in parallel (T001, T002 are independent)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each user story, tasks marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch frontend error infrastructure together (after Foundational complete):
Task: "Create frontend/src/types/errors.ts with ApiError interface"
Task: "Create frontend/src/lib/errors.ts with parseApiError utility"
Task: "Create frontend/src/components/ErrorMessage.tsx component"

# Launch component enhancements together (after error infrastructure exists):
Task: "Enhance frontend/src/components/TaskList.tsx with error display"
Task: "Enhance frontend/src/components/TaskItem.tsx with error handling"
Task: "Enhance frontend/src/components/TaskForm.tsx with validation feedback"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Foundational (CRITICAL - blocks all stories)
2. Complete Phase 2: User Story 1 (Clear Error Feedback)
3. **STOP and VALIDATE**: Test User Story 1 independently per quickstart.md
4. Deploy/demo if ready

### Incremental Delivery

1. Complete Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Frontend error handling)
   - Developer B: User Story 2 (Backend validation) - can start immediately
   - Developer C: User Story 3 (Security verification) - can start after US2 backend work
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are optional per specification - focus on manual validation per quickstart.md
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Count Summary

- **Phase 1 (Foundational)**: 5 tasks (BLOCKS all user stories)
- **Phase 2 (User Story 1 - Clear Error Feedback)**: 11 tasks
- **Phase 3 (User Story 2 - Backend Validation)**: 7 tasks
- **Phase 4 (User Story 3 - Security Enforcement)**: 7 tasks
- **Phase 5 (Polish)**: 18 tasks

**Total**: 48 tasks

**Parallel Opportunities**: 15 tasks marked [P] can run in parallel within their phase

**MVP Scope**: Phases 1-2 (16 tasks) deliver working error handling system with clear user feedback

---

## Validation Checklist

- [x] All tasks follow checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- [x] Tasks organized by user story (US1, US2, US3)
- [x] Each user story has independent test criteria
- [x] Foundational phase clearly marked as blocking
- [x] Parallel opportunities identified with [P] marker
- [x] File paths included in all implementation tasks
- [x] Dependencies section shows story completion order
- [x] Implementation strategy includes MVP-first approach
- [x] Manual testing tasks reference quickstart.md test suites
