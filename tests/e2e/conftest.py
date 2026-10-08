import os
import subprocess
import sys
from collections.abc import AsyncIterator

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.api.deps import get_session
from app.core.config import Settings
from app.main import create_app
from tests.e2e.harness import TEST_DATABASE_URL_DEFAULT, rolled_back_session

API_KEY = "test-api-key"


@pytest.fixture(scope="session")
def database_url() -> str:
    return os.environ.get("TEST_DATABASE_URL", TEST_DATABASE_URL_DEFAULT)


@pytest.fixture(scope="session")
def migrated(database_url: str) -> None:
    """Bring the test database to the latest Alembic revision once per run."""
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=True,
        env={**os.environ, "DATABASE_URL": database_url},
    )


@pytest.fixture(scope="session")
async def engine(database_url: str, migrated: None) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(database_url)
    yield engine
    await engine.dispose()


@pytest.fixture
def settings(database_url: str) -> Settings:
    return Settings(
        database_url=database_url,
        ai_agent_api_key=API_KEY,
        clinic_timezone="America/Sao_Paulo",
        slot_duration_minutes=30,
        min_booking_notice_minutes=120,
        max_booking_advance_days=90,
        max_active_appointments_per_patient=5,
    )


@pytest.fixture
async def app(engine: AsyncEngine, settings: Settings) -> AsyncIterator[FastAPI]:
    application = create_app(settings)
    async with rolled_back_session(engine) as session:

        async def override_session() -> AsyncIterator[AsyncSession]:
            yield session

        application.dependency_overrides[get_session] = override_session
        yield application


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        headers={"X-API-Key": API_KEY},
    ) as http_client:
        yield http_client
