"""
Custom application errors and error codes.
Provides structured error handling with specific error codes.
"""

# Error codes for authentication
ERROR_MISSING_TOKEN = "MISSING_TOKEN"
ERROR_INVALID_TOKEN = "INVALID_TOKEN"
ERROR_TOKEN_EXPIRED = "TOKEN_EXPIRED"

# Error codes for resources
ERROR_USER_NOT_FOUND = "USER_NOT_FOUND"
ERROR_EMAIL_EXISTS = "EMAIL_ALREADY_EXISTS"
ERROR_TASK_NOT_FOUND = "TASK_NOT_FOUND"

# Error codes for authorization
ERROR_FORBIDDEN = "FORBIDDEN"
ERROR_INVALID_CREDENTIALS = "INVALID_CREDENTIALS"

# Error codes for validation
ERROR_VALIDATION_FAILED = "VALIDATION_ERROR"

# Error codes for server errors
ERROR_INTERNAL_SERVER = "INTERNAL_SERVER_ERROR"
ERROR_DATABASE_ERROR = "DATABASE_ERROR"


class AppException(Exception):
    """
    Custom application exception with structured error information.

    Attributes:
        status_code: HTTP status code
        error_code: Application-specific error code
        message: Human-readable error message
        details: Optional list of error details (for validation errors)
    """

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: list = None
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or []
        super().__init__(self.message)
