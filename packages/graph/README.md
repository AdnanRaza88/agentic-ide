# Graph

Replaceable graph / control-flow execution engine for Agentic IDE.

The platform owns the orchestration model. External libraries (LangGraph or others)
may be integrated only behind adapters that implement the `AgentGraph` contract
from `agentic-ide-contracts`. This package provides the default native engine.

## Capabilities

- Nodes with typed handlers
- Static and conditional edges
- Shared mutable state (dict)
- Per-node and global retries with exponential backoff
- Bounded loops via `max_visits` and `max_total_steps`
- Per-node and global timeouts
- Cooperative cancellation
- Checkpoints after every successful node
- Failure transitions (`on_failure`)
- Recovery via `resume` from checkpoint
- Human approval nodes (`requires_approval` → pause)

## Quick usage

```python
from agentic_ide_graph import GraphBuilder, InMemoryCheckpointer, SimpleCancellationToken
from agentic_ide_contracts import GraphRunStatus

async def plan(state):
    return {"plan": "do the work"}

async def execute(state):
    return {"result": "ok"}

async def verify(state):
    return {"verified": True}

builder = (
    GraphBuilder("example")
    .add_node("plan", plan)
    .add_node("execute", execute)
    .add_node("verify", verify)
    .add_edge("plan", "execute")
    .add_edge("execute", "verify")
    .set_entry("plan")
    .add_end("verify")
)
graph = builder.compile()

result = await graph.invoke({"input": "task"})
assert result.status == GraphRunStatus.COMPLETED
```

## Contract

See:

- `packages/contracts/agentic_ide_contracts/interfaces/agent_graph.py`
- ADR-0003: Graph Engine

## Tests

```bash
cd packages/graph
python -m venv .venv && source .venv/bin/activate
pip install -e "../contracts"
pip install -e ".[dev]"
pytest -q
```
