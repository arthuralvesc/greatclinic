from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from app.domain.entities.patient import Patient
from app.domain.errors import EmailAlreadyRegisteredError, PhoneAlreadyRegisteredError
from app.domain.value_objects.phone import Phone
from app.infrastructure.repositories.patient_repository import SqlAlchemyPatientRepository
from tests.e2e.harness import rolled_back_session


def make_patient(*, name: str, email: str, phone: str) -> Patient:
    return Patient(
        id=uuid4(),
        name=name,
        email=email,
        phone=Phone.parse(phone),
        birth_date=date(1990, 5, 17),
    )


async def test_the_unique_phone_constraint_is_reported_as_phone_already_registered(
    engine: AsyncEngine,
) -> None:
    async with rolled_back_session(engine) as session:
        repo = SqlAlchemyPatientRepository(session)
        await repo.add(
            make_patient(name="Maria Silva", email="a@example.com", phone="+5511999998888")
        )

        with pytest.raises(PhoneAlreadyRegisteredError):
            await repo.add(
                make_patient(name="Joana Souza", email="b@example.com", phone="+5511999998888")
            )


async def test_the_unique_email_constraint_is_reported_as_email_already_registered(
    engine: AsyncEngine,
) -> None:
    async with rolled_back_session(engine) as session:
        repo = SqlAlchemyPatientRepository(session)
        await repo.add(
            make_patient(name="Maria Silva", email="a@example.com", phone="+5511999998888")
        )

        with pytest.raises(EmailAlreadyRegisteredError):
            await repo.add(
                make_patient(name="Joana Souza", email="a@example.com", phone="+5521988887777")
            )
