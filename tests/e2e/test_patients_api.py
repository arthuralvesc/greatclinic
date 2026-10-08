import httpx


async def test_lookup_of_an_unknown_but_well_formed_phone_returns_exists_false(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get("/v1/patients/lookup", params={"phone": "(11) 99999-8888"})

    assert response.status_code == 200
    assert response.json() == {"exists": False}


async def test_registered_patient_is_created_and_then_found_by_phone(
    client: httpx.AsyncClient,
) -> None:
    created = await client.post(
        "/v1/patients",
        json={
            "name": "Maria Silva",
            "phone": "(11) 99999-8888",
            "email": "maria@example.com",
            "birthDate": "1990-05-17",
        },
    )

    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "Maria Silva"
    assert body["phone"] == "+5511999998888"
    assert body["birthDate"] == "1990-05-17"

    found = await client.get("/v1/patients/lookup", params={"phone": "+55 11 99999-8888"})

    assert found.status_code == 200
    assert found.json() == {"exists": True, "patient": body}


async def test_lookup_of_an_unparseable_phone_returns_400_invalid_phone(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get("/v1/patients/lookup", params={"phone": "uh, eleven nine"})

    assert response.status_code == 400
    body = response.json()
    assert body["statusCode"] == 400
    assert body["error"] == "INVALID_PHONE"
    assert body["message"]
    assert body["requestId"]


async def test_registering_a_phone_that_already_exists_returns_409(
    client: httpx.AsyncClient,
) -> None:
    first = {
        "name": "Maria Silva",
        "phone": "(11) 99999-8888",
        "email": "maria@example.com",
        "birthDate": "1990-05-17",
    }
    second = {
        **first,
        "name": "Joana Souza",
        "phone": "+55 11 99999-8888",
        "email": "j@example.com",
    }
    assert (await client.post("/v1/patients", json=first)).status_code == 201

    response = await client.post("/v1/patients", json=second)

    assert response.status_code == 409
    assert response.json()["error"] == "PHONE_ALREADY_REGISTERED"


async def test_registering_an_email_that_already_exists_returns_409(
    client: httpx.AsyncClient,
) -> None:
    first = {
        "name": "Maria Silva",
        "phone": "(11) 99999-8888",
        "email": "maria@example.com",
        "birthDate": "1990-05-17",
    }
    second = {**first, "name": "Joana Souza", "phone": "(21) 98888-7777"}
    assert (await client.post("/v1/patients", json=first)).status_code == 201

    response = await client.post("/v1/patients", json=second)

    assert response.status_code == 409
    assert response.json()["error"] == "EMAIL_ALREADY_REGISTERED"


async def test_registering_a_blank_name_returns_400_validation_error(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/v1/patients",
        json={
            "name": "   ",
            "phone": "(11) 99999-8888",
            "email": "maria@example.com",
            "birthDate": "1990-05-17",
        },
    )

    assert response.status_code == 400
    assert response.json()["error"] == "VALIDATION_ERROR"


async def test_a_body_missing_required_fields_returns_400_validation_error(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post("/v1/patients", json={"name": "Maria Silva"})

    assert response.status_code == 400
    body = response.json()
    assert body["statusCode"] == 400
    assert body["error"] == "VALIDATION_ERROR"
    assert body["message"]
    assert body["requestId"]
