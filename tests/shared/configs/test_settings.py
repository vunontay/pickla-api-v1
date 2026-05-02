import pytest
from pydantic import ValidationError
from src.shared.configs.settings import Settings

_REQUIRED = {
    "DATABASE_URL": "postgresql+asyncpg://x:x@localhost/pickla",
    "TEST_DATABASE_URL": "postgresql+asyncpg://x:x@localhost/pickla_test",
    "REDIS_URL": "redis://localhost:6379",
    "SECRET_KEY": "test-secret-key",
}


def make_settings(**overrides: object) -> Settings:
    return Settings(**{**_REQUIRED, **overrides})


def test_dev_environment_enables_debug() -> None:
    assert make_settings(ENVIRONMENT="dev").debug is True


def test_stg_environment_disables_debug() -> None:
    assert make_settings(ENVIRONMENT="stg").debug is False


def test_prod_environment_disables_debug() -> None:
    assert make_settings(ENVIRONMENT="prod").debug is False


def test_dev_environment_disables_json_logs() -> None:
    assert make_settings(ENVIRONMENT="dev").log_json is False


def test_stg_environment_enables_json_logs() -> None:
    assert make_settings(ENVIRONMENT="stg").log_json is True


def test_prod_environment_enables_json_logs() -> None:
    assert make_settings(ENVIRONMENT="prod").log_json is True


def test_default_environment_is_dev() -> None:
    assert make_settings().debug is True
    assert make_settings().log_json is False


def test_invalid_environment_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        make_settings(ENVIRONMENT="production")
