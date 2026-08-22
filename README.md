# Agentic IDE & Software Factory

> Open-source, modular, extensible agentic development platform.

A user describes a real-world business/software problem in natural language.  
The system converts it into structured specifications, architecture, implementation tasks, code, tests, preview, and eventually deployment.

## Core Principle

**The platform owns its core architecture.**

External projects are integrated only through adapters, interfaces, CLI boundaries, HTTP APIs, MCP, plugins, or optional integrations.  
Never make an external project a mandatory architectural dependency unless there is a strong technical reason.

## Status: Foundation Infrastructure

This phase delivers **repository + developer infrastructure only**:

- Monorepo layout
- FastAPI backend with health endpoints
- Next.js frontend that calls the backend
- Shared contracts package
- Lint, format, typecheck, tests, CI
- Dev scripts & documentation

**Not implemented yet** (by design): agent runtime, MCP, plugins, model routing, sandbox, etc.

## Quick start

```bash
# API (port 8000)
chmod +x scripts/*.sh
./scripts/dev-api.sh

# Web (port 3000) — new terminal
./scripts/dev-web.sh
```

Open http://localhost:3000 — you should see **Connected** when the API is up.

Full guide: [docs/development.md](docs/development.md)

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI, Pydantic |
| Contracts | Pydantic models + Protocol interfaces |
| Lint/Format | Ruff (Python), ESLint (TS) |
| Types | Mypy, TypeScript |
| Tests | Pytest, tsc |
| CI | GitHub Actions |

## Repository structure

```
/
├── apps/
│   ├── web/          # Next.js frontend
│   └── api/          # FastAPI backend
├── packages/
│   ├── contracts/    # Stable interfaces (source of truth)
│   └── …             # Placeholders for future packages
├── scripts/          # dev-api, dev-web, test, lint
├── docs/             # Architecture, ADRs, development guide
└── .github/workflows/ci.yml
```

## Architectural source of truth

All future implementation **must** respect contracts in `packages/contracts/` and docs under `docs/`.

- Do **not** silently change contracts.
- Any contract change requires an ADR first.

See:
- [Architecture](docs/architecture.md)
- [Development](docs/development.md)
- [Feature ownership](docs/feature-ownership.md)
- [Testing strategy](docs/testing-strategy.md)
- [Integration strategy](docs/integration-strategy.md)

## License

Apache-2.0
