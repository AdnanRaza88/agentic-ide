# ADR-0003: Graph / Control-Flow Engine

**Date**: 2026-08-23  
**Status**: Accepted  
**Deciders**: Principal Architect  
**Tags**: architecture, orchestration, graph

## Context

Agent workflows require ordered steps, conditional branching, retries, bounded loops,
timeouts, cancellation, checkpoints, failure recovery, and human approval gates.
Many frameworks couple these concerns to a single library (e.g. LangGraph).

## Decision

The platform owns a stable graph contract (`AgentGraph`, `GraphDefinition`,
`GraphNode`, `GraphEdge`, `Checkpointer`, `CancellationToken`, `GraphRunResult`)
in `packages/contracts`.

A native implementation lives in `packages/graph` (`agentic_ide_graph`).
Any external engine may be used only behind an adapter that implements the same
contracts. Application and runtime code must depend on the contracts, never on
a vendor graph library directly.

## Consequences

### Positive
- Full control over control-flow semantics
- Replaceable orchestration engine
- Predictable testing surface without vendor runtime

### Negative
- We maintain the engine ourselves
- Feature parity with specialised libraries requires ongoing work

### Neutral
- LangGraph (or others) can still be adopted later via an adapter package

## Implementation notes

- Default engine: pure asyncio, no external graph dependency
- Handlers are async callables registered by node id
- Conditional edges use pure Python routers
- Checkpoints are optional and injected via `Checkpointer`
- Human approval is modelled as `requires_approval` → `PAUSED` + resume
