"""In-memory and protocol checkpointer implementations."""

from __future__ import annotations

from agentic_ide_contracts.interfaces.agent_graph import GraphCheckpoint


class InMemoryCheckpointer:
    def __init__(self) -> None:
        self._store: dict[str, GraphCheckpoint] = {}
        self._by_graph: dict[str, list[str]] = {}

    async def save(self, checkpoint: GraphCheckpoint) -> None:
        self._store[checkpoint.run_id] = checkpoint
        ids = self._by_graph.setdefault(checkpoint.graph_id, [])
        if checkpoint.run_id not in ids:
            ids.append(checkpoint.run_id)

    async def load(self, run_id: str) -> GraphCheckpoint | None:
        return self._store.get(run_id)

    async def list_for_graph(self, graph_id: str) -> list[GraphCheckpoint]:
        return [self._store[rid] for rid in self._by_graph.get(graph_id, []) if rid in self._store]
