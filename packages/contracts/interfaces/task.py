"""Task contract."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID | None = None
    session_id: UUID | None = None
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    parent_id: UUID | None = None
    depends_on: list[UUID] = Field(default_factory=list)
    assignee: str | None = None  # agent name or "human"
    result: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
