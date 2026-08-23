from __future__ import annotations

from uuid import UUID


class StateError(Exception):
    pass


class NotFoundError(StateError):
    def __init__(self, entity: str, entity_id: UUID | str) -> None:
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} not found: {entity_id}")


class ConflictError(StateError):
    def __init__(self, entity: str, entity_id: UUID | str, expected_version: int) -> None:
        self.entity = entity
        self.entity_id = entity_id
        self.expected_version = expected_version
        super().__init__(
            f"{entity} {entity_id} version conflict (expected version={expected_version})"
        )


class InvalidTransitionError(StateError):
    def __init__(self, entity: str, from_status: str, to_status: str) -> None:
        super().__init__(f"Invalid {entity} transition: {from_status} -> {to_status}")
