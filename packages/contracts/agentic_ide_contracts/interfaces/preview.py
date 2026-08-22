"""Preview & DeploymentTarget contracts."""

from __future__ import annotations

from enum import Enum
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class PreviewStatus(str, Enum):
    STARTING = "starting"
    READY = "ready"
    FAILED = "failed"
    STOPPED = "stopped"


class Preview(BaseModel):
    id: str
    url: str | None = None
    status: PreviewStatus = PreviewStatus.STARTING
    logs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DeploymentTarget(BaseModel):
    id: str
    name: str
    type: str  # local | docker | vercel | fly | custom
    config: dict[str, Any] = Field(default_factory=dict)


@runtime_checkable
class PreviewService(Protocol):
    async def start(self, workspace: Any, target: DeploymentTarget) -> Preview:
        ...

    async def stop(self, preview_id: str) -> None:
        ...

    async def status(self, preview_id: str) -> Preview:
        ...
