"""
Health-check and log viewer endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.core.config import settings
from app.core.logging_config import get_logger
from app.models.schemas import HealthResponse, RecentLogsResponse
from app.services.order_service import check_connectivity
from app.utils.log_utils import list_log_files, read_recent_logs

logger = get_logger(__name__)

router = APIRouter(tags=["System"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns app version, Binance connectivity status.",
)
async def health_check() -> HealthResponse:
    connectivity = await check_connectivity()
    connected = connectivity.get("connected", False)
    return HealthResponse(
        status="ok" if connected else "degraded",
        version=settings.APP_VERSION,
        binance_connected=connected,
        message=(
            "All systems operational"
            if connected
            else f"Binance unreachable: {connectivity.get('error', 'unknown')}"
        ),
    )


@router.get(
    "/logs/recent",
    response_model=RecentLogsResponse,
    summary="Recent Logs",
    description="Return the last N lines from a log file (default: trading_bot.log).",
)
async def recent_logs(
    log_file: str = Query("trading_bot.log", description="Log filename"),
    lines: int = Query(100, ge=1, le=1000, description="Number of tail lines to return"),
) -> RecentLogsResponse:
    data = read_recent_logs(log_file=log_file, lines=lines)
    return RecentLogsResponse(**data)


@router.get(
    "/logs/files",
    summary="List Log Files",
    description="List all available log files.",
)
async def list_logs() -> dict:
    return {"files": list_log_files()}