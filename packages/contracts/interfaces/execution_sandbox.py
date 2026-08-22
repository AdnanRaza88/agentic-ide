"""ExecutionSandbox contract."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable
from pydantic import BaseModel, Field


class CommandResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int


class SandboxConfig(BaseModel):
    image: str = "python:3.12-slim"
    memory_mb: int = 2048
    cpu_limit: float = 1.0
    network_enabled: bool = False
    env: dict[str, str] = Field(default_factory=dict)
    timeout_seconds: int = 300


@runtime_checkable
class ExecutionSandbox(Protocol):
    async def start(self, config: SandboxConfig) -> None:
        ...

    async def exec(self, command: list[str], workdir: str | None = None) -> CommandResult:
        ...

    async def stop(self) -> None:
        ...

    async def is_running(self) -> bool:
        ...
