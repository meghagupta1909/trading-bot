"""
Orders API router.
POST /api/orders/place  — place a new order
"""
from __future__ import annotations

from fastapi import APIRouter

from app.core.logging_config import get_logger
from app.models.schemas import PlaceOrderRequest, PlaceOrderResponse
from app.services.order_service import place_order

logger = get_logger(__name__)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "/place",
    response_model=PlaceOrderResponse,
    summary="Place a Futures Order",
    description=(
        "Place a **MARKET**, **LIMIT**, or **STOP_LIMIT** order on Binance Futures Testnet. "
        "Both BUY and SELL sides are supported. Price is required for LIMIT/STOP_LIMIT orders."
    ),
    responses={
        200: {"description": "Order processed (check `success` field for result)"},
        422: {"description": "Validation error in request body"},
        401: {"description": "Invalid API credentials"},
        503: {"description": "Binance API unreachable"},
    },
)
async def place_order_endpoint(request: PlaceOrderRequest) -> PlaceOrderResponse:
    logger.info(
        "POST /orders/place — symbol=%s side=%s type=%s qty=%s",
        request.symbol,
        request.side,
        request.order_type,
        request.quantity,
    )

    result = await place_order(
        symbol=request.symbol,
        side=request.side.value,
        order_type=request.order_type.value.replace("STOP_MARKET", "STOP_LIMIT"),
        quantity=request.quantity,
        price=request.price,
        stop_price=request.stop_price,
        time_in_force=request.time_in_force.value,
        reduce_only=request.reduce_only,
    )

    return PlaceOrderResponse(**result)