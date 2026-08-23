from __future__ import annotations

from uuid import uuid4

import pytest

from agentic_ide_contracts.interfaces.agent_state import AgentState
from agentic_ide_contracts.interfaces.project import Project
from agentic_ide_contracts.interfaces.session import Session
from agentic_ide_contracts.interfaces.task import Task, TaskStatus
from agentic_ide_state.exceptions import ConflictError, InvalidTransitionError, NotFoundError
from agentic_ide_state.service import StateService


@pytest.mark.asyncio
async def test_project_crud(svc: StateService) -> None:
    p = Project(name="Demo", description="d", owner_id="user-1")
    created = await svc.create_project(p)
    assert created.id == p.id
    assert created.name == "Demo"
    got = await svc.get_project(p.id)
    assert got is not None
    created.name = "Demo 2"
    updated = await svc.update_project(created, expected_version=1)
    assert updated.name == "Demo 2"
    listed = await svc.list_projects_by_owner("user-1")
    assert len(listed) == 1


@pytest.mark.asyncio
async def test_session_lifecycle_and_resume(svc: StateService) -> None:
    session = Session(title="S1", user_id="u1", status="active")
    await svc.create_session(session)
    state = AgentState(session_id=session.id, messages=[{"role": "user", "content": "hi"}])
    saved = await svc.save_state(state)
    assert saved.version == 1
    paused = await svc.update_session_status(session.id, "paused")
    assert paused.status == "paused"
    resumed_session, resumed_state = await svc.resume_session(session.id)
    assert resumed_session.status == "active"
    assert resumed_state is not None
    assert resumed_state.messages[0]["content"] == "hi"


@pytest.mark.asyncio
async def test_optimistic_concurrency(svc: StateService) -> None:
    session = Session(title="occ")
    await svc.create_session(session)
    state = AgentState(session_id=session.id)
    saved = await svc.save_state(state)
    saved.messages = [{"role": "assistant", "content": "ok"}]
    updated = await svc.save_state(saved, expected_version=saved.version)
    assert updated.version == saved.version + 1
    with pytest.raises(ConflictError):
        await svc.save_state(saved, expected_version=1)


@pytest.mark.asyncio
async def test_checkpoint_and_recovery(svc: StateService) -> None:
    session = Session(title="cp")
    await svc.create_session(session)
    state = AgentState(
        session_id=session.id,
        messages=[{"role": "user", "content": "v1"}],
        artifacts={"file": "a.py"},
    )
    await svc.save_state(state, create_checkpoint=True, checkpoint_name="before-edit")
    state.messages.append({"role": "assistant", "content": "v2"})
    state.artifacts = {"file": "b.py"}
    await svc.save_state(state)
    cps = await svc.list_checkpoints(session.id)
    assert len(cps) >= 1
    recovered = await svc.recover_from_checkpoint(session.id, cps[0]["id"])
    assert recovered.messages[0]["content"] == "v1"
    assert recovered.artifacts.get("file") == "a.py"
    assert recovered.status == "running"


@pytest.mark.asyncio
async def test_messages_tasks_usage(svc: StateService) -> None:
    session = Session(title="meta")
    await svc.create_session(session)
    await svc.append_message(session.id, role="user", content="hello")
    msgs = await svc.list_messages(session.id)
    assert len(msgs) == 1
    task = Task(session_id=session.id, title="T1", status=TaskStatus.PENDING)
    await svc.create_task(task)
    tasks = await svc.list_tasks_by_session(session.id)
    assert len(tasks) == 1
    await svc.record_model_usage(
        session.id, provider="openai", model="gpt-4o", prompt_tokens=10, completion_tokens=20
    )
    summary = await svc.get_token_usage_summary(session.id)
    assert summary["total_tokens"] == 30
    await svc.record_tool_execution(
        session.id, tool_name="read_file", arguments={"path": "x.py"}, status="success"
    )
    await svc.set_execution_metadata(session.id, "run_id", {"id": "r-1"})
    meta = await svc.get_execution_metadata(session.id)
    assert meta["run_id"]["id"] == "r-1"


@pytest.mark.asyncio
async def test_invalid_session_transition(svc: StateService) -> None:
    session = Session(title="t", status="active")
    await svc.create_session(session)
    await svc.update_session_status(session.id, "completed")
    with pytest.raises(InvalidTransitionError):
        await svc.update_session_status(session.id, "active")


@pytest.mark.asyncio
async def test_not_found(svc: StateService) -> None:
    with pytest.raises(NotFoundError):
        await svc.resume_session(uuid4())


@pytest.mark.asyncio
async def test_list_states_and_latest(svc: StateService) -> None:
    session = Session(title="multi")
    await svc.create_session(session)
    s1 = AgentState(session_id=session.id, messages=[{"n": 1}])
    await svc.save_state(s1)
    s1.messages = [{"n": 2}]
    await svc.save_state(s1)
    latest = await svc.get_latest_state(session.id)
    assert latest is not None
    assert latest.messages[0]["n"] == 2
