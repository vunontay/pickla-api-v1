from src.shared.errors.exceptions import (
    AppException,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ExternalServiceError,
    NotFoundError,
    ValidationError,
)


def test_app_exception_uses_default_details_when_missing() -> None:
    exc = AppException(message="Unexpected")

    assert exc.message == "Unexpected"
    assert exc.status_code == 500
    assert exc.error_code == "internal_error"
    assert exc.details == {}


def test_not_found_error_uses_default_message() -> None:
    exc = NotFoundError(resource="Match", resource_id=123)

    assert exc.status_code == 404
    assert exc.error_code == "not_found"
    assert exc.message == "Match with ID 123 not found"
    assert exc.details == {"resource": "Match", "resource_id": "123"}


def test_validation_error_handles_none_value() -> None:
    exc = ValidationError(field="password", message="is invalid", value=None)

    assert exc.status_code == 422
    assert exc.error_code == "validation_error"
    assert exc.details == {"field": "password", "value": None}


def test_authentication_error_uses_default_message() -> None:
    exc = AuthenticationError()

    assert exc.status_code == 401
    assert exc.error_code == "authentication_error"
    assert exc.message == "Authentication required"


def test_authorization_error_uses_default_message() -> None:
    exc = AuthorizationError(action="delete", resource="match")

    assert exc.status_code == 403
    assert exc.error_code == "authorization_error"
    assert exc.message == "Not authorized to delete match"


def test_conflict_error_uses_default_message() -> None:
    exc = ConflictError(resource="Email")

    assert exc.status_code == 409
    assert exc.error_code == "conflict"
    assert exc.message == "Email already exists"


def test_external_service_error_uses_default_message() -> None:
    exc = ExternalServiceError(service="Payment")

    assert exc.status_code == 503
    assert exc.error_code == "service_unavailable"
    assert exc.message == "External service 'Payment' is unavailable"
