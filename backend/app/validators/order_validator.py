"""
Input validation helpers used by both CLI and API layers.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Optional

from app.core.exceptions import ValidationError
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Binance futures symbols are uppercase alphanumeric (e.g. BTCUSDT, ETHUSDT)
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{2,20}$")
VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}


def validate_symbol(symbol: str) -> str:
    """Return normalised symbol or raise ValidationError."""
    symbol = symbol.upper().strip()
    if not SYMBOL_PATTERN.match(symbol):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Must be uppercase alphanumeric, 2-20 chars (e.g. BTCUSDT)."
        )
    logger.debug("Symbol validated: %s", symbol)
    return symbol


def validate_side(side: str) -> str:
    """Return normalised side or raise ValidationError."""
    side = side.upper().strip()
    if side not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )
    logger.debug("Side validated: %s", side)
    return side


def validate_order_type(order_type: str) -> str:
    """Return normalised order type or raise ValidationError."""
    order_type = order_type.upper().strip()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    logger.debug("Order type validated: %s", order_type)
    return order_type


def validate_quantity(quantity: str | float | Decimal) -> Decimal:
    """Return Decimal quantity or raise ValidationError."""
    try:
        qty = Decimal(str(quantity))
    except (InvalidOperation, ValueError):
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a positive number.")

    if qty <= 0:
        raise ValidationError(f"Quantity must be greater than 0, got {qty}.")

    logger.debug("Quantity validated: %s", qty)
    return qty


def validate_price(
    price: Optional[str | float | Decimal],
    *,
    required: bool = False,
    label: str = "price",
) -> Optional[Decimal]:
    """Return Decimal price or raise ValidationError."""
    if price is None:
        if required:
            raise ValidationError(f"'{label}' is required for this order type.")
        return None

    try:
        p = Decimal(str(price))
    except (InvalidOperation, ValueError):
        raise ValidationError(f"Invalid {label} '{price}'. Must be a positive number.")

    if p <= 0:
        raise ValidationError(f"'{label}' must be greater than 0, got {p}.")

    logger.debug("%s validated: %s", label, p)
    return p


def validate_place_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float | Decimal,
    price: Optional[str | float | Decimal] = None,
    stop_price: Optional[str | float | Decimal] = None,
) -> dict:
    """
    Validate all order placement inputs in one call.
    Returns a dict of validated/normalised values.
    Raises ValidationError on the first failure.
    """
    validated_symbol = validate_symbol(symbol)
    validated_side = validate_side(side)
    validated_type = validate_order_type(order_type)
    validated_qty = validate_quantity(quantity)

    price_required = validated_type in {"LIMIT", "STOP_LIMIT"}
    stop_price_required = validated_type == "STOP_LIMIT"

    validated_price = validate_price(price, required=price_required, label="price")
    validated_stop_price = validate_price(
        stop_price, required=stop_price_required, label="stop_price"
    )

    logger.info(
        "All inputs validated — symbol=%s side=%s type=%s qty=%s price=%s stop_price=%s",
        validated_symbol,
        validated_side,
        validated_type,
        validated_qty,
        validated_price,
        validated_stop_price,
    )

    return {
        "symbol": validated_symbol,
        "side": validated_side,
        "order_type": validated_type,
        "quantity": validated_qty,
        "price": validated_price,
        "stop_price": validated_stop_price,
    }