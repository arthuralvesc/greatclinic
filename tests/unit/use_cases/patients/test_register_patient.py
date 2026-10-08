from datetime import date

import pytest

from app.domain.errors import (
    EmailAlreadyRegisteredError,
    InvalidPatientError,
    PhoneAlreadyRegisteredError,
)
from app.use_cases.patients.register_patient import RegisterPatient
from tests.unit.fakes import FakeUnitOfWork, FixedClock, InMemoryPatientRepository


async def test_registers_a_patient_with_a_normalized_phone() -> None:
    repo = InMemoryPatientRepository()
    register = RegisterPatient(repo, FixedClock(), FakeUnitOfWork())

    patient = await register.execute(
        name="Maria Silva",
        phone="(11) 99999-8888",
        email="maria@example.com",
        birth_date=date(1990, 5, 17),
    )

    assert patient.name == "Maria Silva"
    assert patient.phone.e164 == "+5511999998888"
    assert await repo.get_by_phone(patient.phone) == patient


async def test_rejects_a_phone_that_is_already_registered_in_any_format() -> None:
    register = RegisterPatient(InMemoryPatientRepository(), FixedClock(), FakeUnitOfWork())
    await register.execute(
        name="Maria Silva",
        phone="(11) 99999-8888",
        email="maria@example.com",
        birth_date=date(1990, 5, 17),
    )

    with pytest.raises(PhoneAlreadyRegisteredError):
        await register.execute(
            name="Joana Souza",
            phone="+55 11 99999-8888",
            email="joana@example.com",
            birth_date=date(1985, 1, 2),
        )


async def test_rejects_an_email_that_is_already_registered() -> None:
    register = RegisterPatient(InMemoryPatientRepository(), FixedClock(), FakeUnitOfWork())
    await register.execute(
        name="Maria Silva",
        phone="(11) 99999-8888",
        email="maria@example.com",
        birth_date=date(1990, 5, 17),
    )

    with pytest.raises(EmailAlreadyRegisteredError):
        await register.execute(
            name="Joana Souza",
            phone="(21) 98888-7777",
            email="maria@example.com",
            birth_date=date(1985, 1, 2),
        )


async def test_reports_the_phone_first_when_phone_and_email_both_clash() -> None:
    register = RegisterPatient(InMemoryPatientRepository(), FixedClock(), FakeUnitOfWork())
    await register.execute(
        name="Maria Silva",
        phone="(11) 99999-8888",
        email="maria@example.com",
        birth_date=date(1990, 5, 17),
    )

    with pytest.raises(PhoneAlreadyRegisteredError):
        await register.execute(
            name="Joana Souza",
            phone="(11) 99999-8888",
            email="maria@example.com",
            birth_date=date(1985, 1, 2),
        )


@pytest.mark.parametrize("blank", ["", "   ", "\t\n"])
async def test_rejects_a_blank_name(blank: str) -> None:
    repo = InMemoryPatientRepository()
    register = RegisterPatient(repo, FixedClock(), FakeUnitOfWork())

    with pytest.raises(InvalidPatientError):
        await register.execute(
            name=blank,
            phone="(11) 99999-8888",
            email="maria@example.com",
            birth_date=date(1990, 5, 17),
        )

    assert await repo.get_by_email("maria@example.com") is None


async def test_rejects_a_birth_date_in_the_future() -> None:
    repo = InMemoryPatientRepository()
    register = RegisterPatient(repo, FixedClock(), FakeUnitOfWork())

    with pytest.raises(InvalidPatientError):
        await register.execute(
            name="Maria Silva",
            phone="(11) 99999-8888",
            email="maria@example.com",
            birth_date=date(2026, 10, 8),
        )

    assert await repo.get_by_email("maria@example.com") is None


async def test_rejects_a_patient_older_than_120_years() -> None:
    repo = InMemoryPatientRepository()
    register = RegisterPatient(repo, FixedClock(), FakeUnitOfWork())

    with pytest.raises(InvalidPatientError):
        await register.execute(
            name="Maria Silva",
            phone="(11) 99999-8888",
            email="maria@example.com",
            birth_date=date(1905, 10, 7),
        )

    assert await repo.get_by_email("maria@example.com") is None


async def test_accepts_a_patient_who_is_still_120_until_tomorrow() -> None:
    register = RegisterPatient(InMemoryPatientRepository(), FixedClock(), FakeUnitOfWork())

    patient = await register.execute(
        name="Maria Silva",
        phone="(11) 99999-8888",
        email="maria@example.com",
        birth_date=date(1905, 10, 8),
    )

    assert patient.birth_date == date(1905, 10, 8)


async def test_commits_once_after_storing_the_patient() -> None:
    uow = FakeUnitOfWork()
    register = RegisterPatient(InMemoryPatientRepository(), FixedClock(), uow)

    await register.execute(
        name="Maria Silva",
        phone="(11) 99999-8888",
        email="maria@example.com",
        birth_date=date(1990, 5, 17),
    )

    assert uow.commits == 1
