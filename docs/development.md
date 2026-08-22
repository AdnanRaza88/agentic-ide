# Development Guide

## Prerequisites

- Python **3.11+**
- Node.js **20+**
- npm 10+

## Quick start

```bash
# Terminal 1 — API
chmod +x scripts/*.sh
./scripts/dev-api.sh
# → http://localhost:8000  |  docs: /docs  |  health: /health

# Terminal 2 — Web
./scripts/dev-web.sh
# → http://localhost:3000
```

Open the frontend. It should show **Connected** after calling the API health endpoint.

## Package responsibilities

| Path | Responsibility |
|------|----------------|
| `apps/api` | HTTP/WS surface (FastAPI). Health only for now. |
| `apps/web` | Next.js UI. Minimal connectivity page for now. |
| `packages/contracts` | Stable interfaces & schemas (source of truth). |
| Other `packages/*` | Placeholders — implement behind contracts later. |

## Tooling

| Concern | Tool |
|---------|------|
| Python lint/format | Ruff |
| Python types | Mypy |
| Python tests | Pytest + httpx |
| JS/TS lint | ESLint (next) |
| JS/TS types | `tsc --noEmit` |
| CI | GitHub Actions (`.github/workflows/ci.yml`) |

## Environment

- Root: `.env.example`
- Web: `apps/web/.env.example` → copy to `.env.local`
- API: settings via env / `pydantic-settings` (`app/config.py`)

## What is intentionally not implemented

- Agent runtime / graph execution
- MCP
- Plugins
- Model providers & routing
- Workspace / sandbox execution
- Database persistence

Future agents must implement these **behind the existing contracts** without redesigning architecture.

## Acceptance checklist (foundation)

- [x] Frontend starts (`npm run dev`)
- [x] Backend starts (`uvicorn`)
- [x] Frontend can call backend (`GET /health`)
- [x] Tests run (`pytest`)
- [x] Lint / type checks run (ruff, mypy, eslint, tsc)
- [x] CI validates the repository
