from typing import Protocol

from app.domain.entities.patient import Patient
from app.domain.value_objects.phone import Phone


class UnitOfWork(Protocol):
    """Owns the transaction. Use cases commit through it; repositories never commit."""

    async def commit(self) -> None: ...


class PatientRepository(Protocol):
    async def add(self, patient: Patient) -> None: ...

    async def get_by_phone(self, phone: Phone) -> Patient | None: ...

    async def get_by_email(self, email: str) -> Patient | None: ...
