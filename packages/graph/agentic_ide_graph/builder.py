"""Fluent graph builder that produces a compileable GraphDefinition + handlers."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from agentic_ide_contracts.interfaces.agent_graph import (
    GraphDefinition,
    GraphEdge,
    GraphNode,
    NodeType,
    RetryPolicy,
)
from agentic_ide_graph.engine import CompiledGraph
from agentic_ide_graph.errors import InvalidGraphError

NodeHandler = Callable[[dict[str, Any]], Awaitable[dict[str, Any] | None]]
ConditionRouter = Callable[[dict[str, Any]], str]


class GraphBuilder:
    def __init__(self, graph_id: str) -> None:
        self._id = graph_id
        self._nodes: dict[str, GraphNode] = {}
        self._handlers: dict[str, NodeHandler] = {}
        self._edges: list[GraphEdge] = []
        self._routers: dict[str, ConditionRouter] = {}
        self._entry: str | None = None
        self._end_nodes: set[str] = set()
        self._default_retry: RetryPolicy | None = None
        self._default_timeout: float | None = None
        self._max_total_steps: int = 200
        self._metadata: dict[str, Any] = {}

    def add_node(
        self,
        node_id: str,
        handler: NodeHandler,
        *,
        type: str = NodeType.CUSTOM.value,
        config: dict[str, Any] | None = None,
        retry: RetryPolicy | None = None,
        timeout_seconds: float | None = None,
        max_visits: int | None = None,
        on_failure: str | None = None,
        requires_approval: bool = False,
    ) -> GraphBuilder:
        if node_id in self._nodes:
            raise InvalidGraphError(f"Duplicate node id: {node_id}")
        self._nodes[node_id] = GraphNode(
            id=node_id,
            type=type,
            config=config or {},
            retry=retry,
            timeout_seconds=timeout_seconds,
            max_visits=max_visits,
            on_failure=on_failure,
            requires_approval=requires_approval,
        )
        self._handlers[node_id] = handler
        return self

    def add_edge(self, source: str, target: str) -> GraphBuilder:
        self._edges.append(GraphEdge(source=source, target=target, condition=None))
        return self

    def add_conditional_edges(
        self,
        source: str,
        router: ConditionRouter,
        mapping: dict[str, str],
    ) -> GraphBuilder:
        self._routers[source] = router
        for condition, target in mapping.items():
            self._edges.append(GraphEdge(source=source, target=target, condition=condition))
        return self

    def set_entry(self, node_id: str) -> GraphBuilder:
        self._entry = node_id
        return self

    def add_end(self, node_id: str) -> GraphBuilder:
        self._end_nodes.add(node_id)
        return self

    def set_default_retry(self, policy: RetryPolicy) -> GraphBuilder:
        self._default_retry = policy
        return self

    def set_default_timeout(self, seconds: float) -> GraphBuilder:
        self._default_timeout = seconds
        return self

    def set_max_total_steps(self, steps: int) -> GraphBuilder:
        self._max_total_steps = steps
        return self

    def set_metadata(self, metadata: dict[str, Any]) -> GraphBuilder:
        self._metadata = dict(metadata)
        return self

    def build_definition(self) -> GraphDefinition:
        if not self._entry:
            raise InvalidGraphError("Entry point is required")
        if self._entry not in self._nodes:
            raise InvalidGraphError(f"Entry point '{self._entry}' is not a registered node")
        for edge in self._edges:
            if edge.source not in self._nodes:
                raise InvalidGraphError(f"Edge source '{edge.source}' is not a registered node")
            if edge.target not in self._nodes and edge.target not in self._end_nodes:
                raise InvalidGraphError(f"Edge target '{edge.target}' is not a registered node")
        for node in self._nodes.values():
            if node.on_failure and node.on_failure not in self._nodes:
                raise InvalidGraphError(
                    f"on_failure target '{node.on_failure}' for node '{node.id}' is missing"
                )
        return GraphDefinition(
            id=self._id,
            nodes=list(self._nodes.values()),
            edges=list(self._edges),
            entry_point=self._entry,
            end_nodes=list(self._end_nodes),
            metadata=self._metadata,
            default_retry=self._default_retry,
            default_timeout_seconds=self._default_timeout,
            max_total_steps=self._max_total_steps,
        )

    def compile(self) -> CompiledGraph:
        definition = self.build_definition()
        return CompiledGraph(
            definition=definition,
            handlers=dict(self._handlers),
            routers=dict(self._routers),
        )
