"""Specification contract."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Specification(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID | None = None
    title: str
    problem_statement: str
    requirements: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    architecture_notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
