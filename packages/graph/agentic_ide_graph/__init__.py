"""Agentic IDE Graph Engine — native control-flow runtime.

Application code depends only on contracts (AgentGraph / GraphDefinition).
Optional external engines (e.g. LangGraph) must live behind adapters that
implement the same contracts; this package is the default implementation.
"""

from agentic_ide_graph.builder import GraphBuilder
from agentic_ide_graph.cancellation import SimpleCancellationToken
from agentic_ide_graph.checkpoint import InMemoryCheckpointer
from agentic_ide_graph.engine import CompiledGraph
from agentic_ide_graph.errors import (
    CheckpointError,
    GraphCancelledError,
    GraphError,
    GraphTimeoutError,
    InvalidGraphError,
    MaxStepsExceededError,
    MaxVisitsExceededError,
    NodeExecutionError,
)

__version__ = "0.1.0"

__all__ = [
    "CheckpointError",
    "CompiledGraph",
    "GraphBuilder",
    "GraphCancelledError",
    "GraphError",
    "GraphTimeoutError",
    "InMemoryCheckpointer",
    "InvalidGraphError",
    "MaxStepsExceededError",
    "MaxVisitsExceededError",
    "NodeExecutionError",
    "SimpleCancellationToken",
]
