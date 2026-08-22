"""AgentGraph contract.

The orchestration engine is replaceable. Any graph library
(LangGraph or custom) must satisfy this interface via an adapter.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable
from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    id: str
    type: str  # agent | tool | condition | human | custom
    config: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    condition: str | None = None


class GraphDefinition(BaseModel):
    id: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    entry_point: str
    metadata: dict[str, Any] = Field(default_factory=dict)


@runtime_checkable
class AgentGraph(Protocol):
    @property
    def definition(self) -> GraphDefinition:
        ...

    async def invoke(self, input: dict[str, Any], state: Any) -> Any:
        """Run the graph to completion (or until interrupt)."""
        ...

    async def stream(self, input: dict[str, Any], state: Any):
        """Yield intermediate state updates."""
        ...

    def compile(self) -> "AgentGraph":
        """Prepare the graph for execution."""
        ...
