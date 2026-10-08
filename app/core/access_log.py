import json
import logging
import sys
import time

from starlette.types import ASGIApp, Message, Receive, Scope, Send

ACCESS_LOGGER_NAME = "greatclinic.access"
_access_logger = logging.getLogger(ACCESS_LOGGER_NAME)


def configure_access_logging() -> None:
    """Emit one bare JSON line per request on stdout. Safe to call more than once."""
    # uvicorn's own access log prints the raw URL, query string included, and the query
    # carries phone numbers (health data). Our middleware logs the route template instead.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    if _access_logger.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    _access_logger.addHandler(handler)
    _access_logger.setLevel(logging.INFO)


class AccessLogMiddleware:
    """Logs request id, method, route template, status, error code and latency.

    The route template is logged instead of the raw URL because query strings carry
    phone numbers. Request and response bodies are never read.
    """

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        started = time.perf_counter()
        status = 500

        async def send_capturing_status(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self._app(scope, receive, send_capturing_status)
        except Exception:
            self._log(scope, 500, "INTERNAL_ERROR", started)
            raise
        self._log(scope, status, scope.get("state", {}).get("error_code"), started)

    @staticmethod
    def _log(scope: Scope, status: int, error_code: str | None, started: float) -> None:
        route = scope.get("route")
        line = {
            "requestId": scope.get("state", {}).get("request_id"),
            "method": scope["method"],
            "route": getattr(route, "path", "unmatched"),
            "status": status,
            "errorCode": error_code,
            "latencyMs": round((time.perf_counter() - started) * 1000, 2),
        }
        _access_logger.info(json.dumps(line))
