REQUEST_VALIDATION_ERROR = "request_validation_error"
INTERNAL_ERROR = "internal_error"
HTTP_ERROR = "http_error"

HTTP_STATUS_TO_ERROR_CODE: dict[int, str] = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    408: "request_timeout",
    409: "conflict",
    429: "too_many_requests",
    500: INTERNAL_ERROR,
    502: "bad_gateway",
    503: "service_unavailable",
    504: "gateway_timeout",
}
