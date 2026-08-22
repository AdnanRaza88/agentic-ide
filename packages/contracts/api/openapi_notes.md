# API Contracts (Overview)

The HTTP + WebSocket surface lives in `apps/api` and must conform to these high-level contracts.

## REST (illustrative)

- `POST /sessions` → create Session
- `GET /sessions/{id}` → get Session
- `POST /sessions/{id}/messages` → send user message (triggers agent)
- `GET /projects` / `POST /projects`
- `GET /projects/{id}/specs`
- `POST /projects/{id}/preview`
- `GET /providers` → list available ModelProviders

## WebSocket

- `WS /ws/sessions/{id}`
  - Client → Server: user messages, control commands
  - Server → Client: Event stream (see `events/events.py`)

Exact OpenAPI schema will be generated from FastAPI once implementation begins.
All request/response models must be defined in `packages/contracts` or re-exported from there.
