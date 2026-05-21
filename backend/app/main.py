"""
FastAPI application entry point.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.api.exception_handlers import (
    generic_exception_handler,
    request_validation_exception_handler,
    trading_bot_exception_handler,
)
from app.core.config import settings
from app.core.exceptions import TradingBotError
from app.core.logging_config import get_logger, setup_logging

# Initialise logging before anything else
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "🚀 %s v%s starting up — debug=%s",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.DEBUG,
    )
    yield
    logger.info("🛑 %s shutting down", settings.APP_NAME)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "## Binance Futures Testnet Trading Bot\n\n"
            "Place **MARKET**, **LIMIT**, and **STOP_LIMIT** orders on Binance Futures Testnet "
            "(USDT-M) via a clean REST API with full validation, structured logging, and error handling.\n\n"
            "### Quick Start\n"
            "1. Set `BINANCE_API_KEY` and `BINANCE_SECRET_KEY` in `.env`\n"
            "2. `POST /api/orders/place` with your order parameters\n"
            "3. Check `/api/health` for connectivity status\n"
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ───────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception handlers ─────────────────────────────────────────────────────
    app.add_exception_handler(TradingBotError, trading_bot_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # ── Routers ────────────────────────────────────────────────────────────────
    app.include_router(api_router)

    # ── Root redirect ──────────────────────────────────────────────────────────
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/api/health",
        }

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )