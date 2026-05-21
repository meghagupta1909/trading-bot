"""
Centralised FastAPI exception handlers.
Maps domain exceptions → HTTP responses with consistent JSON shape.
"""
from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import (
    BinanceAPIError,
    BinanceAuthError,
    BinanceNetworkError,
    ConfigurationError,
    TradingBotError,
    ValidationError,
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def _error_body(status: int, error: str, message: str, details: dict | None = None) -> dict:
    return {"status": status, "error": error, "message": message, "details": details or {}}


async def trading_bot_exception_handler(request: Request, exc: TradingBotError) -> JSONResponse:
    if isinstance(exc, BinanceAuthError):
        logger.error("Auth error on %s: %s", request.url, exc.message)
        return JSONResponse(
            status_code=401,
            content=_error_body(401, "AuthenticationError", exc.message, exc.details),
        )

    if isinstance(exc, BinanceNetworkError):
        logger.error("Network error on %s: %s", request.url, exc.message)
        return JSONResponse(
            status_code=503,
            content=_error_body(503, "NetworkError", exc.message),
        )

    if isinstance(exc, BinanceAPIError):
        logger.error("Binance API error on %s: %s", request.url, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.status_code, "BinanceAPIError", exc.message, exc.details),
        )

    if isinstance(exc, ValidationError):
        logger.warning("Validation error on %s: %s", request.url, exc.message)
        return JSONResponse(
            status_code=422,
            content=_error_body(422, "ValidationError", exc.message),
        )

    if isinstance(exc, ConfigurationError):
        logger.critical("Config error on %s: %s", request.url, exc.message)
        return JSONResponse(
            status_code=500,
            content=_error_body(500, "ConfigurationError", exc.message),
        )

    # Generic TradingBotError
    logger.error("Unhandled TradingBotError on %s: %s", request.url, exc.message)
    return JSONResponse(
        status_code=500,
        content=_error_body(500, "InternalError", exc.message),
    )


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = []
    for err in exc.errors():
        loc = " → ".join(str(x) for x in err.get("loc", []))
        errors.append({"field": loc, "message": err.get("msg"), "type": err.get("type")})

    logger.warning("Request validation failed on %s: %s", request.url, errors)
    return JSONResponse(
        status_code=422,
        content=_error_body(
            422,
            "RequestValidationError",
            "Request body validation failed",
            {"errors": errors},
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s", request.url)
    return JSONResponse(
        status_code=500,
        content=_error_body(500, "InternalServerError", "An unexpected error occurred."),
    )