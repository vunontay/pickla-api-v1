import logging
import traceback
from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.shared.errors.error_codes import (
    HTTP_ERROR,
    HTTP_STATUS_TO_ERROR_CODE,
    INTERNAL_ERROR,
    REQUEST_VALIDATION_ERROR,
)
from src.shared.errors.exceptions import AppException
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def create_error_response(
    code: str,
    fallback_error_code: str,
    request_id: str | None = None,
) -> dict[str, object]:
    error_payload: dict[str, str] = {
        "code": code or fallback_error_code,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    if request_id:
        error_payload["request_id"] = request_id

    return {"success": False, "error": error_payload}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        logger.warning(
            "Application error: %s - %s",
            exc.error_code,
            exc.message,
            extra={
                "error_code": exc.error_code,
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
                "details": exc.details,
            },
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                code=exc.error_code,
                fallback_error_code=exc.error_code,
                request_id=getattr(request.state, "request_id", None),
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append(
                {
                    "field": field,
                    "message": error["msg"],
                    "type": error["type"],
                }
            )

        logger.warning(
            "Validation error on %s",
            request.url.path,
            extra={"errors": errors, "method": request.method},
        )
        return JSONResponse(
            status_code=422,
            content=create_error_response(
                code=REQUEST_VALIDATION_ERROR,
                fallback_error_code=REQUEST_VALIDATION_ERROR,
                request_id=getattr(request.state, "request_id", None),
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        error_code = HTTP_STATUS_TO_ERROR_CODE.get(exc.status_code, HTTP_ERROR)
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                code=error_code,
                fallback_error_code=error_code,
                request_id=getattr(request.state, "request_id", None),
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            "Unhandled exception: %s: %s",
            type(exc).__name__,
            str(exc),
            extra={
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc(),
            },
        )
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                code=INTERNAL_ERROR,
                fallback_error_code=INTERNAL_ERROR,
                request_id=getattr(request.state, "request_id", None),
            ),
        )
