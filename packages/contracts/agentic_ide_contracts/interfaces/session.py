"""Session contract."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol, runtime_checkable
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Session(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: str | None = None
    project_id: UUID | None = None
    title: str = "Untitled Session"
    status: str = "active"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


@runtime_checkable
class SessionStore(Protocol):
    async def create(self, session: Session) -> Session:
        ...

    async def get(self, session_id: UUID) -> Session | None:
        ...

    async def update(self, session: Session) -> Session:
        ...

    async def list_by_user(self, user_id: str) -> list[Session]:
        ...
