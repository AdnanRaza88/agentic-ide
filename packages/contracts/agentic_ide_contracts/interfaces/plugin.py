"""Plugin contract."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class PluginManifest(BaseModel):
    id: str
    name: str
    version: str
    description: str = ""
    author: str | None = None
    entrypoint: str
    permissions: list[str] = Field(default_factory=list)
    hooks: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


@runtime_checkable
class Plugin(Protocol):
    @property
    def manifest(self) -> PluginManifest:
        ...

    async def activate(self, context: dict[str, Any]) -> None:
        ...

    async def deactivate(self) -> None:
        ...
