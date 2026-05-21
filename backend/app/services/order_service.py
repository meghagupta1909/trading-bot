"""
Order service — orchestrates validation, Binance client calls,
and structured response assembly. This is the single source of truth
for all order-related business logic.
"""
from __future__ import annotations

import json
from decimal import Decimal
from typing import Optional

from app.core.exceptions import BinanceAPIError, ValidationError
from app.core.logging_config import get_logger
from app.models.schemas import OrderType
from app.services.binance_client import BinanceClient
from app.validators.order_validator import validate_place_order_inputs

logger = get_logger("orders")


def _build_request_summary(validated: dict) -> dict:
    """Human-readable summary of the validated order inputs."""
    return {
        "symbol": validated["symbol"],
        "side": validated["side"],
        "type": validated["order_type"],
        "quantity": str(validated["quantity"]),
        "price": str(validated["price"]) if validated.get("price") else "N/A",
        "stop_price": str(validated["stop_price"]) if validated.get("stop_price") else "N/A",
    }


def _build_binance_params(validated: dict, time_in_force: str, reduce_only: bool) -> dict:
    """
    Map validated inputs to the exact Binance Futures API parameter names.
    Reference: https://binance-docs.github.io/apidocs/futures/en/#new-order-trade
    """
    order_type = validated["order_type"]

    # Map our friendly name to Binance's enum
    binance_type_map = {
        "MARKET": "MARKET",
        "LIMIT": "LIMIT",
        "STOP_LIMIT": "STOP_MARKET",
    }

    params: dict = {
        "symbol": validated["symbol"],
        "side": validated["side"],
        "type": binance_type_map[order_type],
        "quantity": str(validated["quantity"]),
    }

    if order_type == "LIMIT":
        params["price"] = str(validated["price"])
        params["timeInForce"] = time_in_force

    elif order_type == "STOP_LIMIT":
        params["stopPrice"] = str(validated["stop_price"])
        # STOP_MARKET with a price behaves as stop-limit on futures
        params["price"] = str(validated["price"])
        params["timeInForce"] = time_in_force

    if reduce_only:
        params["reduceOnly"] = "true"

    return params


def _format_order_response(raw: dict) -> dict:
    """Flatten/rename keys for a clean, predictable response structure."""
    return {
        "orderId": raw.get("orderId"),
        "clientOrderId": raw.get("clientOrderId"),
        "symbol": raw.get("symbol"),
        "side": raw.get("side"),
        "type": raw.get("type"),
        "status": raw.get("status"),
        "origQty": raw.get("origQty"),
        "executedQty": raw.get("executedQty"),
        "avgPrice": raw.get("avgPrice"),
        "price": raw.get("price"),
        "stopPrice": raw.get("stopPrice"),
        "timeInForce": raw.get("timeInForce"),
        "updateTime": raw.get("updateTime"),
        "cumQuote": raw.get("cumQuote"),
        "reduceOnly": raw.get("reduceOnly"),
        "closePosition": raw.get("closePosition"),
    }


async def place_order(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float | Decimal,
    price: Optional[str | float | Decimal] = None,
    stop_price: Optional[str | float | Decimal] = None,
    time_in_force: str = "GTC",
    reduce_only: bool = False,
    client: Optional[BinanceClient] = None,
) -> dict:
    """
    Validate inputs, build Binance params, dispatch the order,
    and return a structured result dict.

    Returns:
        {
            "success": bool,
            "message": str,
            "request_summary": dict,
            "order": dict | None,
            "error": str | None,
        }
    """
    logger.info(
        "place_order called — symbol=%s side=%s type=%s qty=%s price=%s stop=%s",
        symbol, side, order_type, quantity, price, stop_price,
    )

    # ── Validate inputs ────────────────────────────────────────────────────────
    try:
        validated = validate_place_order_inputs(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except ValidationError as exc:
        logger.warning("Validation failed: %s", exc.message)
        return {
            "success": False,
            "message": "Validation failed",
            "request_summary": {
                "symbol": symbol, "side": side, "type": order_type,
                "quantity": str(quantity), "price": str(price) if price else "N/A",
            },
            "order": None,
            "error": exc.message,
        }

    request_summary = _build_request_summary(validated)
    binance_params = _build_binance_params(validated, time_in_force, reduce_only)

    logger.info("Request summary: %s", json.dumps(request_summary))
    logger.info("Binance params (unsigned): %s", json.dumps(binance_params))

    # ── Call Binance API ───────────────────────────────────────────────────────
    should_close_client = client is None
    if client is None:
        client = BinanceClient()

    try:
        if should_close_client:
            async with client:
                raw_response = await client.place_order(binance_params)
        else:
            raw_response = await client.place_order(binance_params)

        order = _format_order_response(raw_response)

        logger.info(
            "Order placed successfully — orderId=%s status=%s executedQty=%s avgPrice=%s",
            order.get("orderId"),
            order.get("status"),
            order.get("executedQty"),
            order.get("avgPrice"),
        )

        return {
            "success": True,
            "message": f"Order placed successfully [orderId={order.get('orderId')}]",
            "request_summary": request_summary,
            "order": order,
            "error": None,
        }

    except BinanceAPIError as exc:
        logger.error(
            "Binance API error placing order — %s | details=%s",
            exc.message, exc.details,
        )
        return {
            "success": False,
            "message": "Order placement failed",
            "request_summary": request_summary,
            "order": None,
            "error": exc.message,
        }
    except Exception as exc:
        logger.exception("Unexpected error placing order: %s", exc)
        return {
            "success": False,
            "message": "Unexpected error",
            "request_summary": request_summary,
            "order": None,
            "error": str(exc),
        }


async def check_connectivity() -> dict:
    """Ping Binance API and return connectivity status."""
    async with BinanceClient() as client:
        try:
            await client.ping()
            server_time = await client.get_server_time()
            return {
                "connected": True,
                "server_time": server_time.get("serverTime"),
            }
        except Exception as exc:
            logger.warning("Binance connectivity check failed: %s", exc)
            return {"connected": False, "error": str(exc)}