import httpx
from fastapi import FastAPI

from app.api.deps import get_lookup_patient_by_phone
from app.use_cases.patients.lookup_patient_by_phone import LookupPatientByPhone
from tests.e2e.conftest import API_KEY


async def test_an_unexpected_error_returns_the_standard_500_body_without_leaking_details(
    app: FastAPI,
) -> None:
    async def broken() -> LookupPatientByPhone:
        raise RuntimeError("db exploded for +5511999998888")

    app.dependency_overrides[get_lookup_patient_by_phone] = broken
    # Starlette re-raises after its 500 handler has responded; the client must not.
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)

    async with httpx.AsyncClient(
        transport=transport, base_url="http://test", headers={"X-API-Key": API_KEY}
    ) as client:
        response = await client.get(
            "/v1/patients/lookup",
            params={"phone": "(11) 99999-8888"},
            headers={"X-Request-ID": "req-500-1"},
        )

    assert response.status_code == 500
    body = response.json()
    assert body["statusCode"] == 500
    assert body["error"] == "INTERNAL_ERROR"
    assert body["message"]
    assert body["requestId"] == "req-500-1"
    assert response.headers["X-Request-ID"] == "req-500-1"
    assert "exploded" not in response.text
    assert "5511999998888" not in response.text
