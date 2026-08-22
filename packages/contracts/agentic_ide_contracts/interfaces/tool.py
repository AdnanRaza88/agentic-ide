"""Tool contract."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    name: str
    type: str
    description: str = ""
    required: bool = True
    default: Any = None


class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: list[ToolParameter] = Field(default_factory=list)
    returns: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    success: bool
    output: Any = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


@runtime_checkable
class Tool(Protocol):
    @property
    def spec(self) -> ToolSpec:
        ...

    async def execute(
        self, arguments: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        ...
