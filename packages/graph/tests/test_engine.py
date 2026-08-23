"""Unit tests for the native graph engine."""

from __future__ import annotations

import asyncio

import pytest

from agentic_ide_contracts.interfaces.agent_graph import (
    GraphRunStatus,
    RetryPolicy,
)
from agentic_ide_graph import (
    GraphBuilder,
    InMemoryCheckpointer,
    SimpleCancellationToken,
)
from agentic_ide_graph.errors import InvalidGraphError


async def _ok(state: dict) -> dict:
    return {"ok": True}


async def _plan(state: dict) -> dict:
    return {"plan": "ship it"}


async def _execute(state: dict) -> dict:
    return {"executed": True, "result": state.get("plan", "")}


async def _verify(state: dict) -> dict:
    if state.get("force_fail"):
        raise RuntimeError("verify failed")
    return {"verified": True}


async def _diagnose(state: dict) -> dict:
    return {"diagnosis": "fixed", "force_fail": False}


async def _repair(state: dict) -> dict:
    return {"repaired": True}


@pytest.mark.asyncio
async def test_successful_execution() -> None:
    graph = (
        GraphBuilder("success")
        .add_node("plan", _plan)
        .add_node("execute", _execute)
        .add_node("verify", _verify)
        .add_edge("plan", "execute")
        .add_edge("execute", "verify")
        .set_entry("plan")
        .add_end("verify")
        .compile()
    )
    result = await graph.invoke({"task": "demo"})
    assert result.status == GraphRunStatus.COMPLETED
    assert result.state["plan"] == "ship it"
    assert result.state["executed"] is True
    assert result.state["verified"] is True
    assert result.steps >= 3
