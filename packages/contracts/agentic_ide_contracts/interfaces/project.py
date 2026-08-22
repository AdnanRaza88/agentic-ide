"""Project contract."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol, runtime_checkable
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Project(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str = ""
    owner_id: str | None = None
    workspace_path: str | None = None
    status: str = "active"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


@runtime_checkable
class ProjectStore(Protocol):
    async def create(self, project: Project) -> Project:
        ...

    async def get(self, project_id: UUID) -> Project | None:
        ...

    async def update(self, project: Project) -> Project:
        ...

    async def list_by_owner(self, owner_id: str) -> list[Project]:
        ...
