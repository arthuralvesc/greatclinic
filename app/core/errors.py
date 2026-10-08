from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.errors import DomainError, InvalidPhoneError

# Domain error class -> (HTTP status, stable error code, message suitable to be read aloud).
_HTTP_ERRORS: dict[type[DomainError], tuple[int, str, str]] = {
    InvalidPhoneError: (400, "INVALID_PHONE", "That phone number is not valid."),
}


def error_body(status_code: int, error: str, message: str, request_id: str) -> dict[str, object]:
    return {
        "statusCode": status_code,
        "error": error,
        "message": message,
        "requestId": request_id,
    }


async def _handle_domain_error(request: Request, exc: Exception) -> JSONResponse:
    status_code, code, message = _HTTP_ERRORS[type(exc)]  # type: ignore[index]
    return JSONResponse(
        error_body(status_code, code, message, str(uuid4())), status_code=status_code
    )


def register_exception_handlers(app: FastAPI) -> None:
    for error_type in _HTTP_ERRORS:
        app.add_exception_handler(error_type, _handle_domain_error)
