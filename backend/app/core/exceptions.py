"""
Custom exception classes and global exception handlers for FastAPI.
All API errors follow the standard error response format.
"""

from __future__ import annotations

from typing import Optional, List

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class AppException(Exception):
    """Base application exception with standard error response structure."""

    def __init__(
        self,
        status_code: int = 400,
        message: str = "An error occurred",
        errors: Optional[List] = None,
    ):
        self.status_code = status_code
        self.message = message
        self.errors = errors or []
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(status_code=404, message=message)


class BadRequestException(AppException):
    """Bad request from client."""

    def __init__(self, message: str = "Invalid request", errors: Optional[List] = None):
        super().__init__(status_code=400, message=message, errors=errors)


class UnauthorizedException(AppException):
    """Authentication required or failed (Phase 2)."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(status_code=401, message=message)


class ForbiddenException(AppException):
    """Insufficient permissions (Phase 2)."""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(status_code=403, message=message)


# ── Exception Handlers ──────────────────────────────────────


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global exception handlers to the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "statusCode": exc.status_code,
                "message": exc.message,
                "errors": exc.errors,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "statusCode": exc.status_code,
                "message": exc.detail,
                "errors": [],
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ):
        errors = [
            {
                "field": ".".join(str(loc) for loc in err.get("loc", [])),
                "message": err.get("msg", "Validation error"),
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "statusCode": 422,
                "message": "Validation error",
                "errors": errors,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, _exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "statusCode": 500,
                "message": "Internal server error",
                "errors": [],
            },
        )
