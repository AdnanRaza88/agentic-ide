"""AgentState contract & schema."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol, runtime_checkable
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """Canonical state object passed through the graph."""

    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    project_id: UUID | None = None
    messages: list[dict[str, Any]] = Field(default_factory=list)
    artifacts: dict[str, Any] = Field(default_factory=dict)
    tasks: list[dict[str, Any]] = Field(default_factory=list)
    current_node: str | None = None
    status: str = "running"  # running | paused | completed | failed | repaired
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1

    def bump(self) -> None:
        self.version += 1
        self.updated_at = datetime.utcnow()


@runtime_checkable
class StateStore(Protocol):
    async def get(self, state_id: UUID) -> AgentState | None:
        ...

    async def save(self, state: AgentState) -> None:
        ...

    async def list_by_session(self, session_id: UUID) -> list[AgentState]:
        ...
