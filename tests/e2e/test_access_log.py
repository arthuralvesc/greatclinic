import json
import logging

import httpx
import pytest
from fastapi import FastAPI

from app.api.deps import get_lookup_patient_by_phone
from app.core.config import Settings
from app.main import create_app
from app.use_cases.patients.lookup_patient_by_phone import LookupPatientByPhone
from tests.e2e.conftest import API_KEY

ACCESS_LOGGER = "greatclinic.access"


def access_lines(caplog: pytest.LogCaptureFixture) -> list[dict[str, object]]:
    return [
        json.loads(record.getMessage()) for record in caplog.records if record.name == ACCESS_LOGGER
    ]


async def test_each_request_logs_one_structured_line_without_the_raw_url(
    client: httpx.AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger=ACCESS_LOGGER):
        await client.get(
            "/v1/patients/lookup",
            params={"phone": "not a phone"},
            headers={"X-Request-ID": "req-log-1"},
        )

    (line,) = access_lines(caplog)
    assert line["requestId"] == "req-log-1"
    assert line["method"] == "GET"
    assert line["route"] == "/v1/patients/lookup"
    assert line["status"] == 400
    assert line["errorCode"] == "INVALID_PHONE"
    assert isinstance(line["latencyMs"], int | float)
    raw = " ".join(record.getMessage() for record in caplog.records)
    assert "not a phone" not in raw
    assert "phone=" not in raw


async def test_a_successful_request_logs_a_null_error_code(
    client: httpx.AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger=ACCESS_LOGGER):
        await client.get("/v1/patients/lookup", params={"phone": "(11) 99999-8888"})

    (line,) = access_lines(caplog)
    assert line["status"] == 200
    assert line["errorCode"] is None


async def test_an_unmatched_url_is_logged_as_unmatched_never_by_its_raw_path(
    client: httpx.AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger=ACCESS_LOGGER):
        response = await client.get("/v1/no-such-thing/%2B5511999998888")

    assert response.status_code == 404
    (line,) = access_lines(caplog)
    assert line["route"] == "unmatched"
    assert "5511999998888" not in json.dumps(line)


async def test_request_bodies_are_never_logged(
    client: httpx.AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger=ACCESS_LOGGER):
        await client.post(
            "/v1/patients",
            json={
                "name": "Maria Silva",
                "phone": "(11) 99999-8888",
                "email": "maria@example.com",
                "birthDate": "1990-05-17",
            },
        )

    raw = " ".join(record.getMessage() for record in caplog.records)
    assert access_lines(caplog)
    for secret in ("Maria", "99999", "maria@example.com", "1990-05-17"):
        assert secret not in raw


async def test_an_unexpected_error_is_logged_as_a_500(
    app: FastAPI, caplog: pytest.LogCaptureFixture
) -> None:
    async def broken() -> LookupPatientByPhone:
        raise RuntimeError("boom")

    app.dependency_overrides[get_lookup_patient_by_phone] = broken
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)

    with caplog.at_level(logging.INFO, logger=ACCESS_LOGGER):
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test", headers={"X-API-Key": API_KEY}
        ) as client:
            await client.get("/v1/patients/lookup", params={"phone": "(11) 99999-8888"})

    (line,) = access_lines(caplog)
    assert line["status"] == 500
    assert line["errorCode"] == "INTERNAL_ERROR"
    assert "boom" not in json.dumps(line)


def test_uvicorns_own_access_log_is_silenced_because_it_prints_the_raw_url(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    uvicorn_access = logging.getLogger("uvicorn.access")
    # Reproduce what uvicorn's logging config does before the app is created.
    monkeypatch.setattr(uvicorn_access, "level", logging.INFO)
    uvicorn_access.manager._clear_cache()  # type: ignore[attr-defined]
    assert uvicorn_access.isEnabledFor(logging.INFO)

    create_app(settings)

    assert not uvicorn_access.isEnabledFor(logging.INFO)
