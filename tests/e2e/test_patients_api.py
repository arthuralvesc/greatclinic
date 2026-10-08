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
