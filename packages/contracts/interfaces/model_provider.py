"""ModelProvider contract.

All LLM access must go through this interface.
"""

from __future__ import annotations

from typing import Any, AsyncIterator, Protocol, runtime_checkable
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str  # system | user | assistant | tool
    content: str | list[dict[str, Any]]
    name: str | None = None
    tool_call_id: str | None = None


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict[str, Any]


class ModelResponse(BaseModel):
    content: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    usage: dict[str, int] = Field(default_factory=dict)
    raw: dict[str, Any] = Field(default_factory=dict)
    finish_reason: str | None = None


class ModelRequest(BaseModel):
    messages: list[Message]
    tools: list[dict[str, Any]] | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    stop: list[str] | None = None
    stream: bool = False
    extra: dict[str, Any] = Field(default_factory=dict)


@runtime_checkable
class ModelProvider(Protocol):
    """Stable contract for any model backend."""

    @property
    def name(self) -> str:
        """Unique provider identifier (e.g. 'openai', 'anthropic', 'ollama')."""
        ...

    async def complete(self, request: ModelRequest) -> ModelResponse:
        """Non-streaming completion."""
        ...

    async def stream(self, request: ModelRequest) -> AsyncIterator[ModelResponse]:
        """Streaming completion. Yields partial ModelResponse chunks."""
        ...

    async def health(self) -> bool:
        """Return True if the provider is reachable and authenticated."""
        ...
