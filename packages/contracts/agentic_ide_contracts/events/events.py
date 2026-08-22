"""Event contracts for realtime & internal messaging."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    SESSION_STARTED = "session.started"
    SESSION_ENDED = "session.ended"
    STATE_UPDATED = "state.updated"
    AGENT_STEP = "agent.step"
    TOOL_CALLED = "tool.called"
    TOOL_RESULT = "tool.result"
    MODEL_REQUEST = "model.request"
    MODEL_RESPONSE = "model.response"
    VERIFICATION_STARTED = "verification.started"
    VERIFICATION_COMPLETED = "verification.completed"
    PREVIEW_READY = "preview.ready"
    ERROR = "error"
    LOG = "log"


class Event(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: EventType
    session_id: UUID | None = None
    project_id: UUID | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str | None = None
