"""Simple ModelRouter with ordered fallback support."""

from __future__ import annotations

import logging
from typing import AsyncIterator

from agentic_ide_contracts.interfaces.model_provider import (
    ModelProvider,
    ModelRequest,
    ModelResponse,
)
from agentic_ide_contracts.interfaces.model_router import ModelRouter
from agentic_ide_providers.errors import ProviderError
from agentic_ide_providers.registry import ProviderRegistry

logger = logging.getLogger(__name__)


class FallbackModelRouter:
    """ModelRouter that tries providers in order until one succeeds."""

    def __init__(
        self,
        registry: ProviderRegistry,
        *,
        default_order: list[str] | None = None,
    ) -> None:
        self._registry = registry
        self._default_order = list(default_order or [])

    def register(self, provider: ModelProvider) -> None:
        self._registry.register(provider)

    def list_providers(self) -> list[str]:
        return self._registry.list_providers()

    def set_fallback_order(self, order: list[str]) -> None:
        self._default_order = list(order)

    async def route(self, request: ModelRequest) -> ModelProvider:
        candidates: list[str] = []
        explicit = request.extra.get("provider")
        if isinstance(explicit, str):
            candidates.append(explicit)
        if request.model:
            owner = self._registry.provider_for_model(request.model)
            if owner and owner not in candidates:
                candidates.append(owner)
        for name in self._default_order:
            if name not in candidates:
                candidates.append(name)
        for name in self._registry.list_providers():
            if name not in candidates:
                candidates.append(name)
        if not candidates:
            raise ProviderError("No providers registered")
        last_error: Exception | None = None
        for name in candidates:
            provider = self._registry.get(name)
            if provider is None:
                continue
            try:
                if await provider.health():
                    return provider
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.debug("Health check failed for %s: %s", name, exc)
                continue
        if last_error:
            raise ProviderError(f"No healthy provider available; last error: {last_error}") from last_error
        raise ProviderError("No healthy provider available")

    async def complete(self, request: ModelRequest) -> ModelResponse:
        order = self._candidate_order(request)
        last_error: Exception | None = None
        for name in order:
            provider = self._registry.get(name)
            if provider is None:
                continue
            try:
                return await provider.complete(request)
            except ProviderError as exc:
                last_error = exc
                logger.warning("Provider %s failed: %s; trying next", name, exc)
                continue
        if last_error:
            raise last_error
        raise ProviderError("No provider could complete the request")

    async def stream(self, request: ModelRequest) -> AsyncIterator[ModelResponse]:
        order = self._candidate_order(request)
        last_error: Exception | None = None
        for name in order:
            provider = self._registry.get(name)
            if provider is None:
                continue
            try:
                async for chunk in provider.stream(request):
                    yield chunk
                return
            except ProviderError as exc:
                last_error = exc
                logger.warning("Provider %s stream failed: %s; trying next", name, exc)
                continue
        if last_error:
            raise last_error
        raise ProviderError("No provider could stream the request")

    def _candidate_order(self, request: ModelRequest) -> list[str]:
        candidates: list[str] = []
        explicit = request.extra.get("provider")
        if isinstance(explicit, str):
            candidates.append(explicit)
        if request.model:
            owner = self._registry.provider_for_model(request.model)
            if owner and owner not in candidates:
                candidates.append(owner)
        for name in self._default_order:
            if name not in candidates:
                candidates.append(name)
        for name in self._registry.list_providers():
            if name not in candidates:
                candidates.append(name)
        return candidates


def _assert_protocol() -> None:
    _: ModelRouter = FallbackModelRouter(ProviderRegistry())  # type: ignore[assignment]
