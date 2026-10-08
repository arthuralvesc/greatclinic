from datetime import date
from uuid import uuid4

from app.core.clock import Clock
from app.domain.entities.patient import Patient
from app.domain.errors import (
    EmailAlreadyRegisteredError,
    InvalidPatientError,
    PhoneAlreadyRegisteredError,
)
from app.domain.repositories import PatientRepository, UnitOfWork
from app.domain.value_objects.phone import Phone

MAX_AGE_YEARS = 120


class RegisterPatient:
    def __init__(self, patients: PatientRepository, clock: Clock, uow: UnitOfWork) -> None:
        self._patients = patients
        self._clock = clock
        self._uow = uow

    async def execute(self, *, name: str, phone: str, email: str, birth_date: date) -> Patient:
        if not name.strip():
            raise InvalidPatientError("name must not be blank")
        today = self._clock.now().date()
        if birth_date > today:
            raise InvalidPatientError("birth date must not be in the future")
        had_birthday = (today.month, today.day) >= (birth_date.month, birth_date.day)
        if today.year - birth_date.year - (not had_birthday) > MAX_AGE_YEARS:
            raise InvalidPatientError("patient age must not exceed 120 years")
        normalized_phone = Phone.parse(phone)
        if await self._patients.get_by_phone(normalized_phone) is not None:
            raise PhoneAlreadyRegisteredError(normalized_phone.e164)
        if await self._patients.get_by_email(email) is not None:
            raise EmailAlreadyRegisteredError()
        patient = Patient(
            id=uuid4(),
            name=name,
            email=email,
            phone=normalized_phone,
            birth_date=birth_date,
        )
        await self._patients.add(patient)
        await self._uow.commit()
        return patient
