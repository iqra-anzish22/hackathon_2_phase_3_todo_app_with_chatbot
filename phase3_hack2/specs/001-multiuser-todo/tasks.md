# Tasks: Multi-User Todo Web Application

**Input**: Design documents from `/specs/001-multiuser-todo/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL per specification. This implementation focuses on manual validation and functional delivery.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below follow web application structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure per plan.md (backend/src/, backend/tests/)
- [x] T002 Create frontend directory structure per plan.md (frontend/src/app/, frontend/src/components/, frontend/src/lib/)
- [x] T003 [P] Initialize Python project with requirements.txt in backend/
- [x] T004 [P] Initialize Next.js project with package.json in frontend/
- [x] T005 [P] Create backend/.env.example with BETTER_AUTH_SECRET and DATABASE_URL
- [x] T006 [P] Create frontend/.env.local.example with BETTER_AUTH_SECRET and NEXT_PUBLIC_API_URL
- [x] T007 [P] Create backend/README.md with setup instructions
- [x] T008 [P] Create frontend/README.md with setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Create backend/src/core/config.py for environment variable management
- [x] T010 Create backend/src/core/database.py with async SQLAlchemy engine and Neon PostgreSQL connection
- [x] T011 Create backend/src/core/security.py with JWT verification function using python-jose
- [x] T012 Create backend/src/api/dependencies.py with get_current_user dependency for JWT extraction
- [x] T013 Create backend/src/main.py with FastAPI app initialization and CORS configuration
- [x] T014 Create backend/src/models/__init__.py and backend/src/schemas/__init__.py
- [x] T015 Create backend/src/api/__init__.py and backend/src/api/routes/__init__.py
- [x] T016 Create database migration for tasks table using Alembic or direct SQLModel metadata
- [x] T017 [P] Create frontend/src/lib/auth.ts with Better Auth configuration (JWT plugin enabled)
- [x] T018 [P] Create frontend/src/lib/api.ts with API client that includes Authorization header
- [x] T019 [P] Create frontend/src/types/task.ts with TypeScript Task interface
- [x] T020 [P] Create frontend/src/middleware.ts for route protection (redirect unauthenticated users)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Authentication (Priority: P1) 🎯 MVP

**Goal**: Users can sign up, sign in, and access their personal todo list with session persistence

**Independent Test**: Sign up a new user, sign in, refresh page to verify session persists, attempt to access /tasks without auth to verify redirect

### Implementation for User Story 1

- [x] T021 [P] [US1] Create frontend/src/app/(auth)/signup/page.tsx with sign-up form
- [x] T022 [P] [US1] Create frontend/src/app/(auth)/signin/page.tsx with sign-in form
- [x] T023 [US1] Configure Better Auth in frontend/src/lib/auth.ts with user table and JWT settings
- [x] T024 [US1] Create frontend/src/app/(protected)/layout.tsx that checks authentication and redirects if needed
- [x] T025 [US1] Update frontend/src/middleware.ts to protect /tasks routes and redirect auth routes if already authenticated
- [x] T026 [US1] Test authentication flow: sign up, sign in, session persistence, and redirect behavior

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Task Management (Priority: P2)

**Goal**: Authenticated users can create, view, update, and delete their personal tasks

**Independent Test**: Sign in, create multiple tasks, view task details, edit tasks, delete tasks, verify persistence across sessions, verify multi-user isolation

### Implementation for User Story 2

- [x] T027 [P] [US2] Create backend/src/models/task.py with Task SQLModel (id, user_id, title, description, completed, timestamps)
- [x] T028 [P] [US2] Create backend/src/schemas/task.py with TaskCreate, TaskUpdate, and TaskResponse Pydantic schemas
- [x] T029 [US2] Create backend/src/api/routes/tasks.py with GET /api/tasks endpoint (list user's tasks)
- [x] T030 [US2] Implement POST /api/tasks endpoint in backend/src/api/routes/tasks.py (create task)
- [x] T031 [US2] Implement GET /api/tasks/{id} endpoint in backend/src/api/routes/tasks.py (get task with ownership check)
- [x] T032 [US2] Implement PUT /api/tasks/{id} endpoint in backend/src/api/routes/tasks.py (update task with ownership check)
- [x] T033 [US2] Implement DELETE /api/tasks/{id} endpoint in backend/src/api/routes/tasks.py (delete task with ownership check)
- [x] T034 [US2] Register tasks router in backend/src/main.py
- [x] T035 [P] [US2] Create frontend/src/app/(protected)/tasks/page.tsx for task list view
- [x] T036 [P] [US2] Create frontend/src/app/(protected)/tasks/[id]/page.tsx for task detail view
- [x] T037 [P] [US2] Create frontend/src/components/TaskList.tsx component
- [x] T038 [P] [US2] Create frontend/src/components/TaskItem.tsx component
- [x] T039 [P] [US2] Create frontend/src/components/TaskForm.tsx component for create/edit
- [x] T040 [US2] Implement task creation in frontend/src/app/(protected)/tasks/page.tsx using API client
- [x] T041 [US2] Implement task viewing in frontend/src/app/(protected)/tasks/[id]/page.tsx using API client
- [x] T042 [US2] Implement task editing in frontend/src/app/(protected)/tasks/[id]/page.tsx using API client
- [x] T043 [US2] Implement task deletion in frontend/src/components/TaskItem.tsx using API client
- [x] T044 [US2] Test task management: create, view, edit, delete, persistence, multi-user isolation

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Task Completion Toggle (Priority: P3)

**Goal**: Users can mark tasks as complete or incomplete with visual indication

**Independent Test**: Create tasks, toggle completion status, verify visual changes, verify persistence across page refreshes

### Implementation for User Story 3

- [x] T045 [US3] Implement PATCH /api/tasks/{id}/complete endpoint in backend/src/api/routes/tasks.py (toggle completion with ownership check)
- [x] T046 [US3] Add completion toggle UI to frontend/src/components/TaskItem.tsx (checkbox or button)
- [x] T047 [US3] Add visual styling for completed tasks in frontend/src/components/TaskItem.tsx (strikethrough, color change, etc.)
- [x] T048 [US3] Implement toggle completion API call in frontend/src/components/TaskItem.tsx using API client
- [x] T049 [US3] Test completion toggle: mark complete, mark incomplete, verify visual state, verify persistence

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T050 [P] Add error handling and user feedback for failed API requests in frontend/src/lib/api.ts
- [x] T051 [P] Add loading states to frontend components (TaskList, TaskForm, TaskItem)
- [x] T052 [P] Add input validation feedback in frontend/src/components/TaskForm.tsx
- [x] T053 [P] Improve responsive design for mobile devices in frontend components
- [x] T054 [P] Add proper error responses with HTTP status codes in all backend endpoints
- [x] T055 [P] Add request validation error messages in backend/src/api/routes/tasks.py
- [x] T056 Create frontend/src/app/page.tsx landing page with links to sign up/sign in
- [x] T057 Create frontend/src/app/layout.tsx root layout with basic styling
- [x] T058 Test all success criteria from spec.md (SC-001 through SC-010)
- [x] T059 Verify constitution compliance (security, separation of concerns, API-centric design)
- [x] T060 Run quickstart.md validation to ensure setup instructions are accurate

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Requires US1 for authentication but is independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Requires US2 for tasks to exist but is independently testable

### Within Each User Story

- Backend models before endpoints
- Backend endpoints before frontend pages
- Frontend pages before components (or in parallel if different files)
- Core implementation before polish
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each user story, tasks marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 2

```bash
# Launch backend models and schemas together:
Task: "Create backend/src/models/task.py with Task SQLModel"
Task: "Create backend/src/schemas/task.py with Pydantic schemas"

# Launch frontend components together (after pages exist):
Task: "Create frontend/src/components/TaskList.tsx component"
Task: "Create frontend/src/components/TaskItem.tsx component"
Task: "Create frontend/src/components/TaskForm.tsx component"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Authentication)
   - Developer B: User Story 2 (Task Management) - can start backend work
   - Developer C: User Story 3 (Completion Toggle) - waits for US2 backend
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are optional per specification - focus on manual validation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Count Summary

- **Phase 1 (Setup)**: 8 tasks
- **Phase 2 (Foundational)**: 12 tasks (BLOCKS all user stories)
- **Phase 3 (User Story 1 - Authentication)**: 6 tasks
- **Phase 4 (User Story 2 - Task Management)**: 18 tasks
- **Phase 5 (User Story 3 - Completion Toggle)**: 5 tasks
- **Phase 6 (Polish)**: 11 tasks

**Total**: 60 tasks

**Parallel Opportunities**: 23 tasks marked [P] can run in parallel within their phase

**MVP Scope**: Phases 1-3 (26 tasks) deliver working authentication system
