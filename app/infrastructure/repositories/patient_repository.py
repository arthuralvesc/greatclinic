from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.patient import Patient
from app.domain.errors import EmailAlreadyRegisteredError, PhoneAlreadyRegisteredError
from app.domain.value_objects.phone import Phone
from app.infrastructure.db.models import PatientModel

PHONE_CONSTRAINT = "patients_phone_key"
EMAIL_CONSTRAINT = "patients_email_key"


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
        try:
            await self._session.flush()
        except IntegrityError as exc:
            if PHONE_CONSTRAINT in str(exc.orig):
                raise PhoneAlreadyRegisteredError() from exc
            if EMAIL_CONSTRAINT in str(exc.orig):
                raise EmailAlreadyRegisteredError() from exc
            raise

    async def get_by_phone(self, phone: Phone) -> Patient | None:
        row = await self._session.scalar(
            select(PatientModel).where(PatientModel.phone == phone.e164)
        )
        return _to_entity(row) if row else None

    async def get_by_email(self, email: str) -> Patient | None:
        row = await self._session.scalar(select(PatientModel).where(PatientModel.email == email))
        return _to_entity(row) if row else None
