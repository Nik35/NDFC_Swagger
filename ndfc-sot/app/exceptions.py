"""Application-wide exception classes and FastAPI error handlers."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------

class AppError(Exception):
    """Base application error."""

    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
    ) -> None:
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(detail)


class NotFoundError(AppError):
    """Resource not found (404)."""

    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND") -> None:
        super().__init__(detail=detail, status_code=404, error_code=error_code)


class ConflictError(AppError):
    """Duplicate / conflict (409)."""

    def __init__(self, detail: str = "Resource already exists") -> None:
        super().__init__(detail=detail, status_code=409, error_code="ALREADY_EXISTS")


class ValidationError(AppError):
    """Validation failure (422)."""

    def __init__(self, detail: str = "Validation error") -> None:
        super().__init__(detail=detail, status_code=422, error_code="VALIDATION_ERROR")


class DependencyError(AppError):
    """Referential / dependency failure (409)."""

    def __init__(self, detail: str = "Dependency error") -> None:
        super().__init__(detail=detail, status_code=409, error_code="DEPENDENCY_ERROR")


class DeploymentError(AppError):
    """Deployment / Ansible execution error (500)."""

    def __init__(self, detail: str = "Deployment failed") -> None:
        super().__init__(detail=detail, status_code=500, error_code="INTERNAL_ERROR")


# ---------------------------------------------------------------------------
# FastAPI exception handlers
# ---------------------------------------------------------------------------

def register_exception_handlers(app: FastAPI) -> None:
    """Register global handlers that return the standard error envelope."""

    @app.exception_handler(AppError)
    async def _app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "error_code": exc.error_code},
        )
