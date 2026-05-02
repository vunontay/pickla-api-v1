import json
import logging
import logging.config
from datetime import UTC, datetime
from typing import Any

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
                "level": "INFO",
                "propagate": False,
            },
        },
    }


def configure_logging(*, debug: bool = False, json_logs: bool = False) -> None:
    logging.config.dictConfig(build_logging_config(debug=debug, json_logs=json_logs))
