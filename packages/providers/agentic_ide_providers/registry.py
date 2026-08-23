"""Provider and model registration."""

from __future__ import annotations

import logging
from typing import Callable

from agentic_ide_contracts.interfaces.model_provider import ModelInfo, ModelProvider
from agentic_ide_providers.config import ProviderConfig

logger = logging.getLogger(__name__)

ProviderFactory = Callable[[ProviderConfig], ModelProvider]


class ProviderRegistry:
    """Central registry for ModelProvider instances and factories."""

    def __init__(self) -> None:
        self._providers: dict[str, ModelProvider] = {}
        self._factories: dict[str, ProviderFactory] = {}
        self._model_index: dict[str, str] = {}

    def register_factory(self, name: str, factory: ProviderFactory) -> None:
        self._factories[name] = factory
        logger.debug("Registered provider factory: %s", name)

    def register(self, provider: ModelProvider) -> None:
        self._providers[provider.name] = provider
        logger.info("Registered provider instance: %s", provider.name)

    def create_and_register(self, config: ProviderConfig) -> ModelProvider:
        factory = self._factories.get(config.name)
        if factory is None:
            factory = self._factories.get("openai-compatible")
        if factory is None:
            raise KeyError(
                f"No factory registered for provider '{config.name}'. "
                f"Known factories: {sorted(self._factories)}"
            )
        provider = factory(config)
        self.register(provider)
        return provider

    def get(self, name: str) -> ModelProvider | None:
        return self._providers.get(name)

    def require(self, name: str) -> ModelProvider:
        provider = self.get(name)
        if provider is None:
            raise KeyError(f"Provider '{name}' is not registered")
        return provider

    def list_providers(self) -> list[str]:
        return sorted(self._providers.keys())

    def unregister(self, name: str) -> None:
        self._providers.pop(name, None)
        self._model_index = {m: p for m, p in self._model_index.items() if p != name}

    async def register_models_from_provider(self, name: str) -> list[ModelInfo]:
        provider = self.require(name)
        models = await provider.list_models()
        for m in models:
            self._model_index[m.id] = name
        return models

    def provider_for_model(self, model_id: str) -> str | None:
        return self._model_index.get(model_id)

    def clear(self) -> None:
        self._providers.clear()
        self._model_index.clear()
