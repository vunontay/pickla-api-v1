import sys
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.main import app
from src.shared.configs.settings import settings
from src.shared.database.dependencies import get_db

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


_test_engine = (
    create_async_engine(settings.TEST_DATABASE_URL, echo=False)
    if settings.TEST_DATABASE_URL
    else None
)
_TestSessionLocal = (
    async_sessionmaker(
        bind=_test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    if _test_engine
    else None
)


async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
    if _TestSessionLocal is None:
        raise RuntimeError("TEST_DATABASE_URL is not configured")
    async with _TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with _TestSessionLocal() as session:
        yield session


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
