from typing import Protocol

from app.domain.entities.patient import Patient
from app.domain.value_objects.phone import Phone


class PatientRepository(Protocol):
    async def add(self, patient: Patient) -> None: ...

    async def get_by_phone(self, phone: Phone) -> Patient | None: ...

    async def get_by_email(self, email: str) -> Patient | None: ...
