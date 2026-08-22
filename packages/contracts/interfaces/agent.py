"""Agent contract."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    name: str
    description: str = ""
    model: str | None = None
    tools: list[str] = Field(default_factory=list)
    system_prompt: str | None = None
    max_iterations: int = 25
    metadata: dict[str, Any] = Field(default_factory=dict)


@runtime_checkable
class Agent(Protocol):
    @property
    def config(self) -> AgentConfig:
        ...

    async def run(self, input: dict[str, Any], state: Any) -> Any:
        """Execute one agent turn / full loop depending on implementation."""
        ...
