"""
Custom exception classes for LinguaFlow.
Provides structured error handling throughout the application.
"""


class LinguaFlowException(Exception):
    """Base exception for all LinguaFlow errors."""
    
    def __init__(self, message, status_code=500, error_code=None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        super().__init__(self.message)
    
    def to_dict(self):
        """Convert exception to dictionary for JSON response."""
        return {
            "error": self.message,
            "error_code": self.error_code,
            "status_code": self.status_code
        }


class ValidationError(LinguaFlowException):
    """Raised when input validation fails."""
    
    def __init__(self, message, field=None):
        self.field = field
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR"
        )
    
    def to_dict(self):
        result = super().to_dict()
        if self.field:
            result["field"] = self.field
        return result


class AuthenticationError(LinguaFlowException):
    """Raised when authentication fails."""
    
    def __init__(self, message="Authentication failed"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(LinguaFlowException):
    """Raised when authorization fails."""
    
    def __init__(self, message="Access denied"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )


class NotFoundError(LinguaFlowException):
    """Raised when a resource is not found."""
    
    def __init__(self, message="Resource not found"):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND"
        )


class ConflictError(LinguaFlowException):
    """Raised when there's a conflict (e.g., duplicate resource)."""
    
    def __init__(self, message="Resource conflict"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT"
        )


class DatabaseError(LinguaFlowException):
    """Raised when database operations fail."""
    
    def __init__(self, message="Database operation failed"):
        super().__init__(
            message=message,
            status_code=503,
            error_code="DATABASE_ERROR"
        )


class ExternalServiceError(LinguaFlowException):
    """Raised when external service (Groq API, etc.) fails."""
    
    def __init__(self, message="External service unavailable", service=None):
        self.service = service
        super().__init__(
            message=message,
            status_code=503,
            error_code="EXTERNAL_SERVICE_ERROR"
        )
    
    def to_dict(self):
        result = super().to_dict()
        if self.service:
            result["service"] = self.service
        return result


class RateLimitError(LinguaFlowException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message="Rate limit exceeded", retry_after=None):
        self.retry_after = retry_after
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED"
        )
    
    def to_dict(self):
        result = super().to_dict()
        if self.retry_after:
            result["retry_after"] = self.retry_after
        return result
