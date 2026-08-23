from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid

from agentic_ide_state.database import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class ProjectRow(Base):
    __tablename__ = "ai_projects"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    owner_id: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    workspace_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="active", nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    sessions: Mapped[list[SessionRow]] = relationship(back_populates="project")
    tasks: Mapped[list[TaskRow]] = relationship(back_populates="project")


class SessionRow(Base):
    __tablename__ = "ai_sessions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    project_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("ai_projects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(512), default="Untitled Session", nullable=False)
    status: Mapped[str] = mapped_column(String(64), default="active", nullable=False, index=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    latest_state_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)

    project: Mapped[ProjectRow | None] = relationship(back_populates="sessions")
    agent_states: Mapped[list[AgentStateRow]] = relationship(back_populates="session")
    tasks: Mapped[list[TaskRow]] = relationship(back_populates="session")
    messages: Mapped[list[MessageRow]] = relationship(back_populates="session")
    model_usages: Mapped[list[ModelUsageRow]] = relationship(back_populates="session")
    tool_executions: Mapped[list[ToolExecutionRow]] = relationship(back_populates="session")


class AgentStateRow(Base):
    __tablename__ = "ai_agent_states"
    __table_args__ = (
        UniqueConstraint("session_id", "version", name="uq_agent_state_session_version"),
        Index("ix_agent_states_session_updated", "session_id", "updated_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("ai_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True, index=True)
    messages: Mapped[list[Any]] = mapped_column(JSON, default=list)
    artifacts: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    tasks: Mapped[list[Any]] = mapped_column(JSON, default=list)
    current_node: Mapped[str | None] = mapped_column(String(256), nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="running", nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    session: Mapped[SessionRow] = relationship(back_populates="agent_states")
    checkpoints: Mapped[list[CheckpointRow]] = relationship(back_populates="agent_state")


class CheckpointRow(Base):
    __tablename__ = "ai_checkpoints"
    __table_args__ = (Index("ix_checkpoints_session_created", "session_id", "created_at"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("ai_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_state_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("ai_agent_states.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    label: Mapped[str | None] = mapped_column(String(256), nullable=True)
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(128), nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)

    agent_state: Mapped[AgentStateRow] = relationship(back_populates="checkpoints")


class MessageRow(Base):
    __tablename__ = "ai_messages"
    __table_args__ = (Index("ix_messages_session_created", "session_id", "created_at"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("ai_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_state_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True, index=True)
    role: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    tool_call_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tool_calls: Mapped[list[Any] | None] = mapped_column(JSON, nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)

    session: Mapped[SessionRow] = relationship(back_populates="messages")


class TaskRow(Base):
    __tablename__ = "ai_tasks"
    __table_args__ = (Index("ix_tasks_session_status", "session_id", "status"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    project_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("ai_projects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    session_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("ai_sessions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(64), default="pending", nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True, index=True)
    depends_on: Mapped[list[Any]] = mapped_column(JSON, default=list)
    assignee: Mapped[str | None] = mapped_column(String(256), nullable=True)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    project: Mapped[ProjectRow | None] = relationship(back_populates="tasks")
    session: Mapped[SessionRow | None] = relationship(back_populates="tasks")


class ModelUsageRow(Base):
    __tablename__ = "ai_model_usages"
    __table_args__ = (Index("ix_model_usages_session_created", "session_id", "created_at"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("ai_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_state_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    provider: Mapped[str] = mapped_column(String(128), nullable=False)
    model: Mapped[str] = mapped_column(String(256), nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[float | None] = mapped_column(nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, server_default=func.now(), nullable=False
    )

    session: Mapped[SessionRow] = relationship(back_populates="model_usages")


class ToolExecutionRow(Base):
    __tablename__ = "ai_tool_executions"
    __table_args__ = (Index("ix_tool_exec_session_created", "session_id", "created_at"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("ai_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_state_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    tool_name: Mapped[str] = mapped_column(String(256), nullable=False)
    tool_call_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    arguments: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="success", nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, server_default=func.now(), nullable=False
    )

    session: Mapped[SessionRow] = relationship(back_populates="tool_executions")


class ExecutionMetadataRow(Base):
    __tablename__ = "ai_execution_metadata"
    __table_args__ = (UniqueConstraint("session_id", "key", name="uq_exec_meta_session_key"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("ai_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(256), nullable=False)
    value: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )
