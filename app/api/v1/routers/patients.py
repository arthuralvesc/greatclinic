from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_lookup_patient_by_phone
from app.api.v1.schemas.patients import LookupPatientResponse, PatientResponse
from app.use_cases.patients.lookup_patient_by_phone import LookupPatientByPhone

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
    return LookupPatientResponse(
        exists=True,
        patient=PatientResponse(
            id=patient.id,
            name=patient.name,
            email=patient.email,
            phone=patient.phone.e164,
            birth_date=patient.birth_date,
        ),
    )
