"""Workspace contract."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable
from pathlib import PurePosixPath
from pydantic import BaseModel


class FileInfo(BaseModel):
    path: str
    is_dir: bool
    size: int | None = None
    modified_at: str | None = None


@runtime_checkable
class Workspace(Protocol):
    @property
    def root(self) -> PurePosixPath:
        ...

    async def read_text(self, path: str) -> str:
        ...

    async def write_text(self, path: str, content: str) -> None:
        ...

    async def list_dir(self, path: str = ".") -> list[FileInfo]:
        ...

    async def exists(self, path: str) -> bool:
        ...

    async def delete(self, path: str) -> None:
        ...

    async def mkdir(self, path: str) -> None:
        ...
