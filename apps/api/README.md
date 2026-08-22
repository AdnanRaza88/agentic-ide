# API (`apps/api`)

FastAPI backend for Agentic IDE.

## Run locally

```bash
# from repo root
cd apps/api
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the root script:

```bash
./scripts/dev-api.sh
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Root info |
| GET | `/health` | Liveness |
| GET | `/health/ready` | Readiness |
| GET | `/docs` | OpenAPI UI |

## Tests

```bash
cd apps/api
pytest
```

## Notes

- Agent runtime, MCP, plugins, and model routing are **not** implemented in this package yet.
- CORS is configured for `http://localhost:3000` by default.
