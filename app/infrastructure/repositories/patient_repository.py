from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.patient import Patient
from app.domain.value_objects.phone import Phone
from app.infrastructure.db.models import PatientModel


def _to_entity(row: PatientModel) -> Patient:
    return Patient(
        id=row.id,
        name=row.name,
        email=row.email,
        phone=Phone(row.phone),
        birth_date=row.birth_date,
    )


class SqlAlchemyPatientRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, patient: Patient) -> None:
        self._session.add(
            PatientModel(
                id=patient.id,
                name=patient.name,
                email=patient.email,
                phone=patient.phone.e164,
                birth_date=patient.birth_date,
            )
        )
        await self._session.flush()

    async def get_by_phone(self, phone: Phone) -> Patient | None:
        row = await self._session.scalar(
            select(PatientModel).where(PatientModel.phone == phone.e164)
        )
        return _to_entity(row) if row else None

    async def get_by_email(self, email: str) -> Patient | None:
        row = await self._session.scalar(select(PatientModel).where(PatientModel.email == email))
        return _to_entity(row) if row else None
