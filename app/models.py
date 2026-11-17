from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkflowStatus(str, Enum):
    draft = "draft"
    active = "active"
    archived = "archived"

class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = False

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = False

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool | None = None

class Workflow(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    status: WorkflowStatus = WorkflowStatus.draft
    tasks: list[Task] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

class WorkflowCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    status: WorkflowStatus = WorkflowStatus.draft

class WorkflowUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    status: WorkflowStatus | None = None
