import os
from collections.abc import AsyncIterator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from tests.e2e.harness import TEST_DATABASE_URL_DEFAULT, rolled_back_session


@pytest.fixture
async def engine() -> AsyncIterator[AsyncEngine]:
    url = os.environ.get("TEST_DATABASE_URL", TEST_DATABASE_URL_DEFAULT)
    engine = create_async_engine(url)
    yield engine
    await engine.dispose()


async def test_writes_in_one_session_are_invisible_to_the_next(engine: AsyncEngine) -> None:
    async with rolled_back_session(engine) as session:
        await session.execute(text("CREATE TABLE harness_probe (id int, label text)"))
        await session.execute(text("INSERT INTO harness_probe VALUES (1, 'leaked?')"))
        await session.commit()  # the code under test commits; the harness must still roll back
        inside = await session.scalar(text("SELECT count(*) FROM harness_probe"))
        assert inside == 1

    async with rolled_back_session(engine) as session:
        exists = await session.scalar(text("SELECT to_regclass('harness_probe') IS NOT NULL"))
        assert exists is False
