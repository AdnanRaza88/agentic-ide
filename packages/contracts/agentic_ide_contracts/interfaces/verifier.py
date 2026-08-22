"""Verifier contract."""

from __future__ import annotations

from enum import Enum
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class VerificationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class VerificationResult(BaseModel):
    name: str
    status: VerificationStatus
    message: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    duration_ms: int | None = None


@runtime_checkable
class Verifier(Protocol):
    @property
    def name(self) -> str:
        ...

    async def verify(
        self, workspace: Any, context: dict[str, Any] | None = None
    ) -> list[VerificationResult]:
        """Run verification suite against the workspace."""
        ...
