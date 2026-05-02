import uuid
from unittest.mock import patch

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from src.shared.middlewares.request_logging import RequestLoggingMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


def build_test_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/ok")
    async def ok_route() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/not-found")
    async def not_found_route() -> None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Not found")

    @app.get("/server-error")
    async def server_error_route() -> None:
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail="Server error")

    @app.get("/state")
    async def state_route(request: Request) -> dict[str, str]:
        return {"request_id": request.state.request_id}

    return app


def build_app_where_inner_middleware_raises_before_response() -> FastAPI:
    """Inner middleware raises so outer RequestLoggingMiddleware sees call_next fail."""

    class ExplodingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            raise RuntimeError("boom before response")

    app = FastAPI()
    app.add_middleware(ExplodingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/never-reached")
    async def never_reached() -> dict[str, str]:
        return {"status": "ok"}

    return app


@pytest.fixture
def client() -> TestClient:
    return TestClient(build_test_app())


def test_response_contains_x_request_id_header(client: TestClient) -> None:
    response = client.get("/ok")
    assert "x-request-id" in response.headers


def test_x_request_id_is_valid_uuid(client: TestClient) -> None:
    response = client.get("/ok")
    request_id = response.headers["x-request-id"]
    uuid.UUID(request_id)


def test_request_state_contains_request_id(client: TestClient) -> None:
    response = client.get("/state")
    assert response.status_code == 200
    request_id = response.json()["request_id"]
    uuid.UUID(request_id)


def test_success_request_logged_at_info_level(client: TestClient) -> None:
    with patch("src.shared.middlewares.request_logging.logger") as mock_logger:
        client.get("/ok")
        mock_logger.info.assert_called_once()
        mock_logger.warning.assert_not_called()
        mock_logger.error.assert_not_called()


def test_log_message_includes_query_string_extra_path_is_route_only(
    client: TestClient,
) -> None:
    with patch("src.shared.middlewares.request_logging.logger") as mock_logger:
        client.get("/ok", params={"page": "2", "limit": "10"})

    mock_logger.info.assert_called_once()
    _msg, method, path_for_log, status, _duration_ms = mock_logger.info.call_args[0]
    assert method == "GET"
    assert status == 200
    assert path_for_log == "/ok?page=2&limit=10"
    extra = mock_logger.info.call_args.kwargs["extra"]
    assert extra["path"] == "/ok"


def test_log_message_has_no_query_suffix_when_query_empty(client: TestClient) -> None:
    with patch("src.shared.middlewares.request_logging.logger") as mock_logger:
        client.get("/ok")

    _msg, _method, path_for_log, _status, _duration_ms = mock_logger.info.call_args[0]
    assert path_for_log == "/ok"
    assert "?" not in path_for_log


def test_client_error_logged_at_warning_level(client: TestClient) -> None:
    with patch("src.shared.middlewares.request_logging.logger") as mock_logger:
        client.get("/not-found")
        mock_logger.warning.assert_called_once()
        mock_logger.info.assert_not_called()
        mock_logger.error.assert_not_called()


def test_server_error_logged_at_error_level(client: TestClient) -> None:
    with patch("src.shared.middlewares.request_logging.logger") as mock_logger:
        client.get("/server-error")
        mock_logger.error.assert_called_once()
        mock_logger.info.assert_not_called()
        mock_logger.warning.assert_not_called()


def test_each_request_gets_unique_request_id(client: TestClient) -> None:
    ids = {client.get("/ok").headers["x-request-id"] for _ in range(3)}
    assert len(ids) == 3


def test_reuses_incoming_x_request_id_from_upstream(client: TestClient) -> None:
    upstream_id = "lb-abc-123"
    response = client.get("/ok", headers={"X-Request-ID": upstream_id})
    assert response.headers["x-request-id"] == upstream_id


def test_incoming_x_request_id_available_on_request_state(client: TestClient) -> None:
    upstream_id = "trace-from-gateway"
    response = client.get("/state", headers={"X-Request-ID": upstream_id})
    assert response.status_code == 200
    assert response.json()["request_id"] == upstream_id


def test_call_next_exception_logs_with_exception_and_request_metadata() -> None:
    app = build_app_where_inner_middleware_raises_before_response()
    client = TestClient(app, raise_server_exceptions=False)

    with patch("src.shared.middlewares.request_logging.logger") as mock_logger:
        response = client.get("/never-reached")

    assert response.status_code == 500
    mock_logger.exception.assert_called_once()
    call_kwargs = mock_logger.exception.call_args.kwargs
    assert call_kwargs["extra"]["request_id"]
    assert call_kwargs["extra"]["status_code"] == 500
    assert call_kwargs["extra"]["method"] == "GET"
    assert call_kwargs["extra"]["path"] == "/never-reached"
    mock_logger.info.assert_not_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()
