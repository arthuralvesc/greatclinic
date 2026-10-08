from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.repositories.patient_repository import SqlAlchemyPatientRepository
from app.use_cases.patients.lookup_patient_by_phone import LookupPatientByPhone


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with factory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_lookup_patient_by_phone(session: SessionDep) -> LookupPatientByPhone:
    return LookupPatientByPhone(SqlAlchemyPatientRepository(session))
