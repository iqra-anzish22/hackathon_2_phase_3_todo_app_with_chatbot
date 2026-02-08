"""
Task API routes.
Provides CRUD endpoints for task management with JWT authentication and ownership enforcement.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List

from ...core.database import get_db
from ...core.authorization import get_user_task_or_404
from ...core.errors import AppException, ERROR_INTERNAL_SERVER
from ...models.task import Task
from ...schemas.task import TaskCreate, TaskUpdate, TaskResponse
from ..dependencies import get_current_user


router = APIRouter()


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all tasks for the authenticated user.
    Returns tasks ordered by creation date (newest first).

    Raises:
        401: Missing or invalid authentication token
        500: Internal server error
    """
    try:
        result = await db.execute(
            select(Task)
            .where(Task.user_id == current_user)
            .order_by(Task.created_at.desc())
        )
        tasks = result.scalars().all()
        return tasks
    except AppException:
        # Re-raise AppException (auth errors)
        raise
    except Exception as e:
        # Catch any unexpected errors
        raise AppException(
            status_code=500,
            error_code=ERROR_INTERNAL_SERVER,
            message="An unexpected error occurred while fetching tasks"
        )


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new task for the authenticated user.

    Raises:
        401: Missing or invalid authentication token
        422: Validation error (invalid task data)
        500: Internal server error
    """
    try:
        task = Task(
            user_id=current_user,
            title=task_data.title,
            description=task_data.description,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(task)
        await db.commit()
        await db.refresh(task)

        return task
    except AppException:
        # Re-raise AppException (auth errors)
        raise
    except Exception as e:
        # Rollback on error
        await db.rollback()
        raise AppException(
            status_code=500,
            error_code=ERROR_INTERNAL_SERVER,
            message="An unexpected error occurred while creating the task"
        )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific task by ID.
    Verifies task ownership before returning.

    Raises:
        401: Missing or invalid authentication token
        403: Task belongs to another user
        404: Task not found
        500: Internal server error
    """
    try:
        task = await get_user_task_or_404(task_id, current_user, db)
        return task
    except AppException:
        # Re-raise AppException (auth, ownership, not found errors)
        raise
    except Exception as e:
        raise AppException(
            status_code=500,
            error_code=ERROR_INTERNAL_SERVER,
            message="An unexpected error occurred while fetching the task"
        )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing task.
    Verifies task ownership before updating.
    Note: user_id cannot be changed and is ignored if provided in request.

    Raises:
        401: Missing or invalid authentication token
        403: Task belongs to another user
        404: Task not found
        422: Validation error (invalid task data)
        500: Internal server error
    """
    try:
        task = await get_user_task_or_404(task_id, current_user, db)

        # Update fields if provided
        # Note: user_id is never updated from request data (ownership cannot be transferred)
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description

        task.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(task)

        return task
    except AppException:
        # Re-raise AppException (auth, ownership, not found errors)
        raise
    except Exception as e:
        await db.rollback()
        raise AppException(
            status_code=500,
            error_code=ERROR_INTERNAL_SERVER,
            message="An unexpected error occurred while updating the task"
        )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a task.
    Verifies task ownership before deleting.

    Raises:
        401: Missing or invalid authentication token
        403: Task belongs to another user
        404: Task not found
        500: Internal server error
    """
    try:
        task = await get_user_task_or_404(task_id, current_user, db)

        await db.delete(task)
        await db.commit()

        return None
    except AppException:
        # Re-raise AppException (auth, ownership, not found errors)
        raise
    except Exception as e:
        await db.rollback()
        raise AppException(
            status_code=500,
            error_code=ERROR_INTERNAL_SERVER,
            message="An unexpected error occurred while deleting the task"
        )


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    task_id: int,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle the completion status of a task.
    Verifies task ownership before toggling.
    Uses SELECT FOR UPDATE to prevent race conditions on concurrent toggles.

    Raises:
        401: Missing or invalid authentication token
        403: Task belongs to another user
        404: Task not found
        500: Internal server error
    """
    try:
        # Use SELECT FOR UPDATE to lock the row and prevent race conditions
        task = await get_user_task_or_404(task_id, current_user, db, for_update=True)

        # Toggle completion status
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(task)

        return task
    except AppException:
        # Re-raise AppException (auth, ownership, not found errors)
        raise
    except Exception as e:
        await db.rollback()
        raise AppException(
            status_code=500,
            error_code=ERROR_INTERNAL_SERVER,
            message="An unexpected error occurred while toggling task completion"
        )
