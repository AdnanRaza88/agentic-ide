"""Hook contract.

Hooks allow plugins and core systems to intercept lifecycle events.
"""

from __future__ import annotations

from typing import Any, Callable, Protocol, runtime_checkable
from enum import Enum


class HookPoint(str, Enum):
    PRE_MODEL = "pre_model"
    POST_MODEL = "post_model"
    PRE_TOOL = "pre_tool"
    POST_TOOL = "post_tool"
    PRE_GRAPH = "pre_graph"
    POST_GRAPH = "post_graph"
    ON_ERROR = "on_error"
    ON_STATE_UPDATE = "on_state_update"
    ON_SESSION_START = "on_session_start"
    ON_SESSION_END = "on_session_end"


@runtime_checkable
class Hook(Protocol):
    @property
    def point(self) -> HookPoint:
        ...

    @property
    def priority(self) -> int:
        """Lower numbers run first."""
        ...

    async def __call__(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        """Return modified payload or None to continue unchanged."""
        ...
