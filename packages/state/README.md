# packages/state

Persistent state and session subsystem for Agentic IDE.

Independent of LLM providers and graph frameworks.

## Capabilities

- Projects, sessions, versioned AgentState
- Checkpoints with recovery
- Messages, tasks
- Model usage and tool execution records
- Execution metadata
- Session resume and optimistic concurrency
- PostgreSQL production target; SQLite for tests

## Usage

```python
from agentic_ide_state import StateService, create_engine, create_session_factory, init_db

engine = create_engine("postgresql+asyncpg://...")
await init_db(engine)
svc = StateService(create_session_factory(engine))
```

## Tests

```bash
cd packages/state
pip install -e ".[dev]" -e ../contracts
pytest -q
```
