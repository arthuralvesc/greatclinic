from dataclasses import dataclass
from datetime import date
from uuid import UUID

from app.domain.value_objects.phone import Phone


@dataclass(frozen=True)
class Patient:
    id: UUID
    name: str
    email: str
    phone: Phone
    birth_date: date
