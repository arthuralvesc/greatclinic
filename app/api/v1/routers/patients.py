from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import get_lookup_patient_by_phone, get_register_patient
from app.api.v1.schemas.patients import (
    LookupPatientResponse,
    PatientResponse,
    RegisterPatientRequest,
)
from app.domain.entities.patient import Patient
from app.use_cases.patients.lookup_patient_by_phone import LookupPatientByPhone
from app.use_cases.patients.register_patient import RegisterPatient

router = APIRouter(tags=["patients"])


@router.get(
    "/patients/lookup",
    response_model=LookupPatientResponse,
    response_model_exclude_none=True,
)
async def lookup_patient(
    phone: str,
    use_case: Annotated[LookupPatientByPhone, Depends(get_lookup_patient_by_phone)],
) -> LookupPatientResponse:
    patient = await use_case.execute(phone)
    if patient is None:
        return LookupPatientResponse(exists=False)
    return LookupPatientResponse(exists=True, patient=_to_response(patient))


def _to_response(patient: Patient) -> PatientResponse:
    return PatientResponse(
        id=patient.id,
        name=patient.name,
        email=patient.email,
        phone=patient.phone.e164,
        birth_date=patient.birth_date,
    )


@router.post("/patients", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def register_patient(
    body: RegisterPatientRequest,
    use_case: Annotated[RegisterPatient, Depends(get_register_patient)],
) -> PatientResponse:
    patient = await use_case.execute(
        name=body.name, phone=body.phone, email=body.email, birth_date=body.birth_date
    )
    return _to_response(patient)
