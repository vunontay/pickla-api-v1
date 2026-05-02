from unittest.mock import patch

from fastapi.testclient import TestClient
from src.main import app, run


def test_docs_endpoint_is_available() -> None:
    client = TestClient(app)
    response = client.get("/docs")

    assert response.status_code == 200


def test_run_invokes_uvicorn_with_expected_options() -> None:
    with patch("uvicorn.run") as mock_uvicorn_run:
        run()

    mock_uvicorn_run.assert_called_once_with(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        log_config=None,
    )
