from datetime import UTC, datetime

from app.domain.entities.patient import Patient
from app.domain.value_objects.phone import Phone


class InMemoryPatientRepository:
    def __init__(self) -> None:
        self._patients: list[Patient] = []

    async def add(self, patient: Patient) -> None:
        self._patients.append(patient)

    async def get_by_phone(self, phone: Phone) -> Patient | None:
        return next((p for p in self._patients if p.phone == phone), None)

    async def get_by_email(self, email: str) -> Patient | None:
        return next((p for p in self._patients if p.email == email), None)


class FixedClock:
    def __init__(self, now: datetime = datetime(2026, 10, 7, 15, 0, tzinfo=UTC)) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1
