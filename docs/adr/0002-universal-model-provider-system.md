# ADR-0002: Universal Model Provider System

**Date**: 2026-08-22  
**Status**: Accepted  
**Deciders**: Principal Architect  
**Tags**: architecture, contracts, providers, adapters

## Context

The platform requires a stable, vendor-agnostic way to call large language models.  
Hard-coding any single SDK (OpenAI, Anthropic, etc.) would violate the core principle of owning the architecture and would create lock-in.

We need:

- Support for multiple providers (OpenAI, Anthropic, Google, Qwen, OpenRouter, Ollama, generic OpenAI-compatible, custom)
- Registration of providers and models
- Credential configuration
- Connection / health testing
- Streaming and non-streaming completions
- Model capability discovery
- Normalized errors
- Timeout handling and retry policy
- Configurable fallback between providers

The application layer and agent runtime must never import vendor SDKs.

## Decision

1. Extend the existing `ModelProvider` contract in `packages/contracts` with:
   - `ModelCapabilities` and `ModelInfo` schemas
   - Optional `list_models()` and `get_capabilities(model_id)` methods
   - Clear error contract via documented exception hierarchy (implemented in providers package)

2. Implement all concrete adapters exclusively inside `packages/providers`.  
   Application code depends only on the `ModelProvider` / `ModelRouter` protocols.

3. Prefer pure HTTP (httpx) adapters over vendor SDKs wherever possible.  
   Vendor SDKs, if used, are confined to the adapter modules and are optional dependencies.

4. Provide a `ProviderRegistry` and a simple `FallbackModelRouter` that support:
   - Dynamic registration
   - Per-provider credentials and timeouts
   - Retry with exponential backoff
   - Ordered fallback lists

5. All new public types that form part of the stable contract live in `packages/contracts`.  
   Implementation details (retry policy objects, internal HTTP clients, etc.) stay in `packages/providers`.

## Consequences

### Positive
- True multi-provider support without architectural lock-in
- Easy to add new providers or swap implementations
- Consistent error surface and observability for the rest of the system
- Testability via mock providers

### Negative
- Slightly larger contracts surface
- Adapter maintenance cost when upstream APIs change

### Neutral
- Retry / timeout / fallback logic lives in the providers package (not in contracts)

## Alternatives Considered

1. Keep the minimal Protocol and put everything else in providers only — rejected because capability discovery and model listing are useful stable contracts for the router and agent runtime.
2. Make OpenAI the only first-class provider and treat others as secondary — rejected (violates platform ownership principle).
3. Depend on LangChain / LiteLLM as the abstraction layer — rejected (external library would become a hard architectural dependency).

## Compliance

- [x] Contracts updated (ModelProvider extended, new schemas)
- [x] ADR written
- [x] Tests for registry, adapters (mocked), router, error normalization
- [x] Providers package documented
