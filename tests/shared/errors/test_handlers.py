from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from src.shared.errors.exceptions import AppException
from src.shared.errors.handlers import register_exception_handlers
from src.shared.middlewares.request_logging import RequestLoggingMiddleware


def build_test_client() -> TestClient:
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)
    register_exception_handlers(app)

    @app.get("/app-exception")
    async def app_exception_route() -> None:
        raise AppException(
            message="Password does not meet complexity requirements",
            status_code=422,
            error_code="must_valid_password",
            details={"field": "password"},
        )

    @app.get("/validation/{item_id}")
    async def validation_route(item_id: int) -> dict[str, int]:
        return {"item_id": item_id}

    @app.get("/http")
    async def http_exception_route() -> None:
        raise HTTPException(status_code=403, detail="Forbidden")

    @app.get("/unhandled")
    async def unhandled_exception_route() -> None:
        raise RuntimeError("Unexpected")

    return TestClient(app, raise_server_exceptions=False)


def assert_minimal_error_payload(payload: dict) -> None:
    assert payload["success"] is False
    assert "error" in payload
    assert "code" in payload["error"]
    assert "timestamp" in payload["error"]
    assert "message" not in payload["error"]
    assert "details" not in payload["error"]


def test_app_exception_response_uses_custom_error_code() -> None:
    client = build_test_client()
    response = client.get("/app-exception")

    assert response.status_code == 422
    body = response.json()
    assert_minimal_error_payload(body)
    assert body["error"]["code"] == "must_valid_password"
    assert body["error"]["request_id"]


def test_validation_exception_response_uses_standard_error_code() -> None:
    client = build_test_client()
    response = client.get("/validation/invalid-id")

    assert response.status_code == 422
    body = response.json()
    assert_minimal_error_payload(body)
    assert body["error"]["code"] == "request_validation_error"
    assert body["error"]["request_id"]


def test_http_exception_response_maps_status_to_error_code() -> None:
    client = build_test_client()
    response = client.get("/http")

    assert response.status_code == 403
    body = response.json()
    assert_minimal_error_payload(body)
    assert body["error"]["code"] == "forbidden"
    assert body["error"]["request_id"]


def test_unhandled_exception_response_uses_internal_error_code() -> None:
    client = build_test_client()
    response = client.get("/unhandled")

    assert response.status_code == 500
    body = response.json()
    assert_minimal_error_payload(body)
    assert body["error"]["code"] == "internal_error"
    assert body["error"]["request_id"]
