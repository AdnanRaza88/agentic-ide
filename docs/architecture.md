# Architecture Document

**Status**: Source of Truth  
**Last Updated**: 2026-08-22

## 1. Vision

Build a fast, modular, extensible **Agentic IDE and Software Factory** that turns natural-language problem descriptions into production-ready software artifacts.

## 2. Core Principle

> The platform must own its core architecture.

External systems (LangGraph, specific model SDKs, Docker APIs, MCP servers, etc.) are integrated **only** via adapters and stable interfaces. No external project becomes a mandatory hard dependency of the core runtime.

## 3. High-Level Architecture

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │
┌──────▼──────┐
│ Application │  (Next.js + Monaco + shadcn)
│     UI      │
└──────┬──────┘
       │ HTTP / WebSocket
┌──────▼──────┐
│     API     │  (FastAPI)
└──────┬──────┘
       │
┌──────▼──────────────────────────────────────────┐
│              Agent Runtime                       │
│  ┌─────────┐  ┌───────┐  ┌───────┐  ┌────────┐ │
│  │  Graph  │→ │ State │→ │Context│→ │Provider│ │
│  └────┬────┘  └───────┘  └───────┘  └────┬───┘ │
│       │                                   │     │
│  ┌────▼────┐  ┌───────┐  ┌────────┐  ┌───▼───┐ │
│  │  Tools  │  │Harness│  │Workspace│  │Verifier│ │
│  └─────────┘  └───────┘  └────────┘  └───────┘ │
└─────────────────────────────────────────────────┘
       │
┌──────▼──────┐
│  Execution  │  (Docker Sandbox)
│ Environment │
└─────────────┘
```

## 4. Layers & Responsibilities

| Layer | Package | Responsibility |
|-------|---------|----------------|
| Contracts | `packages/contracts` | All stable interfaces, schemas, events |
| Agent Runtime | `packages/agent-runtime` | Orchestrates graph execution, lifecycle |
| Graph | `packages/graph` | Graph definition & execution engine (replaceable) |
| State | `packages/state` | AgentState persistence & versioning |
| Providers | `packages/providers` | ModelProvider & ModelRouter implementations |
| Tools | `packages/tools` | Tool registry & execution |
| MCP | `packages/mcp` | MCP client/server adapters |
| Plugins | `packages/plugins` | Plugin loading & lifecycle |
| Hooks | `packages/hooks` | Lifecycle hooks (pre/post tool, model, etc.) |
| Harness | `packages/harness` | Agent execution harness |
| Workspace | `packages/workspace` | Project filesystem abstraction |
| Verifier | `packages/verifier` | Test, lint, type-check, security verification |
| Specs | `packages/specs` | Specification models & parsers |
| Preview | `packages/preview` | Live preview & deployment targets |
| API | `apps/api` | HTTP + WebSocket surface |
| Web | `apps/web` | User-facing IDE |

## 5. Design Decisions (Summary)

- **Modular Monolith**: Prefer clear package boundaries over microservices in the initial phase.
- **Replaceable Orchestration**: Graph engine is behind an interface so LangGraph (or any other) can be swapped.
- **Provider Abstraction**: All LLM access goes through `ModelProvider` / `ModelRouter`.
- **Docker Sandbox**: Execution happens in isolated workspaces.
- **Contract-First**: Interfaces live in `packages/contracts` and are versioned.
- **ADR-Driven Changes**: Any contract or architectural change requires an Architecture Decision Record.

## 6. Non-Goals (Current Phase)

- Implementing full agent loops
- Shipping production model routers
- Building the complete UI
- Multi-tenant SaaS features

## 7. Evolution Path

1. Stabilize contracts (this commit)
2. Implement minimal runtime + one reference graph
3. Add workspace + sandbox
4. Wire providers + tools
5. Build UI surfaces incrementally
6. Add verification & preview
7. Introduce plugins & MCP

## 8. References

- `packages/contracts/` — all interfaces
- `docs/adr/` — Architecture Decision Records
- `docs/feature-ownership.md`
- `docs/testing-strategy.md`
- `docs/integration-strategy.md`
