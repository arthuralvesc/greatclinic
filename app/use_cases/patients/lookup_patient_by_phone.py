from app.domain.entities.patient import Patient
from app.domain.repositories import PatientRepository
from app.domain.value_objects.phone import Phone


class LookupPatientByPhone:
    def __init__(self, patients: PatientRepository) -> None:
        self._patients = patients

    async def execute(self, phone: str) -> Patient | None:
        return await self._patients.get_by_phone(Phone.parse(phone))
