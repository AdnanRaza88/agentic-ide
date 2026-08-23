"""In-memory mock provider for unit tests."""

from __future__ import annotations

from typing import AsyncIterator

from agentic_ide_contracts.interfaces.model_provider import (
    ModelCapabilities,
    ModelCapability,
    ModelInfo,
    ModelRequest,
    ModelResponse,
)
from agentic_ide_providers.config import ProviderConfig
from agentic_ide_providers.errors import ProviderError


class MockProvider:
    """Deterministic ModelProvider for tests."""

    def __init__(
        self,
        config: ProviderConfig | None = None,
        *,
        name: str = "mock",
        responses: list[ModelResponse] | None = None,
        healthy: bool = True,
        models: list[ModelInfo] | None = None,
        fail_times: int = 0,
    ) -> None:
        self._name = name
        self._config = config or ProviderConfig(name=name)
        self._responses = list(responses or [
            ModelResponse(content="mock response", finish_reason="stop", provider=name)
        ])
        self._healthy = healthy
        self._models = models or [
            ModelInfo(
                id="mock-model",
                name="Mock Model",
                provider=name,
                capabilities=ModelCapabilities(
                    model_id="mock-model",
                    capabilities=[ModelCapability.CHAT, ModelCapability.STREAMING],
                ),
            )
        ]
        self._fail_times = fail_times
        self._call_count = 0
        self.last_request: ModelRequest | None = None

    @property
    def name(self) -> str:
        return self._name

    async def complete(self, request: ModelRequest) -> ModelResponse:
        self.last_request = request
        self._call_count += 1
        if self._call_count <= self._fail_times:
            raise ProviderError("mock failure", provider=self.name, retryable=True)
        idx = min(self._call_count - 1, len(self._responses) - 1)
        resp = self._responses[idx]
        return resp.model_copy(update={"provider": self.name, "model": request.model})

    async def stream(self, request: ModelRequest) -> AsyncIterator[ModelResponse]:
        self.last_request = request
        self._call_count += 1
        if self._call_count <= self._fail_times:
            raise ProviderError("mock stream failure", provider=self.name, retryable=True)
        full = await self.complete(request)
        yield full

    async def health(self) -> bool:
        return self._healthy

    async def list_models(self) -> list[ModelInfo]:
        return list(self._models)

    async def get_capabilities(self, model_id: str) -> ModelCapabilities | None:
        for m in self._models:
            if m.id == model_id and m.capabilities:
                return m.capabilities
        return ModelCapabilities(model_id=model_id, capabilities=[ModelCapability.CHAT])
