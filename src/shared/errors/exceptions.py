from typing import Any


class AppException(Exception):
    """Base exception for all application errors"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "internal_error",
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    """Resource not found"""

    def __init__(self, resource: str, resource_id: Any, message: str | None = None):
        super().__init__(
            message=message or f"{resource} with ID {resource_id} not found",
            status_code=404,
            error_code="not_found",
            details={"resource": resource, "resource_id": str(resource_id)},
        )


class ValidationError(AppException):
    """Input validation failed"""

    def __init__(self, field: str, message: str, value: Any = None):
        super().__init__(
            message=f"Validation error on field '{field}': {message}",
            status_code=422,
            error_code="validation_error",
            details={"field": field, "value": str(value) if value else None},
        )


class AuthenticationError(AppException):
    """Authentication failed"""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message, status_code=401, error_code="authentication_error"
        )


class AuthorizationError(AppException):
    """User lacks permission"""

    def __init__(self, action: str, resource: str, message: str | None = None):
        super().__init__(
            message=message or f"Not authorized to {action} {resource}",
            status_code=403,
            error_code="authorization_error",
            details={"action": action, "resource": resource},
        )


class ConflictError(AppException):
    """Resource conflict, like duplicate entries"""

    def __init__(self, resource: str, message: str | None = None):
        super().__init__(
            message=message or f"{resource} already exists",
            status_code=409,
            error_code="conflict",
            details={"resource": resource},
        )


class ExternalServiceError(AppException):
    """Third-party service failed"""

    def __init__(self, service: str, message: str | None = None):
        super().__init__(
            message=message or f"External service '{service}' is unavailable",
            status_code=503,
            error_code="service_unavailable",
            details={"service": service},
        )
