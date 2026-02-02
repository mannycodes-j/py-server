"""
Task Models
Defines the core task-related data structures for the application.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class TaskStatus(str, Enum):
    """Possible states of a task."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStage(str, Enum):
    """Stages a task can go through during execution."""
    INITIALIZATION = "initialization"
    PROXY_SETUP = "proxy_setup"
    ACCOUNT_LOGIN = "account_login"
    DATA_FETCH = "data_fetch"
    PROCESSING = "processing"
    VALIDATION = "validation"
    FINALIZATION = "finalization"


class TaskError(BaseModel):
    """Represents an error that occurred during task execution."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    stage: TaskStage
    message: str
    details: Optional[Dict[str, Any]] = None
    recoverable: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskProgress(BaseModel):
    """Tracks the progress of a task."""
    current_stage: TaskStage = TaskStage.INITIALIZATION
    percentage: float = 0.0
    items_processed: int = 0
    items_total: int = 0
    started_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None


class TaskResources(BaseModel):
    """Resources assigned to a task."""
    proxy_ids: List[str] = []
    card_ids: List[str] = []
    email_ids: List[str] = []
    account_ids: List[str] = []


class Task(BaseModel):
    """Main task model representing a unit of work."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    progress: TaskProgress = Field(default_factory=TaskProgress)
    resources: TaskResources = Field(default_factory=TaskResources)
    errors: List[TaskError] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    name: str
    description: Optional[str] = None
    resources: Optional[TaskResources] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    resources: Optional[TaskResources] = None
    metadata: Optional[Dict[str, Any]] = None
