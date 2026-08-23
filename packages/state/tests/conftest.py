from __future__ import annotations

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from agentic_ide_state.database import create_engine, create_session_factory, init_db
from agentic_ide_state.service import StateService


@pytest_asyncio.fixture
async def engine() -> AsyncEngine:
    eng = create_engine("sqlite+aiosqlite:///:memory:", echo=False)
    await init_db(eng)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(engine)


@pytest_asyncio.fixture
async def svc(session_factory: async_sessionmaker[AsyncSession]) -> StateService:
    return StateService(session_factory)
