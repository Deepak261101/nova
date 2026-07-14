"""Application-level exceptions mapped to HTTP responses in the API layer."""

from __future__ import annotations


class NovaError(Exception):
    """Base class for domain/application errors."""

    status_code = 400
    detail = "Bad request"

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail or self.detail)
        if detail:
            self.detail = detail


class AuthenticationError(NovaError):
    status_code = 401
    detail = "Invalid credentials"


class PermissionDeniedError(NovaError):
    status_code = 403
    detail = "Permission denied"


class NotFoundError(NovaError):
    status_code = 404
    detail = "Not found"


class ConflictError(NovaError):
    status_code = 409
    detail = "Conflict"
