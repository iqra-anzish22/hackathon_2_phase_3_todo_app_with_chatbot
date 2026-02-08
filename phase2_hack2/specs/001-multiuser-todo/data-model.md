# Data Model: Multi-User Todo Web Application

**Feature**: 001-multiuser-todo
**Date**: 2026-02-04
**Purpose**: Define data entities, relationships, and validation rules

## Overview

This document defines the data model for the multi-user Todo application. The model supports strict user isolation with each task belonging to exactly one user. User authentication is managed by Better Auth, while task data is managed by the FastAPI backend.

---

## Entity Definitions

### User

**Managed By**: Better Auth (frontend authentication system)

**Purpose**: Represents an authenticated user of the application.

**Attributes**:
- `id` (UUID/String): Unique user identifier, primary key
- `email` (String): User's email address, unique, used for authentication
- `password_hash` (String): Hashed password (managed by Better Auth)
- `created_at` (DateTime): Account creation timestamp
- `updated_at` (DateTime): Last account update timestamp

**Notes**:
- User table is managed entirely by Better Auth
- Backend references user IDs from JWT tokens
- Backend does NOT store or manage user credentials
- User ID from JWT is the source of truth for ownership

**Validation Rules**:
- Email must be valid format and unique
- Password must meet minimum strength requirements (8+ characters)
- User ID must be present in JWT for all authenticated requests

---

### Task

**Managed By**: FastAPI backend with SQLModel

**Purpose**: Represents a todo item belonging to a specific user.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique task identifier |
| `user_id` | String | Foreign Key, Not Null, Indexed | Owner's user ID (from JWT) |
| `title` | String(200) | Not Null, Length: 1-200 | Task title |
| `description` | String(2000) | Nullable, Length: 0-2000 | Optional task description |
| `completed` | Boolean | Not Null, Default: False | Completion status |
| `created_at` | DateTime | Not Null, Auto-set | Task creation timestamp |
| `updated_at` | DateTime | Not Null, Auto-update | Last modification timestamp |

**Indexes**:
- Primary index on `id`
- Index on `user_id` (for efficient user-scoped queries)
- Composite index on `(user_id, created_at)` (for sorted task lists)

**Validation Rules**:
- `title`: Required, 1-200 characters, no leading/trailing whitespace
- `description`: Optional, 0-2000 characters
- `user_id`: Must match authenticated user from JWT
- `completed`: Boolean only (true/false)
- `created_at`: Immutable after creation
- `updated_at`: Automatically updated on any modification

**Business Rules**:
1. **Ownership**: Every task MUST have exactly one owner (user_id)
2. **Isolation**: Users can ONLY access their own tasks
3. **Immutable Owner**: user_id cannot be changed after task creation
4. **Soft Delete**: Tasks are permanently deleted (no soft delete)
5. **Timestamps**: System-managed, not user-editable

---

## Relationships

### User → Task (One-to-Many)

```
User (Better Auth)
  └─ has many → Task (Backend)
```

**Relationship Type**: One-to-Many
**Foreign Key**: `Task.user_id` references `User.id`
**Cascade**: Not applicable (User managed by Better Auth)
**Enforcement**: Application-level via JWT validation

**Notes**:
- No database-level foreign key constraint (User table in different system)
- Referential integrity enforced by JWT verification
- Orphaned tasks (user deleted from Better Auth) remain in database
- Backend queries always filter by authenticated user_id from JWT

---

## SQLModel Implementation

### Task Model

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """Task entity for multi-user todo application."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user-uuid-123",
                "title": "Complete project documentation",
                "description": "Write comprehensive docs for the API",
                "completed": False,
                "created_at": "2026-02-04T10:00:00Z",
                "updated_at": "2026-02-04T10:00:00Z"
            }
        }
```

### Database Schema (SQL)

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(2000),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
```

---

## Pydantic Schemas (Request/Response)

### TaskCreate (Request)

```python
from pydantic import BaseModel, Field, validator

class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)

    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

    @validator('description')
    def description_strip(cls, v):
        return v.strip() if v else None
```

### TaskUpdate (Request)

```python
class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)

    @validator('title')
    def title_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip() if v else None

    @validator('description')
    def description_strip(cls, v):
        return v.strip() if v else None
```

### TaskResponse (Response)

```python
from datetime import datetime

class TaskResponse(BaseModel):
    """Schema for task responses."""

    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

---

## State Transitions

### Task Completion Status

```
[Created] → completed = False
    ↓
[Toggle] → completed = True
    ↓
[Toggle] → completed = False
    ↓
[Toggle] → completed = True
    ...
```

**Rules**:
- Initial state: `completed = False`
- Toggle operation flips boolean value
- No intermediate states
- State persists across sessions

---

## Data Validation Summary

| Field | Required | Min Length | Max Length | Format | Default |
|-------|----------|------------|------------|--------|---------|
| title | Yes | 1 | 200 | String, trimmed | N/A |
| description | No | 0 | 2000 | String, trimmed | null |
| completed | Yes | N/A | N/A | Boolean | false |
| user_id | Yes | N/A | N/A | String (UUID) | From JWT |
| created_at | Yes | N/A | N/A | ISO 8601 DateTime | Auto |
| updated_at | Yes | N/A | N/A | ISO 8601 DateTime | Auto |

---

## Query Patterns

### List User Tasks

```python
# Get all tasks for authenticated user, ordered by creation date
tasks = await db.execute(
    select(Task)
    .where(Task.user_id == current_user.user_id)
    .order_by(Task.created_at.desc())
)
```

### Get Single Task with Ownership Check

```python
# Get task and verify ownership
task = await db.get(Task, task_id)
if not task or task.user_id != current_user.user_id:
    raise HTTPException(status_code=404, detail="Task not found")
```

### Update Task with Ownership Check

```python
# Update task only if owned by current user
task = await db.get(Task, task_id)
if not task or task.user_id != current_user.user_id:
    raise HTTPException(status_code=404, detail="Task not found")

task.title = update_data.title or task.title
task.description = update_data.description or task.description
task.updated_at = datetime.utcnow()
await db.commit()
await db.refresh(task)
```

---

## Migration Strategy

### Initial Migration

```python
# Alembic migration: Create tasks table
def upgrade():
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_user_created', 'tasks', ['user_id', 'created_at'])

def downgrade():
    op.drop_index('idx_tasks_user_created', 'tasks')
    op.drop_index('idx_tasks_user_id', 'tasks')
    op.drop_table('tasks')
```

---

## TypeScript Types (Frontend)

```typescript
// frontend/src/types/task.ts

export interface Task {
  id: number
  user_id: string
  title: string
  description: string | null
  completed: boolean
  created_at: string // ISO 8601
  updated_at: string // ISO 8601
}

export interface TaskCreate {
  title: string
  description?: string
}

export interface TaskUpdate {
  title?: string
  description?: string
}
```

---

## Summary

**Entities**: 2 (User managed by Better Auth, Task managed by backend)
**Relationships**: 1 (User → Task, one-to-many)
**Validation Rules**: 6 field-level rules + 5 business rules
**Indexes**: 2 (user_id, user_id + created_at)
**State Transitions**: 1 (completed boolean toggle)

**Key Design Decisions**:
1. User management delegated to Better Auth (separation of concerns)
2. Task ownership enforced via JWT user_id (security first)
3. All queries filtered by authenticated user (data isolation)
4. Timestamps auto-managed (data integrity)
5. Simple boolean completion state (no complexity)
