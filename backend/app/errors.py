"""Centralized API error helpers and FastAPI exception handlers."""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.errors import ErrorResponse

logger = logging.getLogger(__name__)

DEFAULT_ERROR_CODES: dict[int, str] = {
    400: "bad_request",
    404: "not_found",
    422: "validation_error",
    500: "internal_error",
    503: "service_unavailable",
}


def error_response(
    status_code: int,
    code: str,
    message: str,
    detail: str | None = None,
) -> JSONResponse:
    body = ErrorResponse(code=code, message=message, detail=detail)
    return JSONResponse(status_code=status_code, content=body.model_dump(exclude_none=True))


def raise_api_error(
    status_code: int,
    code: str,
    message: str,
    detail: str | None = None,
) -> None:
    """Raise an HTTPException whose detail is normalized by the global handler."""
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message, "detail": detail},
    )


def _normalize_http_detail(detail: object, status_code: int) -> tuple[str, str, str | None]:
    if isinstance(detail, dict):
        code = str(detail.get("code") or DEFAULT_ERROR_CODES.get(status_code, "http_error"))
        message = str(detail.get("message") or "Request failed")
        raw_detail = detail.get("detail")
        normalized_detail = str(raw_detail) if raw_detail is not None else None
        return code, message, normalized_detail

    if isinstance(detail, str):
        code = DEFAULT_ERROR_CODES.get(status_code, "http_error")
        return code, detail, None

    code = DEFAULT_ERROR_CODES.get(status_code, "http_error")
    return code, "Request failed", None


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code, message, detail = _normalize_http_detail(exc.detail, exc.status_code)
        return error_response(exc.status_code, code, message, detail)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return error_response(
            422,
            "validation_error",
            "Request validation failed",
            detail=str(exc.errors()),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s", request.url.path)
        return error_response(
            500,
            "internal_error",
            "An unexpected server error occurred",
        )
