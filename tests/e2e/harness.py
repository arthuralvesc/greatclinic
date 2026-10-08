from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

TEST_DATABASE_URL_DEFAULT = "postgresql+asyncpg://user:pass@localhost:5432/clinic_test"


@asynccontextmanager
async def rolled_back_session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Yield a session whose work is always rolled back on exit.

    The session joins an outer transaction through savepoints, so code under test
    can call ``commit()`` freely without making anything permanent.
    """
    async with engine.connect() as connection:
        outer = await connection.begin()
        session = AsyncSession(
            bind=connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )
        try:
            yield session
        finally:
            await session.close()
            await outer.rollback()
