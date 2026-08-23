# ADR-0004: Persistent State and Session Subsystem

**Date**: 2026-08-23
**Status**: Accepted
**Tags**: state, persistence, sessions, postgresql

## Context

Agent runs must be durable, resumable, and recoverable. State must survive process restarts and support checkpoints. The subsystem must stay independent of any LLM provider or graph framework.

## Decision

Implement packages/state (agentic_ide_state) with:

1. PostgreSQL (SQLAlchemy 2 async) as production store; SQLite for tests
2. Tables for projects, sessions, versioned agent states, checkpoints, messages, tasks, model usage, tool executions, execution metadata
3. StateService facade plus contracts protocols
4. Optimistic concurrency via version column
5. Session resume and checkpoint recovery
6. Explicit status transition rules
7. Zero imports from providers or graph packages

## Consequences

Positive: clear ownership, resumable runs, observable usage.
Negative: PostgreSQL operational dependency; Alembic recommended for production migrations.
