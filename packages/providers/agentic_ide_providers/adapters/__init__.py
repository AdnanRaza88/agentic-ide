"""Concrete ModelProvider adapters.

All vendor-specific code is confined to this package.
"""

from agentic_ide_providers.adapters.anthropic import AnthropicAdapter
from agentic_ide_providers.adapters.mock import MockProvider
from agentic_ide_providers.adapters.openai_compatible import OpenAICompatibleAdapter

__all__ = [
    "AnthropicAdapter",
    "MockProvider",
    "OpenAICompatibleAdapter",
]
