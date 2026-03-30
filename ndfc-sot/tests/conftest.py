"""Shared test fixtures."""

from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("NDFC_SOT_API_KEY", "test-key-12345")
os.environ.setdefault(
    "NDFC_SOT_DATABASE_URL",
    "postgresql+asyncpg://ndfc:ndfc@localhost:5432/ndfc_sot_test",
)

from app.config import settings  # noqa: E402
from app.database import get_async_session  # noqa: E402
from app.db_models import Base  # noqa: E402
from app.main import app  # noqa: E402

TEST_DB_URL = settings.database_url.replace(
    "/ndfc_sot", "/ndfc_sot_test"
) if "ndfc_sot_test" not in settings.database_url else settings.database_url


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create async engine and setup/teardown schema."""
    eng = create_async_engine(TEST_DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional test session that rolls back."""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client with overridden DB dependency."""

    async def _override():
        yield db_session

    app.dependency_overrides[get_async_session] = _override
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"X-API-Key": "test-key-12345"},
    ) as c:
        yield c
    app.dependency_overrides.clear()