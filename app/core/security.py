import secrets
from typing import Annotated

from fastapi import Header, Request

from app.core.config import Settings


class UnauthorizedError(Exception):
    """The X-API-Key header is missing or does not match."""


async def verify_api_key(
    request: Request,
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    settings: Settings = request.app.state.settings
    expected = settings.ai_agent_api_key.encode()
    # Compare bytes so a non-ASCII header cannot make compare_digest raise.
    if x_api_key is None or not secrets.compare_digest(x_api_key.encode(), expected):
        raise UnauthorizedError()
