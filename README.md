# Agentic IDE & Software Factory

> Open-source, modular, extensible agentic development platform.

A user describes a real-world business/software problem in natural language.  
The system converts it into structured specifications, architecture, implementation tasks, code, tests, preview, and eventually deployment.

## Core Principle

**The platform owns its core architecture.**

External projects are integrated only through adapters, interfaces, CLI boundaries, HTTP APIs, MCP, plugins, or optional integrations.  
Never make an external project a mandatory architectural dependency unless there is a strong technical reason.

## High-Level Flow

```
User
→ Application UI
→ API
→ Agent Runtime
→ Graph
→ State
→ Context
→ Model Provider
→ Tools
→ Harness
→ Execution Environment
→ Verification
→ State Update
→ Continue / Repair / Finish
```

## Initial Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js, TypeScript, Tailwind CSS, shadcn/ui, Monaco Editor |
| Backend | Python, FastAPI, Pydantic |
| Orchestration | Graph-based (LangGraph behind adapter if useful) |
| Database | PostgreSQL |
| Realtime | WebSocket |
| Execution | Docker-based workspace/sandbox |
| Models | Provider abstraction (OpenAI, Anthropic, Google, Qwen, OpenRouter, Ollama, OpenAI-compatible, custom) |

## Repository Structure

```
/
├── apps/
│   ├── web/          # Next.js frontend
│   └── api/          # FastAPI backend
├── packages/
│   ├── contracts/    # All stable interfaces & schemas (source of truth)
│   ├── agent-runtime/
│   ├── graph/
│   ├── state/
│   ├── providers/
│   ├── tools/
│   ├── mcp/
│   ├── plugins/
│   ├── hooks/
│   ├── harness/
│   ├── workspace/
│   ├── verifier/
│   ├── specs/
│   └── preview/
├── skills/
├── docs/             # Architecture, ADRs, guides
├── tests/
└── scripts/
```

## Architectural Source of Truth

All future implementation **must** respect the contracts defined in `packages/contracts/` and the documents in `docs/`.

- Do **not** silently change contracts.
- Any contract change requires an ADR first.

See:
- [Architecture Overview](docs/architecture.md)
- [Interface Contracts](packages/contracts/)
- [ADR Template](docs/adr/0000-template.md)
- [Feature Ownership Rules](docs/feature-ownership.md)
- [Testing Strategy](docs/testing-strategy.md)
- [Integration Strategy](docs/integration-strategy.md)

## Status

This repository currently contains the **architectural foundation only**.  
Major features are intentionally not implemented yet.

## License

Apache-2.0 (to be confirmed)
