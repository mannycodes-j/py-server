"""
Task Routes
API endpoints for task management.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..models.task import (
    Task, TaskCreate, TaskUpdate, TaskStatus, 
    TaskStage, TaskError
)
from ..services.task_manager import task_manager

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


# ============== CRUD ENDPOINTS ==============

@router.post("/", response_model=Task, status_code=201)
async def create_task(task_data: TaskCreate):
    """Create a new task."""
    return task_manager.create_task(task_data)


@router.get("/", response_model=List[Task])
async def get_all_tasks(status: Optional[TaskStatus] = Query(None)):
    """Get all tasks, optionally filtered by status."""
    return task_manager.get_all_tasks(status)


@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Get a specific task by ID."""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: str, task_data: TaskUpdate):
    """Update a task."""
    task = task_manager.update_task(task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """Delete a task."""
    if not task_manager.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


# ============== STATUS CONTROL ENDPOINTS ==============

@router.post("/{task_id}/start", response_model=Task)
async def start_task(task_id: str):
    """Start a pending or paused task."""
    task = task_manager.start_task(task_id)
    if not task:
        raise HTTPException(
            status_code=400, 
            detail="Task not found or cannot be started"
        )
    return task


@router.post("/{task_id}/pause", response_model=Task)
async def pause_task(task_id: str):
    """Pause a running task."""
    task = task_manager.pause_task(task_id)
    if not task:
        raise HTTPException(
            status_code=400, 
            detail="Task not found or cannot be paused"
        )
    return task


@router.post("/{task_id}/complete", response_model=Task)
async def complete_task(task_id: str):
    """Mark a task as completed."""
    task = task_manager.complete_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/cancel", response_model=Task)
async def cancel_task(task_id: str):
    """Cancel a task."""
    task = task_manager.cancel_task(task_id)
    if not task:
        raise HTTPException(
            status_code=400, 
            detail="Task not found or cannot be cancelled"
        )
    return task


# ============== PROGRESS ENDPOINTS ==============

@router.put("/{task_id}/progress", response_model=Task)
async def update_progress(
    task_id: str,
    stage: Optional[TaskStage] = None,
    percentage: Optional[float] = None,
    items_processed: Optional[int] = None,
    items_total: Optional[int] = None
):
    """Update task progress."""
    task = task_manager.update_progress(
        task_id, stage, percentage, items_processed, items_total
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/error", response_model=Task)
async def add_error(task_id: str, error: TaskError):
    """Add an error to a task."""
    task = task_manager.add_error(task_id, error)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ============== RESOURCE ASSIGNMENT ENDPOINTS ==============

@router.put("/{task_id}/resources", response_model=Task)
async def assign_resources(
    task_id: str,
    proxy_ids: Optional[List[str]] = None,
    card_ids: Optional[List[str]] = None,
    email_ids: Optional[List[str]] = None,
    account_ids: Optional[List[str]] = None
):
    """Assign resources to a task."""
    task = task_manager.assign_resources(
        task_id, proxy_ids, card_ids, email_ids, account_ids
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ============== STATISTICS ENDPOINT ==============

@router.get("/stats/overview")
async def get_statistics():
    """Get task statistics overview."""
    return task_manager.get_statistics()
