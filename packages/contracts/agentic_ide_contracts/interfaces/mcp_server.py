"""MCP Server contract."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel


class MCPResource(BaseModel):
    uri: str
    name: str
    description: str | None = None
    mime_type: str | None = None


class MCPTool(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]


@runtime_checkable
class MCPServer(Protocol):
    @property
    def name(self) -> str:
        ...

    async def list_tools(self) -> list[MCPTool]:
        ...

    async def list_resources(self) -> list[MCPResource]:
        ...

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        ...

    async def read_resource(self, uri: str) -> Any:
        ...

    async def connect(self) -> None:
        ...

    async def disconnect(self) -> None:
        ...
