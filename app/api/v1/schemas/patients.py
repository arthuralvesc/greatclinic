from datetime import date
from uuid import UUID

from app.api.v1.schemas.base import CamelModel


class PatientResponse(CamelModel):
    id: UUID
    name: str
    email: str
    phone: str
    birth_date: date


class LookupPatientResponse(CamelModel):
    exists: bool
    patient: PatientResponse | None = None
