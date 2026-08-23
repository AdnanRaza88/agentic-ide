"""Convenience factories for well-known providers."""

from __future__ import annotations

from agentic_ide_providers.adapters.anthropic import AnthropicAdapter
from agentic_ide_providers.adapters.openai_compatible import OpenAICompatibleAdapter
from agentic_ide_providers.config import ProviderConfig
from agentic_ide_providers.registry import ProviderRegistry


def build_default_registry() -> ProviderRegistry:
    """Return a registry with standard factories pre-registered."""
    registry = ProviderRegistry()
    registry.register_factory("openai", OpenAICompatibleAdapter)
    registry.register_factory("openrouter", OpenAICompatibleAdapter)
    registry.register_factory("ollama", OpenAICompatibleAdapter)
    registry.register_factory("qwen", OpenAICompatibleAdapter)
    registry.register_factory("openai-compatible", OpenAICompatibleAdapter)
    registry.register_factory("generic", OpenAICompatibleAdapter)
    registry.register_factory("anthropic", AnthropicAdapter)
    registry.register_factory("google", OpenAICompatibleAdapter)
    return registry


def create_provider(config: ProviderConfig) -> object:
    """Create a single provider instance without a registry."""
    reg = build_default_registry()
    return reg.create_and_register(config)
