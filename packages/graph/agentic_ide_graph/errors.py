"""Normalized errors for the graph engine."""

from __future__ import annotations


class GraphError(Exception):
    def __init__(self, message: str, *, node_id: str | None = None, retryable: bool = False) -> None:
        super().__init__(message)
        self.node_id = node_id
        self.retryable = retryable


class NodeExecutionError(GraphError):
    def __init__(
        self,
        message: str,
        *,
        node_id: str | None = None,
        retryable: bool = False,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message, node_id=node_id, retryable=retryable)
        self.cause = cause


class GraphTimeoutError(GraphError):
    def __init__(self, message: str = "Graph execution timed out", *, node_id: str | None = None) -> None:
        super().__init__(message, node_id=node_id, retryable=False)


class GraphCancelledError(GraphError):
    def __init__(self, message: str = "Graph execution cancelled", *, node_id: str | None = None) -> None:
        super().__init__(message, node_id=node_id, retryable=False)


class MaxStepsExceededError(GraphError):
    def __init__(
        self,
        message: str = "Maximum step count exceeded",
        *,
        node_id: str | None = None,
        steps: int = 0,
    ) -> None:
        super().__init__(message, node_id=node_id, retryable=False)
        self.steps = steps


class MaxVisitsExceededError(GraphError):
    def __init__(
        self,
        message: str = "Node visit limit exceeded",
        *,
        node_id: str | None = None,
        visits: int = 0,
    ) -> None:
        super().__init__(message, node_id=node_id, retryable=False)
        self.visits = visits


class InvalidGraphError(GraphError):
    def __init__(self, message: str) -> None:
        super().__init__(message, retryable=False)


class CheckpointError(GraphError):
    def __init__(self, message: str, *, run_id: str | None = None) -> None:
        super().__init__(message, retryable=False)
        self.run_id = run_id
