"""Agentic IDE Model Providers — adapters & registry.

Application code depends only on contracts (ModelProvider / ModelRouter).
All vendor-specific code lives behind adapters in this package.
"""

from agentic_ide_providers.adapters.mock import MockProvider
from agentic_ide_providers.adapters.openai_compatible import OpenAICompatibleAdapter
from agentic_ide_providers.adapters.anthropic import AnthropicAdapter
from agentic_ide_providers.config import ProviderConfig, RetryPolicy
from agentic_ide_providers.errors import (
    AuthenticationError,
    ProviderError,
    RateLimitError,
    TimeoutError,
    TransientError,
    UnsupportedFeatureError,
)
from agentic_ide_providers.factory import build_default_registry, create_provider
from agentic_ide_providers.registry import ProviderRegistry
from agentic_ide_providers.router import FallbackModelRouter

__version__ = "0.1.0"

__all__ = [
    "AnthropicAdapter",
    "AuthenticationError",
    "FallbackModelRouter",
    "MockProvider",
    "OpenAICompatibleAdapter",
    "ProviderConfig",
    "ProviderError",
    "ProviderRegistry",
    "RateLimitError",
    "RetryPolicy",
    "TimeoutError",
    "TransientError",
    "UnsupportedFeatureError",
    "build_default_registry",
    "create_provider",
]
