# Providers

Implementations of the `ModelProvider` and `ModelRouter` contracts.

**Architecture**

```
Application / Agent Runtime
        │
        ▼
  ModelProvider / ModelRouter   ← packages/contracts (stable)
        │
        ▼
  Provider Adapter              ← this package
        │
   ┌────┴────┬──────────┬─────────┐
OpenAI*  Anthropic   Ollama   …   Custom
```

\* OpenAI-compatible adapters also cover OpenRouter, Qwen, generic OpenAI-compatible APIs, and Google (via compatible endpoints).

## Design rules

- Application code **never** imports vendor SDKs.
- All vendor-specific HTTP / SDK usage lives inside `agentic_ide_providers.adapters`.
- Errors are normalized to `ProviderError` hierarchy.
- Timeouts and retries are configurable via `ProviderConfig` / `RetryPolicy`.
- Fallback across providers is handled by `FallbackModelRouter`.

## Supported providers

| Name                 | Adapter                    | Default base URL                                      |
|----------------------|----------------------------|-------------------------------------------------------|
| `openai`             | OpenAICompatibleAdapter    | https://api.openai.com/v1                             |
| `openrouter`         | OpenAICompatibleAdapter    | https://openrouter.ai/api/v1                          |
| `ollama`             | OpenAICompatibleAdapter    | http://localhost:11434/v1                             |
| `qwen`               | OpenAICompatibleAdapter    | https://dashscope.aliyuncs.com/compatible-mode/v1     |
| `openai-compatible`  | OpenAICompatibleAdapter    | (required in config)                                  |
| `generic`            | OpenAICompatibleAdapter    | (required in config)                                  |
| `anthropic`          | AnthropicAdapter           | https://api.anthropic.com                             |
| `google`             | OpenAICompatibleAdapter    | (configure Gemini OpenAI-compatible endpoint)         |
| custom               | any factory you register   | —                                                     |

## Quick usage

```python
from agentic_ide_providers import (
    ProviderConfig,
    build_default_registry,
    FallbackModelRouter,
)
from agentic_ide_contracts import Message, ModelRequest

registry = build_default_registry()
registry.create_and_register(
    ProviderConfig(
        name="openai",
        api_key="sk-...",
        default_model="gpt-4o-mini",
    )
)
registry.create_and_register(
    ProviderConfig(
        name="anthropic",
        api_key="sk-ant-...",
        default_model="claude-3-5-sonnet-20241022",
    )
)

router = FallbackModelRouter(registry, default_order=["openai", "anthropic"])

response = await router.complete(
    ModelRequest(
        messages=[Message(role="user", content="Hello")],
    )
)
print(response.content)
```

## Features

- **Provider registration** — `ProviderRegistry.register` / `register_factory` / `create_and_register`
- **Model registration** — `register_models_from_provider` builds a model → provider index
- **Credentials** — `ProviderConfig.api_key` (SecretStr), `extra_headers`, `base_url`
- **Connection testing** — `provider.health()`
- **Streaming** — `provider.stream(request)` yields `ModelResponse` chunks
- **Capabilities** — `list_models()`, `get_capabilities(model_id)`
- **Error normalization** — `AuthenticationError`, `RateLimitError`, `TimeoutError`, `TransientError`, …
- **Timeout handling** — per-provider `timeout_seconds`
- **Retry policy** — exponential backoff + optional jitter via `RetryPolicy`
- **Configurable fallback** — `FallbackModelRouter` with ordered candidate list

## Contract

See:

- `packages/contracts/agentic_ide_contracts/interfaces/model_provider.py`
- `packages/contracts/agentic_ide_contracts/interfaces/model_router.py`
- ADR-0002: Universal Model Provider System

## Tests

```bash
cd packages/providers
python -m venv .venv && source .venv/bin/activate
pip install -e "../contracts"
pip install -e ".[dev]"
pytest -q
```

All tests use mocked providers / httpx MockTransport — no real network calls.
