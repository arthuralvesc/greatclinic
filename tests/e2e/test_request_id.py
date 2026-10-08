import httpx


async def test_a_valid_request_id_is_echoed_in_the_header_and_the_error_body(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get(
        "/v1/patients/lookup",
        params={"phone": "not a phone"},
        headers={"X-Request-ID": "req-abc-123"},
    )

    assert response.status_code == 400
    assert response.headers["X-Request-ID"] == "req-abc-123"
    assert response.json()["requestId"] == "req-abc-123"


async def test_a_request_id_is_generated_when_none_is_sent(client: httpx.AsyncClient) -> None:
    response = await client.get("/v1/patients/lookup", params={"phone": "not a phone"})

    generated = response.headers["X-Request-ID"]
    assert generated
    assert response.json()["requestId"] == generated


async def test_an_unsafe_request_id_is_replaced_not_echoed(client: httpx.AsyncClient) -> None:
    too_long = "x" * 65
    for unsafe in (too_long, "has space", "semi;colon", "<script>"):
        response = await client.get(
            "/v1/patients/lookup",
            params={"phone": "not a phone"},
            headers={"X-Request-ID": unsafe},
        )

        assert response.headers["X-Request-ID"] != unsafe
        assert response.json()["requestId"] == response.headers["X-Request-ID"]


async def test_successful_responses_carry_the_request_id_header_too(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get(
        "/v1/patients/lookup",
        params={"phone": "(11) 99999-8888"},
        headers={"X-Request-ID": "req-ok-1"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-ok-1"
