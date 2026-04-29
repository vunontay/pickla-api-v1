import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Attach request metadata for logging and error correlation."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id

            duration = time.perf_counter() - start_time
            logger.info(
                "%s %s - %s",
                request.method,
                request.url.path,
                response.status_code,
                extra={
                    "request_id": request_id,
                    "duration_ms": round(duration * 1000, 2),
                    "status_code": response.status_code,
                },
            )
            return response
        except Exception:
            duration = time.perf_counter() - start_time
            logger.exception(
                "Request failed: %s %s",
                request.method,
                request.url.path,
                extra={
                    "request_id": request_id,
                    "duration_ms": round(duration * 1000, 2),
                },
            )
            raise
