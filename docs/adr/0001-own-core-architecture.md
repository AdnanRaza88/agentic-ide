# ADR-0001: Own the Core Architecture

**Date**: 2026-08-22  
**Status**: Accepted  
**Deciders**: Principal Architect  
**Tags**: architecture, principle

## Context

Many agentic frameworks and AI IDEs tightly couple their runtime to specific libraries (LangGraph, particular model SDKs, specific sandbox providers). This creates lock-in and makes the system fragile when those libraries evolve or when better alternatives appear.

## Decision

The platform **owns** its core architecture. All external systems are integrated exclusively through adapters that implement stable contracts defined in `packages/contracts`.

No external project becomes a mandatory architectural dependency unless a strong technical reason is documented in a subsequent ADR.

## Consequences

### Positive
- Long-term flexibility and replaceability
- Clear boundaries for contributors
- Ability to swap orchestration engines, model providers, and sandboxes without rewriting the product

### Negative
- Slightly more boilerplate (adapters)
- Initial velocity may be lower than building directly on a single framework

### Neutral
- We can still use LangGraph, OpenAI SDK, etc., behind adapters

## Alternatives Considered

1. Build directly on LangGraph as the core runtime — rejected (lock-in)
2. Make OpenAI the only first-class provider — rejected (limits future models)
