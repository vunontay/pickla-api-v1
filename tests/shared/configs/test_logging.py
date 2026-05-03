import json
import logging
from unittest.mock import patch

import pytest
from src.shared.configs.logging import (
    JsonFormatter,
    _inject_better_stack,
    build_logging_config,
    configure_logging,
)

_FAKE_BETTER_STACK_TOKEN = "fake-token-for-unit-tests"


def test_production_mode_sets_pickla_logger_to_info() -> None:
    config = build_logging_config(debug=False)
    assert config["loggers"]["pickla"]["level"] == "INFO"


def test_debug_mode_sets_pickla_logger_to_debug() -> None:
    config = build_logging_config(debug=True)
    assert config["loggers"]["pickla"]["level"] == "DEBUG"


def test_uvicorn_loggers_always_info_regardless_of_debug_flag() -> None:
    for debug in (True, False):
        config = build_logging_config(debug=debug)
        assert config["loggers"]["uvicorn"]["level"] == "INFO"
        assert config["loggers"]["uvicorn.access"]["level"] == "WARNING"


def test_config_includes_all_required_loggers() -> None:
    config = build_logging_config()
    required = {"pickla", "uvicorn", "uvicorn.error", "uvicorn.access"}
    assert required.issubset(config["loggers"].keys())


def test_build_logging_config_sets_root_logger_with_default_handler() -> None:
    prod = build_logging_config(debug=False)
    assert prod["root"]["handlers"] == ["default"]
    assert prod["root"]["level"] == "INFO"

    dev = build_logging_config(debug=True)
    assert dev["root"]["handlers"] == ["default"]
    assert dev["root"]["level"] == "DEBUG"


def test_module_loggers_propagate_to_configured_root() -> None:
    """Typical ``getLogger(__name__)`` loggers under ``src`` propagate to root."""
    configure_logging(debug=True)
    module_logger = logging.getLogger("src.shared.errors.handlers")
    root = logging.getLogger()

    assert module_logger.propagate is True
    assert not module_logger.handlers
    assert root.handlers
    assert root.level == logging.DEBUG


def test_configure_logging_applies_config_to_python_logging() -> None:
    configure_logging(debug=True)
    pickla_logger = logging.getLogger("pickla")
    assert pickla_logger.level == logging.DEBUG

    with patch("src.shared.configs.logging._inject_better_stack"):
        configure_logging(debug=False)
    pickla_logger = logging.getLogger("pickla")
    assert pickla_logger.level == logging.INFO


def test_configure_logging_succeeds_with_json_logs() -> None:
    with patch("src.shared.configs.logging._inject_better_stack"):
        configure_logging(debug=False, json_logs=True)
    pickla_logger = logging.getLogger("pickla")
    assert pickla_logger.level == logging.INFO


def test_better_stack_injected_when_not_debug() -> None:
    config = build_logging_config(debug=False)
    _inject_better_stack(
        config,
        source_token=_FAKE_BETTER_STACK_TOKEN,
        ingest_host=None,
    )
    assert "logtail" in config["handlers"]
    assert "logtail" in config["loggers"]["pickla"]["handlers"]


def test_better_stack_not_injected_in_debug_mode() -> None:
    """Dev environment uses console-only logging; no Better Stack traffic."""
    config = build_logging_config(debug=True)
    assert "logtail" not in config["handlers"]
    assert "logtail" not in config["loggers"]["pickla"]["handlers"]


def test_inject_better_stack_raises_if_token_missing() -> None:
    """Fail loudly when non-dev is deployed without the required token."""
    config = build_logging_config()
    with pytest.raises(ValueError, match="BETTER_STACK_SOURCE_TOKEN"):
        _inject_better_stack(config, source_token=None)


def test_inject_better_stack_explicit_token_does_not_use_settings_singleton() -> None:
    """Fails if tests call inject without kwargs: no BETTER_STACK_* in env required."""
    config = build_logging_config()
    with patch("src.shared.configs.logging.settings") as mock_settings:
        mock_settings.BETTER_STACK_SOURCE_TOKEN = None
        mock_settings.BETTER_STACK_INGEST_HOST = None
        _inject_better_stack(
            config,
            source_token=_FAKE_BETTER_STACK_TOKEN,
            ingest_host=None,
        )
    assert config["handlers"]["logtail"]["source_token"] == _FAKE_BETTER_STACK_TOKEN


