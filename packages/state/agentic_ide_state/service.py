from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agentic_ide_contracts.interfaces.agent_state import AgentState
from agentic_ide_contracts.interfaces.project import Project
from agentic_ide_contracts.interfaces.session import Session
from agentic_ide_contracts.interfaces.task import Task, TaskStatus
from agentic_ide_state.exceptions import ConflictError, InvalidTransitionError, NotFoundError
from agentic_ide_state.models import (
    AgentStateRow,
    CheckpointRow,
    ExecutionMetadataRow,
    MessageRow,
    ModelUsageRow,
    ProjectRow,
    SessionRow,
    TaskRow,
    ToolExecutionRow,
)

_SESSION_TRANSITIONS: dict[str, set[str]] = {
    "active": {"paused", "completed", "failed", "archived"},
    "paused": {"active", "completed", "failed", "archived"},
    "completed": {"archived"},
    "failed": {"active", "archived"},
    "archived": set(),
}

_STATE_TRANSITIONS: dict[str, set[str]] = {
    "running": {"paused", "completed", "failed", "repaired"},
    "paused": {"running", "completed", "failed"},
    "failed": {"running", "repaired"},
    "repaired": {"running", "completed", "failed"},
    "completed": set(),
}


def _now() -> datetime:
    return datetime.now(UTC)


