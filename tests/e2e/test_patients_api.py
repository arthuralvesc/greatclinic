import httpx


async def test_lookup_of_an_unknown_but_well_formed_phone_returns_exists_false(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get("/v1/patients/lookup", params={"phone": "(11) 99999-8888"})

    assert response.status_code == 200
    assert response.json() == {"exists": False}
