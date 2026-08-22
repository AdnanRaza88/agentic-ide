"""ModelRouter contract.

Responsible for selecting which ModelProvider (and model) to use
for a given request based on policy, cost, capability, or user preference.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from .model_provider import ModelProvider, ModelRequest, ModelResponse


@runtime_checkable
class ModelRouter(Protocol):
    async def route(self, request: ModelRequest) -> ModelProvider:
        """Select the best provider for this request."""
        ...

    async def complete(self, request: ModelRequest) -> ModelResponse:
        """Route + complete in one call."""
        ...

    def register(self, provider: ModelProvider) -> None:
        """Register a provider instance."""
        ...

    def list_providers(self) -> list[str]:
        """Return names of registered providers."""
        ...