class StateService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    async def create_project(self, project: Project) -> Project:
        async with self._sf() as db:
            row = ProjectRow(
                id=project.id,
                name=project.name,
                description=project.description,
                owner_id=project.owner_id,
                workspace_path=project.workspace_path,
                status=project.status,
                metadata_=project.metadata,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
            db.add(row)
            await db.commit()
            await db.refresh(row)
            return self._to_project(row)

    async def get_project(self, project_id: UUID) -> Project | None:
        async with self._sf() as db:
            row = await db.get(ProjectRow, project_id)
            return self._to_project(row) if row else None

    async def update_project(
        self, project: Project, *, expected_version: int | None = None
    ) -> Project:
        async with self._sf() as db:
            row = await db.get(ProjectRow, project.id)
            if row is None:
                raise NotFoundError("Project", project.id)
            if expected_version is not None and row.version != expected_version:
                raise ConflictError("Project", project.id, expected_version)
            row.name = project.name
            row.description = project.description
            row.owner_id = project.owner_id
            row.workspace_path = project.workspace_path
            row.status = project.status
            row.metadata_ = project.metadata
            row.updated_at = _now()
            row.version += 1
            await db.commit()
            await db.refresh(row)
            return self._to_project(row)

    async def list_projects_by_owner(self, owner_id: str) -> list[Project]:
        async with self._sf() as db:
            result = await db.execute(
                select(ProjectRow)
                .where(ProjectRow.owner_id == owner_id)
                .order_by(ProjectRow.created_at.desc())
            )
            return [self._to_project(r) for r in result.scalars().all()]

    async def create_session(self, session: Session) -> Session:
        async with self._sf() as db:
            row = SessionRow(
                id=session.id,
                user_id=session.user_id,
                project_id=session.project_id,
                title=session.title,
                status=session.status,
                metadata_=session.metadata,
                created_at=session.created_at,
                updated_at=session.updated_at,
            )
            db.add(row)
            await db.commit()
            await db.refresh(row)
            return self._to_session(row)

    async def get_session(self, session_id: UUID) -> Session | None:
        async with self._sf() as db:
            row = await db.get(SessionRow, session_id)
            return self._to_session(row) if row else None

    async def update_session_status(
        self, session_id: UUID, new_status: str, *, expected_version: int | None = None
    ) -> Session:
        async with self._sf() as db:
            row = await db.get(SessionRow, session_id)
            if row is None:
                raise NotFoundError("Session", session_id)
            if expected_version is not None and row.version != expected_version:
                raise ConflictError("Session", session_id, expected_version)
            allowed = _SESSION_TRANSITIONS.get(row.status, set())
            if new_status not in allowed:
                raise InvalidTransitionError("Session", row.status, new_status)
            row.status = new_status
            row.updated_at = _now()
            row.version += 1
            await db.commit()
            await db.refresh(row)
            return self._to_session(row)

    async def update_session(
        self, session: Session, *, expected_version: int | None = None
    ) -> Session:
        async with self._sf() as db:
            row = await db.get(SessionRow, session.id)
            if row is None:
                raise NotFoundError("Session", session.id)
            if expected_version is not None and row.version != expected_version:
                raise ConflictError("Session", session.id, expected_version)
            if session.status != row.status:
                allowed = _SESSION_TRANSITIONS.get(row.status, set())
                if session.status not in allowed:
                    raise InvalidTransitionError("Session", row.status, session.status)
            row.title = session.title
            row.status = session.status
            row.metadata_ = session.metadata
            row.user_id = session.user_id
            row.project_id = session.project_id
            row.updated_at = _now()
            row.version += 1
            await db.commit()
            await db.refresh(row)
            return self._to_session(row)

    async def list_sessions_by_user(self, user_id: str) -> list[Session]:
        async with self._sf() as db:
            result = await db.execute(
                select(SessionRow)
                .where(SessionRow.user_id == user_id)
                .order_by(SessionRow.updated_at.desc())
            )
            return [self._to_session(r) for r in result.scalars().all()]

    async def list_sessions_by_project(self, project_id: UUID) -> list[Session]:
        async with self._sf() as db:
            result = await db.execute(
                select(SessionRow)
                .where(SessionRow.project_id == project_id)
                .order_by(SessionRow.updated_at.desc())
            )
            return [self._to_session(r) for r in result.scalars().all()]

    async def save_state(
        self,
        state: AgentState,
        *,
        expected_version: int | None = None,
        create_checkpoint: bool = False,
        checkpoint_name: str | None = None,
        checkpoint_reason: str = "auto",
    ) -> AgentState:
        async with self._sf() as db:
            session_row = await db.get(SessionRow, state.session_id)
            if session_row is None:
                raise NotFoundError("Session", state.session_id)
            existing = await db.get(AgentStateRow, state.id)
            if existing is None:
                row = AgentStateRow(
                    id=state.id,
                    session_id=state.session_id,
                    project_id=state.project_id,
                    messages=state.messages,
                    artifacts=state.artifacts,
                    tasks=state.tasks,
                    current_node=state.current_node,
                    status=state.status,
                    error=state.error,
                    metadata_=state.metadata,
                    created_at=state.created_at,
                    updated_at=_now(),
                    version=state.version,
                )
                db.add(row)
            else:
                if expected_version is not None and existing.version != expected_version:
                    raise ConflictError("AgentState", state.id, expected_version)
                if state.status != existing.status:
                    allowed = _STATE_TRANSITIONS.get(existing.status, set())
                    if state.status not in allowed:
                        raise InvalidTransitionError(
                            "AgentState", existing.status, state.status
                        )
                existing.messages = state.messages
                existing.artifacts = state.artifacts
                existing.tasks = state.tasks
                existing.current_node = state.current_node
                existing.status = state.status
                existing.error = state.error
                existing.metadata_ = state.metadata
                existing.project_id = state.project_id
                existing.updated_at = _now()
                existing.version += 1
                row = existing
            session_row.latest_state_id = row.id
            session_row.updated_at = _now()
            session_row.version += 1
            if create_checkpoint:
                db.add(
                    CheckpointRow(
                        id=uuid4(),
                        session_id=state.session_id,
                        agent_state_id=row.id,
                        name=checkpoint_name,
                        snapshot=self._state_to_dict(row),
                        reason=checkpoint_reason,
                    )
                )
            await db.commit()
            await db.refresh(row)
            return self._to_agent_state(row)

    async def get_state(self, state_id: UUID) -> AgentState | None:
        async with self._sf() as db:
            row = await db.get(AgentStateRow, state_id)
            return self._to_agent_state(row) if row else None

    async def list_states_by_session(self, session_id: UUID) -> list[AgentState]:
        async with self._sf() as db:
            result = await db.execute(
                select(AgentStateRow)
                .where(AgentStateRow.session_id == session_id)
                .order_by(AgentStateRow.version.asc())
            )
            return [self._to_agent_state(r) for r in result.scalars().all()]

    async def get_latest_state(self, session_id: UUID) -> AgentState | None:
        async with self._sf() as db:
            session_row = await db.get(SessionRow, session_id)
            if session_row is None:
                raise NotFoundError("Session", session_id)
            if session_row.latest_state_id is None:
                result = await db.execute(
                    select(AgentStateRow)
                    .where(AgentStateRow.session_id == session_id)
                    .order_by(AgentStateRow.version.desc())
                    .limit(1)
                )
                row = result.scalar_one_or_none()
                return self._to_agent_state(row) if row else None
            row = await db.get(AgentStateRow, session_row.latest_state_id)
            return self._to_agent_state(row) if row else None

    async def resume_session(self, session_id: UUID) -> tuple[Session, AgentState | None]:
        async with self._sf() as db:
            session_row = await db.get(SessionRow, session_id)
            if session_row is None:
                raise NotFoundError("Session", session_id)
            if session_row.status in ("paused", "failed"):
                session_row.status = "active"
                session_row.updated_at = _now()
                session_row.version += 1
                await db.commit()
                await db.refresh(session_row)
            state: AgentState | None = None
            if session_row.latest_state_id:
                state_row = await db.get(AgentStateRow, session_row.latest_state_id)
                if state_row:
                    state = self._to_agent_state(state_row)
            else:
                result = await db.execute(
                    select(AgentStateRow)
                    .where(AgentStateRow.session_id == session_id)
                    .order_by(AgentStateRow.version.desc())
                    .limit(1)
                )
                state_row = result.scalar_one_or_none()
                if state_row:
                    state = self._to_agent_state(state_row)
            return self._to_session(session_row), state

    async def recover_from_checkpoint(
        self, session_id: UUID, checkpoint_id: UUID
    ) -> AgentState:
        async with self._sf() as db:
            session_row = await db.get(SessionRow, session_id)
            if session_row is None:
                raise NotFoundError("Session", session_id)
            cp = await db.get(CheckpointRow, checkpoint_id)
            if cp is None or cp.session_id != session_id:
                raise NotFoundError("Checkpoint", checkpoint_id)
            snap = cp.snapshot
            new_id = uuid4()
            result = await db.execute(
                select(AgentStateRow)
                .where(AgentStateRow.session_id == session_id)
                .order_by(AgentStateRow.version.desc())
                .limit(1)
            )
            latest = result.scalar_one_or_none()
            next_version = (latest.version + 1) if latest else 1
            project_id = UUID(str(snap["project_id"])) if snap.get("project_id") else None
            row = AgentStateRow(
                id=new_id,
                session_id=session_id,
                project_id=project_id,
                messages=snap.get("messages", []),
                artifacts=snap.get("artifacts", {}),
                tasks=snap.get("tasks", []),
                current_node=snap.get("current_node"),
                status="running",
                error=None,
                metadata_={**(snap.get("metadata") or {}), "recovered_from": str(checkpoint_id)},
                created_at=_now(),
                updated_at=_now(),
                version=next_version,
            )
            db.add(row)
            session_row.latest_state_id = new_id
            session_row.status = "active"
            session_row.updated_at = _now()
            session_row.version += 1
            await db.commit()
            await db.refresh(row)
            return self._to_agent_state(row)

    async def create_checkpoint(
        self,
        session_id: UUID,
        *,
        name: str | None = None,
        reason: str = "manual",
        state_id: UUID | None = None,
    ) -> UUID:
        async with self._sf() as db:
            if state_id is None:
                session_row = await db.get(SessionRow, session_id)
                if session_row is None:
                    raise NotFoundError("Session", session_id)
                state_id = session_row.latest_state_id
            if state_id is None:
                raise NotFoundError("AgentState", "latest")
            state_row = await db.get(AgentStateRow, state_id)
            if state_row is None or state_row.session_id != session_id:
                raise NotFoundError("AgentState", state_id)
            cp_id = uuid4()
            db.add(
                CheckpointRow(
                    id=cp_id,
                    session_id=session_id,
                    agent_state_id=state_id,
                    name=name,
                    snapshot=self._state_to_dict(state_row),
                    reason=reason,
                )
            )
            await db.commit()
            return cp_id

    async def list_checkpoints(self, session_id: UUID) -> list[dict[str, Any]]:
        async with self._sf() as db:
            result = await db.execute(
                select(CheckpointRow)
                .where(CheckpointRow.session_id == session_id)
                .order_by(CheckpointRow.created_at.desc())
            )
            return [
                {
                    "id": r.id,
                    "name": r.name,
                    "reason": r.reason,
                    "agent_state_id": r.agent_state_id,
                    "created_at": r.created_at,
                    "metadata": r.metadata_,
                }
                for r in result.scalars().all()
            ]

    async def append_message(
        self,
        session_id: UUID,
        *,
        role: str,
        content: str | None = None,
        name: str | None = None,
        tool_call_id: str | None = None,
        tool_calls: list[Any] | None = None,
        agent_state_id: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> UUID:
        async with self._sf() as db:
            session_row = await db.get(SessionRow, session_id)
            if session_row is None:
                raise NotFoundError("Session", session_id)
            msg_id = uuid4()
            db.add(
                MessageRow(
                    id=msg_id,
                    session_id=session_id,
                    agent_state_id=agent_state_id,
                    role=role,
                    content=content,
                    name=name,
                    tool_call_id=tool_call_id,
                    tool_calls=tool_calls,
                    metadata_=metadata or {},
                )
            )
            session_row.updated_at = _now()
            await db.commit()
            return msg_id

    async def list_messages(
        self, session_id: UUID, *, limit: int = 200, offset: int = 0
    ) -> list[dict[str, Any]]:
        async with self._sf() as db:
            result = await db.execute(
                select(MessageRow)
                .where(MessageRow.session_id == session_id)
                .order_by(MessageRow.created_at.asc())
                .offset(offset)
                .limit(limit)
            )
            return [
                {
                    "id": r.id,
                    "role": r.role,
                    "content": r.content,
                    "name": r.name,
                    "tool_call_id": r.tool_call_id,
                    "tool_calls": r.tool_calls,
                    "metadata": r.metadata_,
                    "created_at": r.created_at,
                    "agent_state_id": r.agent_state_id,
                }
                for r in result.scalars().all()
            ]

    async def create_task(self, task: Task) -> Task:
        async with self._sf() as db:
            status_val = (
                task.status.value if isinstance(task.status, TaskStatus) else str(task.status)
            )
            row = TaskRow(
                id=task.id,
                project_id=task.project_id,
                session_id=task.session_id,
                title=task.title,
                description=task.description,
                status=status_val,
                parent_id=task.parent_id,
                depends_on=[str(u) for u in task.depends_on],
                assignee=task.assignee,
                result=task.result,
                metadata_=task.metadata,
                created_at=task.created_at,
                updated_at=task.updated_at,
            )
            db.add(row)
            await db.commit()
            await db.refresh(row)
            return self._to_task(row)

    async def get_task(self, task_id: UUID) -> Task | None:
        async with self._sf() as db:
            row = await db.get(TaskRow, task_id)
            return self._to_task(row) if row else None

    async def update_task(self, task: Task, *, expected_version: int | None = None) -> Task:
        async with self._sf() as db:
            row = await db.get(TaskRow, task.id)
            if row is None:
                raise NotFoundError("Task", task.id)
            if expected_version is not None and row.version != expected_version:
                raise ConflictError("Task", task.id, expected_version)
            row.title = task.title
            row.description = task.description
            row.status = (
                task.status.value if isinstance(task.status, TaskStatus) else str(task.status)
            )
            row.parent_id = task.parent_id
            row.depends_on = [str(u) for u in task.depends_on]
            row.assignee = task.assignee
            row.result = task.result
            row.metadata_ = task.metadata
            row.updated_at = _now()
            row.version += 1
            await db.commit()
            await db.refresh(row)
            return self._to_task(row)

    async def list_tasks_by_session(self, session_id: UUID) -> list[Task]:
        async with self._sf() as db:
            result = await db.execute(
                select(TaskRow)
                .where(TaskRow.session_id == session_id)
                .order_by(TaskRow.created_at.asc())
            )
            return [self._to_task(r) for r in result.scalars().all()]

    async def record_model_usage(
        self,
        session_id: UUID,
        *,
        provider: str,
        model: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int | None = None,
        latency_ms: int | None = None,
        cost_usd: float | None = None,
        request_id: str | None = None,
        agent_state_id: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> UUID:
        async with self._sf() as db:
            if await db.get(SessionRow, session_id) is None:
                raise NotFoundError("Session", session_id)
            total = total_tokens if total_tokens is not None else prompt_tokens + completion_tokens
            rid = uuid4()
            db.add(
                ModelUsageRow(
                    id=rid,
                    session_id=session_id,
                    agent_state_id=agent_state_id,
                    provider=provider,
                    model=model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total,
                    latency_ms=latency_ms,
                    cost_usd=cost_usd,
                    request_id=request_id,
                    metadata_=metadata or {},
                )
            )
            await db.commit()
            return rid

    async def record_tool_execution(
        self,
        session_id: UUID,
        *,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        result: dict[str, Any] | None = None,
        status: str = "success",
        error: str | None = None,
        latency_ms: int | None = None,
        tool_call_id: str | None = None,
        agent_state_id: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> UUID:
        async with self._sf() as db:
            if await db.get(SessionRow, session_id) is None:
                raise NotFoundError("Session", session_id)
            rid = uuid4()
            db.add(
                ToolExecutionRow(
                    id=rid,
                    session_id=session_id,
                    agent_state_id=agent_state_id,
                    tool_name=tool_name,
                    tool_call_id=tool_call_id,
                    arguments=arguments or {},
                    result=result,
                    status=status,
                    error=error,
                    latency_ms=latency_ms,
                    metadata_=metadata or {},
                )
            )
            await db.commit()
            return rid

    async def get_token_usage_summary(self, session_id: UUID) -> dict[str, Any]:
        async with self._sf() as db:
            result = await db.execute(
                select(ModelUsageRow).where(ModelUsageRow.session_id == session_id)
            )
            rows = result.scalars().all()
            return {
                "session_id": session_id,
                "call_count": len(rows),
                "prompt_tokens": sum(r.prompt_tokens for r in rows),
                "completion_tokens": sum(r.completion_tokens for r in rows),
                "total_tokens": sum(r.total_tokens for r in rows),
                "cost_usd": sum(r.cost_usd or 0.0 for r in rows),
            }

    async def set_execution_metadata(
        self, session_id: UUID, key: str, value: dict[str, Any]
    ) -> None:
        async with self._sf() as db:
            if await db.get(SessionRow, session_id) is None:
                raise NotFoundError("Session", session_id)
            result = await db.execute(
                select(ExecutionMetadataRow).where(
                    ExecutionMetadataRow.session_id == session_id,
                    ExecutionMetadataRow.key == key,
                )
            )
            row = result.scalar_one_or_none()
            if row is None:
                db.add(
                    ExecutionMetadataRow(
                        id=uuid4(), session_id=session_id, key=key, value=value
                    )
                )
            else:
                row.value = value
                row.updated_at = _now()
            await db.commit()

    async def get_execution_metadata(
        self, session_id: UUID, key: str | None = None
    ) -> dict[str, Any]:
        async with self._sf() as db:
            q = select(ExecutionMetadataRow).where(
                ExecutionMetadataRow.session_id == session_id
            )
            if key is not None:
                q = q.where(ExecutionMetadataRow.key == key)
            result = await db.execute(q)
            return {r.key: r.value for r in result.scalars().all()}

    @staticmethod
    def _to_project(row: ProjectRow) -> Project:
        return Project(
            id=row.id,
            name=row.name,
            description=row.description,
            owner_id=row.owner_id,
            workspace_path=row.workspace_path,
            status=row.status,
            metadata=row.metadata_ or {},
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def _to_session(row: SessionRow) -> Session:
        return Session(
            id=row.id,
            user_id=row.user_id,
            project_id=row.project_id,
            title=row.title,
            status=row.status,
            metadata=row.metadata_ or {},
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def _to_agent_state(row: AgentStateRow) -> AgentState:
        return AgentState(
            id=row.id,
            session_id=row.session_id,
            project_id=row.project_id,
            messages=row.messages or [],
            artifacts=row.artifacts or {},
            tasks=row.tasks or [],
            current_node=row.current_node,
            status=row.status,
            error=row.error,
            metadata=row.metadata_ or {},
            created_at=row.created_at,
            updated_at=row.updated_at,
            version=row.version,
        )

    @staticmethod
    def _to_task(row: TaskRow) -> Task:
        depends: list[UUID] = []
        for d in row.depends_on or []:
            try:
                depends.append(UUID(str(d)))
            except (ValueError, TypeError):
                continue
        try:
            status_enum = TaskStatus(row.status)
        except ValueError:
            status_enum = TaskStatus.PENDING
        return Task(
            id=row.id,
            project_id=row.project_id,
            session_id=row.session_id,
            title=row.title,
            description=row.description,
            status=status_enum,
            parent_id=row.parent_id,
            depends_on=depends,
            assignee=row.assignee,
            result=row.result,
            metadata=row.metadata_ or {},
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def _state_to_dict(row: AgentStateRow) -> dict[str, Any]:
        return {
            "id": str(row.id),
            "session_id": str(row.session_id),
            "project_id": str(row.project_id) if row.project_id else None,
            "messages": row.messages or [],
            "artifacts": row.artifacts or {},
            "tasks": row.tasks or [],
            "current_node": row.current_node,
            "status": row.status,
            "error": row.error,
            "metadata": row.metadata_ or {},
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            "version": row.version,
        }
