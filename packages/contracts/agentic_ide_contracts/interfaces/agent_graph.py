"""AgentGraph contract.

The orchestration engine is replaceable. Any graph library
(LangGraph or custom) must satisfy this interface via an adapter.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, AsyncIterator, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    AGENT = "agent"
    TOOL = "tool"
    CONDITION = "condition"
    HUMAN = "human"
    CUSTOM = "custom"
    START = "start"
    END = "end"


class GraphRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


class RetryPolicy(BaseModel):
    max_attempts: int = 3
    initial_delay_seconds: float = 0.5
    max_delay_seconds: float = 30.0
    backoff_factor: float = 2.0
    jitter: bool = True


class GraphNode(BaseModel):
    id: str
    type: str = NodeType.CUSTOM.value
    config: dict[str, Any] = Field(default_factory=dict)
    retry: RetryPolicy | None = None
    timeout_seconds: float | None = None
    max_visits: int | None = None
    on_failure: str | None = None
    requires_approval: bool = False


class GraphEdge(BaseModel):
    source: str
    target: str
    condition: str | None = None


class GraphDefinition(BaseModel):
    id: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    entry_point: str
    end_nodes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    default_retry: RetryPolicy | None = None
    default_timeout_seconds: float | None = None
    max_total_steps: int = 200


class GraphCheckpoint(BaseModel):
    run_id: str
    graph_id: str
    node_id: str
    state: dict[str, Any]
    step: int
    status: GraphRunStatus = GraphRunStatus.RUNNING
    metadata: dict[str, Any] = Field(default_factory=dict)
    version: int = 1


class GraphRunResult(BaseModel):
    run_id: str
    status: GraphRunStatus
    state: dict[str, Any]
    current_node: str | None = None
    steps: int = 0
    error: str | None = None
    checkpoint: GraphCheckpoint | None = None


class GraphEvent(BaseModel):
    type: str
    node_id: str | None = None
    state: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    step: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


@runtime_checkable
class Checkpointer(Protocol):
    async def save(self, checkpoint: GraphCheckpoint) -> None:
        ...

    async def load(self, run_id: str) -> GraphCheckpoint | None:
        ...

    async def list_for_graph(self, graph_id: str) -> list[GraphCheckpoint]:
        ...


@runtime_checkable
class CancellationToken(Protocol):
    def is_cancelled(self) -> bool:
        ...

    def cancel(self) -> None:
        ...


@runtime_checkable
class AgentGraph(Protocol):
    @property
    def definition(self) -> GraphDefinition:
        ...

    async def invoke(
        self,
        input: dict[str, Any],
        *,
        state: dict[str, Any] | None = None,
        run_id: str | None = None,
        timeout_seconds: float | None = None,
        cancellation: CancellationToken | None = None,
        checkpointer: Checkpointer | None = None,
    ) -> GraphRunResult:
        ...

    async def stream(
        self,
        input: dict[str, Any],
        *,
        state: dict[str, Any] | None = None,
        run_id: str | None = None,
        timeout_seconds: float | None = None,
        cancellation: CancellationToken | None = None,
        checkpointer: Checkpointer | None = None,
    ) -> AsyncIterator[GraphEvent]:
        ...

    async def resume(
        self,
        checkpoint: GraphCheckpoint,
        *,
        updates: dict[str, Any] | None = None,
        timeout_seconds: float | None = None,
        cancellation: CancellationToken | None = None,
        checkpointer: Checkpointer | None = None,
    ) -> GraphRunResult:
        ...

    def compile(self) -> AgentGraph:
        ...
