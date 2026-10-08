import httpx


async def test_a_request_without_an_api_key_is_rejected_with_401(
    client: httpx.AsyncClient,
) -> None:
    del client.headers["X-API-Key"]

    response = await client.get("/v1/patients/lookup", params={"phone": "(11) 99999-8888"})

    assert response.status_code == 401
    body = response.json()
    assert body["statusCode"] == 401
    assert body["error"] == "UNAUTHORIZED"
    assert body["message"]
    assert body["requestId"]


async def test_a_wrong_api_key_is_rejected_with_401(client: httpx.AsyncClient) -> None:
    client.headers["X-API-Key"] = "not-the-key"

    response = await client.get("/v1/patients/lookup", params={"phone": "(11) 99999-8888"})

    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"


async def test_a_non_ascii_api_key_is_rejected_with_401_not_a_server_error(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get(
        "/v1/patients/lookup",
        params={"phone": "(11) 99999-8888"},
        headers={b"X-API-Key": "chave-é".encode("latin-1")},
    )

    assert response.status_code == 401


async def test_authentication_is_checked_before_the_body_is_validated(
    client: httpx.AsyncClient,
) -> None:
    del client.headers["X-API-Key"]

    response = await client.post("/v1/patients", json={"name": "Maria Silva"})

    assert response.status_code == 401
