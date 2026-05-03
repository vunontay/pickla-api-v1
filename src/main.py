import uvicorn
from fastapi import FastAPI
from src.api.v1 import router as api_router
from src.shared.configs.logging import configure_logging
from src.shared.configs.settings import settings
from src.shared.errors.handlers import register_exception_handlers
from src.shared.middlewares.request_logging import RequestLoggingMiddleware

configure_logging(debug=settings.debug, json_logs=settings.log_json)

app = FastAPI()

app.add_middleware(RequestLoggingMiddleware)


@app.get("/health", tags=["probes"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/healthz", tags=["probes"])
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz", tags=["probes"])
async def readyz() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")

register_exception_handlers(app)


def run() -> None:
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        log_config=None,
    )


if __name__ == "__main__":
    run()
