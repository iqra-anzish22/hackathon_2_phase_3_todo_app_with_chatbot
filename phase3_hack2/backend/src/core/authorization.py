"""
Authorization utilities for ownership verification.
Provides reusable functions for checking task ownership and access control.
"""
from typing import Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.task import Task
from .errors import AppException, ERROR_TASK_NOT_FOUND, ERROR_FORBIDDEN
from .logging import logger


async def get_user_task_or_404(
    task_id: int,
    user_id: str,
    session: AsyncSession,
    for_update: bool = False
) -> Task:
    """
    Fetch a task and verify ownership.

    This function centralizes authorization logic to ensure consistent
    ownership checks across all task operations.

    Args:
        task_id: ID of the task to fetch
        user_id: ID of the authenticated user (from JWT)
        session: Database session
        for_update: If True, use SELECT FOR UPDATE to lock the row (for race condition prevention)

    Returns:
        Task: The task if it exists and belongs to the user

    Raises:
        AppException: 404 if task doesn't exist, 403 if user doesn't own the task
    """
    # Build query with optional row locking
    statement = select(Task).where(Task.id == task_id)
    if for_update:
        statement = statement.with_for_update()

    # Execute query
    result = await session.execute(statement)
    task = result.scalar_one_or_none()

    # Check if task exists
    if not task:
        raise AppException(
            status_code=404,
            error_code=ERROR_TASK_NOT_FOUND,
            message=f"Task with ID {task_id} not found"
        )

    # Check ownership
    if task.user_id != user_id:
        # Log authorization failure with user_id and resource_id (non-sensitive)
        logger.warning(
            f"User attempted to access task owned by another user",
            extra={
                "event_type": "authz_failure",
                "user_id": user_id,
                "resource_id": str(task_id)
            }
        )
        raise AppException(
            status_code=403,
            error_code=ERROR_FORBIDDEN,
            message="You don't have permission to access this task"
        )

    return task
