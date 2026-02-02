"""
Task Manager Service
Handles all task-related operations and state management.
"""

from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from ..models.task import (
    Task, TaskCreate, TaskUpdate, TaskStatus, 
    TaskStage, TaskError, TaskProgress
)


class TaskManager:
    """
    Singleton service for managing tasks.
    In production, this would be backed by a database.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._tasks: Dict[str, Task] = {}
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}
        self._initialized = True
    
    # ============== CRUD OPERATIONS ==============
    
    def create_task(self, task_data: TaskCreate) -> Task:
        """Create a new task."""
        task = Task(
            name=task_data.name,
            description=task_data.description,
            resources=task_data.resources or Task.__fields__['resources'].default_factory(),
            metadata=task_data.metadata or {}
        )
        self._tasks[task.id] = task
        self._notify_subscribers(task.id, "created", task)
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        return self._tasks.get(task_id)
    
    def get_all_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """Get all tasks, optionally filtered by status."""
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)
    
    def update_task(self, task_id: str, task_data: TaskUpdate) -> Optional[Task]:
        """Update an existing task."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        update_dict = task_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(task, field, value)
        
        task.updated_at = datetime.utcnow()
        self._notify_subscribers(task_id, "updated", task)
        return task
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id in self._tasks:
            task = self._tasks.pop(task_id)
            self._notify_subscribers(task_id, "deleted", task)
            return True
        return False
    
    # ============== STATUS MANAGEMENT ==============
    
    def start_task(self, task_id: str) -> Optional[Task]:
        """Start a pending task."""
        task = self._tasks.get(task_id)
        if not task or task.status not in [TaskStatus.PENDING, TaskStatus.PAUSED]:
            return None
        
        task.status = TaskStatus.RUNNING
        task.progress.started_at = task.progress.started_at or datetime.utcnow()
        task.progress.updated_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        self._notify_subscribers(task_id, "started", task)
        return task
    
    def pause_task(self, task_id: str) -> Optional[Task]:
        """Pause a running task."""
        task = self._tasks.get(task_id)
        if not task or task.status != TaskStatus.RUNNING:
            return None
        
        task.status = TaskStatus.PAUSED
        task.progress.updated_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        self._notify_subscribers(task_id, "paused", task)
        return task
    
    def complete_task(self, task_id: str) -> Optional[Task]:
        """Mark a task as completed."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        task.status = TaskStatus.COMPLETED
        task.progress.percentage = 100.0
        task.progress.current_stage = TaskStage.FINALIZATION
        task.progress.updated_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        self._notify_subscribers(task_id, "completed", task)
        return task
    
    def fail_task(self, task_id: str, error: TaskError) -> Optional[Task]:
        """Mark a task as failed."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        task.status = TaskStatus.FAILED
        task.errors.append(error)
        task.progress.updated_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        self._notify_subscribers(task_id, "failed", task)
        return task
    
    def cancel_task(self, task_id: str) -> Optional[Task]:
        """Cancel a task."""
        task = self._tasks.get(task_id)
        if not task or task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            return None
        
        task.status = TaskStatus.CANCELLED
        task.progress.updated_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        self._notify_subscribers(task_id, "cancelled", task)
        return task
    
    # ============== PROGRESS MANAGEMENT ==============
    
    def update_progress(
        self,
        task_id: str,
        stage: Optional[TaskStage] = None,
        percentage: Optional[float] = None,
        items_processed: Optional[int] = None,
        items_total: Optional[int] = None
    ) -> Optional[Task]:
        """Update task progress."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        if stage is not None:
            task.progress.current_stage = stage
        if percentage is not None:
            task.progress.percentage = min(100.0, max(0.0, percentage))
        if items_processed is not None:
            task.progress.items_processed = items_processed
        if items_total is not None:
            task.progress.items_total = items_total
        
        task.progress.updated_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        self._notify_subscribers(task_id, "progress", task)
        return task
    
    def add_error(self, task_id: str, error: TaskError) -> Optional[Task]:
        """Add an error to a task."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        task.errors.append(error)
        task.updated_at = datetime.utcnow()
        
        self._notify_subscribers(task_id, "error", task)
        return task
    
    # ============== RESOURCE ASSIGNMENT ==============
    
    def assign_resources(
        self,
        task_id: str,
        proxy_ids: Optional[List[str]] = None,
        card_ids: Optional[List[str]] = None,
        email_ids: Optional[List[str]] = None,
        account_ids: Optional[List[str]] = None
    ) -> Optional[Task]:
        """Assign resources to a task."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        if proxy_ids is not None:
            task.resources.proxy_ids = proxy_ids
        if card_ids is not None:
            task.resources.card_ids = card_ids
        if email_ids is not None:
            task.resources.email_ids = email_ids
        if account_ids is not None:
            task.resources.account_ids = account_ids
        
        task.updated_at = datetime.utcnow()
        self._notify_subscribers(task_id, "resources_updated", task)
        return task
    
    # ============== STATISTICS ==============
    
    def get_statistics(self) -> Dict:
        """Get task statistics."""
        tasks = list(self._tasks.values())
        return {
            "total": len(tasks),
            "pending": len([t for t in tasks if t.status == TaskStatus.PENDING]),
            "running": len([t for t in tasks if t.status == TaskStatus.RUNNING]),
            "paused": len([t for t in tasks if t.status == TaskStatus.PAUSED]),
            "completed": len([t for t in tasks if t.status == TaskStatus.COMPLETED]),
            "failed": len([t for t in tasks if t.status == TaskStatus.FAILED]),
            "cancelled": len([t for t in tasks if t.status == TaskStatus.CANCELLED]),
            "total_errors": sum(len(t.errors) for t in tasks)
        }
    
    # ============== REAL-TIME SUBSCRIPTIONS ==============
    
    async def subscribe(self, task_id: str = "*") -> asyncio.Queue:
        """Subscribe to task updates. Use '*' for all tasks."""
        queue = asyncio.Queue()
        if task_id not in self._subscribers:
            self._subscribers[task_id] = []
        self._subscribers[task_id].append(queue)
        return queue
    
    def unsubscribe(self, task_id: str, queue: asyncio.Queue):
        """Unsubscribe from task updates."""
        if task_id in self._subscribers:
            try:
                self._subscribers[task_id].remove(queue)
            except ValueError:
                pass
    
    def _notify_subscribers(self, task_id: str, event: str, task: Task):
        """Notify all subscribers of a task event."""
        message = {"event": event, "task_id": task_id, "task": task.dict()}
        
        # Notify specific task subscribers
        for queue in self._subscribers.get(task_id, []):
            queue.put_nowait(message)
        
        # Notify global subscribers
        for queue in self._subscribers.get("*", []):
            queue.put_nowait(message)


# Global instance
task_manager = TaskManager()
