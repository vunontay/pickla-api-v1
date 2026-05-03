import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("pickla.requests")

_SILENT_PATHS: frozenset[str] = frozenset({"/health", "/healthz", "/readyz"})


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log each request: method, path+query in the message line, status, duration.

    Reuses ``X-Request-ID`` from the inbound request when set (e.g. load balancer or
    upstream service) for end-to-end correlation; if the header is absent, generates a
    UUID.

    Structured ``extra["path"]`` is the path only (no query string) for aggregation;
    the human-readable log message includes ``?…`` when a query string is present.

    The resolved id is stored on ``request.state`` and echoed on the response
    ``X-Request-ID`` header.

    Liveness-style paths (``/health``, ``/healthz``, ``/readyz``) skip *successful*
    request lines to limit probe noise; 4xx/5xx and uncaught exceptions are still
    logged so a missing route or broken handler is visible in production.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        path = request.url.path
        path_for_log = path + (f"?{request.url.query}" if request.url.query else "")
        start_time = time.perf_counter()
        silent_probe = path in _SILENT_PATHS

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.exception(
                "%s %s 500 (%.2fms)",
                request.method,
                path_for_log,
                duration_ms,
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": path,
                    "status_code": 500,
                    "duration_ms": round(duration_ms, 2),
                },
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000
        status = response.status_code

        if silent_probe and status < 400:
            response.headers["X-Request-ID"] = request_id
            return response

        if status >= 500:
            log = logger.error
        elif status >= 400:
            log = logger.warning
        else:
            log = logger.info

        log(
            "%s %s %s (%.2fms)",
            request.method,
            path_for_log,
            status,
            duration_ms,
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": path,
                "status_code": status,
                "duration_ms": round(duration_ms, 2),
            },
        )

        response.headers["X-Request-ID"] = request_id
        return response
