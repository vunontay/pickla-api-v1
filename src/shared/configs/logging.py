import json
import logging
import logging.config
from datetime import UTC, datetime
from typing import Any

from src.shared.configs.settings import settings


class _UseAppSettings:
    """Default for ``_inject_better_stack`` overrides: read from ``settings``."""

    __slots__ = ()


_USE_APP_SETTINGS = _UseAppSettings()

# Standard LogRecord attributes — excluded from the "extra" fields in JSON output.
_STANDARD_ATTRS: frozenset[str] = frozenset(
    logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys()
) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    """Emit each log record as a single-line JSON object.

    Standard fields (timestamp, level, logger, message) are always present.
    Any extra fields passed via the ``extra={}`` argument are merged in automatically.
    """

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()
        entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.message,
        }
        for key, value in record.__dict__.items():
            if key not in _STANDARD_ATTRS:
                entry[key] = value
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


def build_logging_config(
    *, debug: bool = False, json_logs: bool = False
) -> dict[str, Any]:
    """Build the base console-only logging config dict.

    Does not include any Better Stack / logtail configuration.
    Call ``configure_logging`` to apply config with optional Better Stack support.
    """
    level = "DEBUG" if debug else "INFO"

    if json_logs:
        default_formatter: dict[str, Any] = {"()": JsonFormatter}
        access_formatter: dict[str, Any] = {"()": JsonFormatter}
    else:
        default_formatter = {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
        access_formatter = {
            "format": (
                '%(asctime)s - %(client_addr)s - "%(request_line)s" %(status_code)s'
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": default_formatter,
            "access": access_formatter,
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "handlers": ["default"],
            "level": level,
        },
        "loggers": {
            "pickla": {
                "handlers": ["default"],
                "level": level,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "level": "WARNING",
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "propagate": True,
            },
        },
    }


def _inject_better_stack(
    config: dict[str, Any],
    *,
    source_token: str | None | _UseAppSettings = _USE_APP_SETTINGS,
    ingest_host: str | None | _UseAppSettings = _USE_APP_SETTINGS,
) -> None:
    """Augment a console config dict with the logtail handler.

    Adds the logtail handler and attaches it to the app-owned loggers
    (pickla, uvicorn, uvicorn.access). Root logger is intentionally excluded
    to avoid forwarding third-party library logs to Better Stack.

    Raises ValueError if BETTER_STACK_SOURCE_TOKEN is not configured — a missing
    token in a non-dev environment is a deployment error, not a recoverable state.

    ``source_token`` / ``ingest_host`` default to application settings; tests may pass
    explicit values so unit tests do not depend on process env or ``settings`` mocks.
    """
    resolved_token = (
        settings.BETTER_STACK_SOURCE_TOKEN
        if source_token is _USE_APP_SETTINGS
        else source_token
    )
    resolved_host = (
        settings.BETTER_STACK_INGEST_HOST
        if ingest_host is _USE_APP_SETTINGS
        else ingest_host
    )
    if not resolved_token:
        raise ValueError(
            "BETTER_STACK_SOURCE_TOKEN must be set in non-dev environments"
        )
    config["handlers"]["logtail"] = {
        "class": "logtail.LogtailHandler",
        "level": "INFO",
        "source_token": resolved_token,
        "host": resolved_host,
    }
    for name in ("pickla", "uvicorn"):
        config["loggers"][name]["handlers"].append("logtail")
    config["loggers"]["uvicorn.access"]["handlers"].append("logtail")


def configure_logging(*, debug: bool = False, json_logs: bool = False) -> None:
    config = build_logging_config(debug=debug, json_logs=json_logs)
    if not debug:
        _inject_better_stack(config)
    logging.config.dictConfig(config)