def test_uvicorn_access_logger_suppressed_to_warning() -> None:
    config = build_logging_config()
    assert config["loggers"]["uvicorn.access"]["level"] == "WARNING"


def test_plain_mode_uvicorn_access_uses_access_handler_not_default() -> None:
    """Uvicorn access records need client_addr / request_line in plain text."""
    config = build_logging_config(json_logs=False)
    assert config["loggers"]["uvicorn.access"]["handlers"] == ["access"]
    assert config["handlers"]["access"]["formatter"] == "access"
    fmt = config["formatters"]["access"]["format"]
    assert "%(client_addr)s" in fmt
    assert "%(request_line)s" in fmt


def test_json_mode_uvicorn_access_uses_access_handler() -> None:
    config = build_logging_config(json_logs=True)
    assert config["loggers"]["uvicorn.access"]["handlers"] == ["access"]


def test_sqlalchemy_engine_suppressed_to_warning() -> None:
    """Prevents SQL query spam in Better Stack on every DB operation."""
    config = build_logging_config()
    assert config["loggers"]["sqlalchemy.engine"]["level"] == "WARNING"


def test_inject_better_stack_adds_logtail_to_app_loggers() -> None:
    config = build_logging_config()
    _inject_better_stack(
        config,
        source_token=_FAKE_BETTER_STACK_TOKEN,
        ingest_host=None,
    )

    assert "logtail" in config["handlers"]
    assert "logtail" in config["loggers"]["pickla"]["handlers"]
    assert "logtail" in config["loggers"]["uvicorn"]["handlers"]
    assert config["loggers"]["uvicorn.access"]["handlers"] == ["access", "logtail"]


def test_inject_better_stack_does_not_add_logtail_to_root() -> None:
    config = build_logging_config()
    _inject_better_stack(
        config,
        source_token=_FAKE_BETTER_STACK_TOKEN,
        ingest_host=None,
    )

    assert "logtail" not in config["root"]["handlers"]


def test_plain_mode_does_not_use_json_formatter() -> None:
    config = build_logging_config(json_logs=False)
    formatter_class = config["formatters"]["default"].get("()")
    assert formatter_class is None


def test_json_mode_uses_json_formatter_for_default_handler() -> None:
    config = build_logging_config(json_logs=True)
    assert config["formatters"]["default"]["()"] is JsonFormatter


def test_json_mode_uses_json_formatter_for_access_handler() -> None:
    config = build_logging_config(json_logs=True)
    assert config["formatters"]["access"]["()"] is JsonFormatter


def _make_record(
    msg: str, level: int = logging.INFO, **extra: object
) -> logging.LogRecord:
    record = logging.LogRecord(
        name="pickla.test",
        level=level,
        pathname="",
        lineno=0,
        msg=msg,
        args=(),
        exc_info=None,
    )
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_json_formatter_outputs_valid_json() -> None:
    formatter = JsonFormatter()
    record = _make_record("hello")
    output = formatter.format(record)
    parsed = json.loads(output)
    assert isinstance(parsed, dict)


def test_json_formatter_includes_required_fields() -> None:
    formatter = JsonFormatter()
    record = _make_record("test message")
    parsed = json.loads(formatter.format(record))
    assert parsed["message"] == "test message"
    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "pickla.test"
    assert "timestamp" in parsed


def test_json_formatter_includes_extra_fields() -> None:
    formatter = JsonFormatter()
    record = _make_record(
        "req", request_id="abc-123", status_code=200, duration_ms=42.5
    )
    parsed = json.loads(formatter.format(record))
    assert parsed["request_id"] == "abc-123"
    assert parsed["status_code"] == 200
    assert parsed["duration_ms"] == 42.5


def test_json_formatter_timestamp_is_iso8601() -> None:
    from datetime import datetime

    formatter = JsonFormatter()
    record = _make_record("ts test")
    parsed = json.loads(formatter.format(record))
    datetime.fromisoformat(parsed["timestamp"])
    assert parsed["timestamp"].endswith("+00:00")


def test_json_formatter_includes_exception_info() -> None:
    formatter = JsonFormatter()
    try:
        raise ValueError("boom")
    except ValueError:
        import sys

        record = logging.LogRecord(
            name="pickla.test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="error occurred",
            args=(),
            exc_info=sys.exc_info(),
        )
    parsed = json.loads(formatter.format(record))
    assert "exception" in parsed
    assert "ValueError" in parsed["exception"]
