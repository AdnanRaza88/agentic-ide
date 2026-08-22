# Contracts Package

**This is the single source of truth for all stable interfaces.**

Every future feature and package **must** respect these contracts.

Changing any public contract requires an ADR first.

## Contents

- `interfaces/` — Python Protocol / ABC definitions (and TypeScript equivalents later)
- `schemas/` — Pydantic models for State, Specs, Events, API payloads
- `events/` — Event contracts
- `api/` — HTTP & WebSocket API contracts
