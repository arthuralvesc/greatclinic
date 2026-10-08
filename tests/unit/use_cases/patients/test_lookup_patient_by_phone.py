from datetime import date
from uuid import uuid4

import pytest

from app.domain.entities.patient import Patient
from app.domain.errors import InvalidPhoneError
from app.domain.value_objects.phone import Phone
from app.use_cases.patients.lookup_patient_by_phone import LookupPatientByPhone
from tests.unit.fakes import InMemoryPatientRepository


async def test_finds_a_known_patient_whatever_the_phone_format() -> None:
    repo = InMemoryPatientRepository()
    maria = Patient(
        id=uuid4(),
        name="Maria Silva",
        email="maria@example.com",
        phone=Phone.parse("+5511999998888"),
        birth_date=date(1990, 5, 17),
    )
    await repo.add(maria)

    found = await LookupPatientByPhone(repo).execute("(11) 99999-8888")

    assert found == maria


async def test_returns_none_for_an_unknown_but_well_formed_phone() -> None:
    found = await LookupPatientByPhone(InMemoryPatientRepository()).execute("(21) 98888-7777")

    assert found is None


async def test_rejects_an_unparseable_phone() -> None:
    with pytest.raises(InvalidPhoneError):
        await LookupPatientByPhone(InMemoryPatientRepository()).execute("uh, eleven nine")
