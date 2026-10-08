from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.security import UnauthorizedError
from app.domain.errors import (
    EmailAlreadyRegisteredError,
    InvalidPatientError,
    InvalidPhoneError,
    PhoneAlreadyRegisteredError,
)

# Domain error class -> (HTTP status, stable error code, message suitable to be read aloud).
_HTTP_ERRORS: dict[type[Exception], tuple[int, str, str]] = {
    UnauthorizedError: (401, "UNAUTHORIZED", "A valid API key is required."),
    InvalidPhoneError: (400, "INVALID_PHONE", "That phone number is not valid."),
    InvalidPatientError: (400, "VALIDATION_ERROR", "The patient details are not valid."),
    PhoneAlreadyRegisteredError: (
        409,
        "PHONE_ALREADY_REGISTERED",
        "A patient with this phone number is already registered.",
    ),
    EmailAlreadyRegisteredError: (
        409,
        "EMAIL_ALREADY_REGISTERED",
        "A patient with this email is already registered.",
    ),
}


def error_body(status_code: int, error: str, message: str, request_id: str) -> dict[str, object]:
    return {
        "statusCode": status_code,
        "error": error,
        "message": message,
        "requestId": request_id,
    }


async def _handle_domain_error(request: Request, exc: Exception) -> JSONResponse:
    status_code, code, message = _HTTP_ERRORS[type(exc)]
    request.state.error_code = code
    return JSONResponse(
        error_body(status_code, code, message, request.state.request_id), status_code=status_code
    )


async def _handle_validation_error(request: Request, exc: Exception) -> JSONResponse:
    # Field details are deliberately left out: they can echo patient data back.
    request.state.error_code = "VALIDATION_ERROR"
    body = error_body(
        400, "VALIDATION_ERROR", "The request is not valid.", request.state.request_id
    )
    return JSONResponse(body, status_code=400)


async def _handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    # Never echo the exception: it can carry patient data. Starlette runs this handler
    # outside RequestIdMiddleware, so the header has to be set here.
    request_id: str = request.state.request_id
    body = error_body(500, "INTERNAL_ERROR", "Something went wrong. Please try again.", request_id)
    return JSONResponse(body, status_code=500, headers={"X-Request-ID": request_id})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, _handle_unexpected_error)
    app.add_exception_handler(RequestValidationError, _handle_validation_error)
    for error_type in _HTTP_ERRORS:
        app.add_exception_handler(error_type, _handle_domain_error)
