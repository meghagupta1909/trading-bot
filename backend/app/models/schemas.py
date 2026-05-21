"""
Pydantic schemas for request/response validation.
"""
from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


# ── Enums ─────────────────────────────────────────────────────────────────────

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LIMIT = "STOP_MARKET"   # Binance futures uses STOP_MARKET for stop-limit


class OrderStatus(str, Enum):
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class TimeInForce(str, Enum):
    GTC = "GTC"   # Good Till Cancel
    IOC = "IOC"   # Immediate or Cancel
    FOK = "FOK"   # Fill or Kill
    GTX = "GTX"   # Good Till Crossing (Post Only)


# ── Request schemas ────────────────────────────────────────────────────────────

class PlaceOrderRequest(BaseModel):
    symbol: str = Field(
        ...,
        min_length=2,
        max_length=20,
        description="Trading pair symbol e.g. BTCUSDT",
        examples=["BTCUSDT"],
    )
    side: OrderSide = Field(..., description="BUY or SELL")
    order_type: OrderType = Field(..., alias="type", description="MARKET, LIMIT, or STOP_LIMIT")
    quantity: Decimal = Field(..., gt=0, description="Order quantity (must be > 0)")
    price: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Required for LIMIT and STOP_LIMIT orders",
    )
    stop_price: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Required for STOP_LIMIT orders — trigger price",
    )
    time_in_force: TimeInForce = Field(
        TimeInForce.GTC,
        description="Time in force policy (default GTC)",
    )
    reduce_only: bool = Field(False, description="Reduce existing position only")

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def validate_order_constraints(self) -> "PlaceOrderRequest":
        # Normalise symbol
        self.symbol = self.symbol.upper().strip()

        # Price required for LIMIT
        if self.order_type == OrderType.LIMIT and self.price is None:
            raise ValueError("price is required for LIMIT orders")

        # Both price + stop_price required for STOP_LIMIT
        if self.order_type == OrderType.STOP_LIMIT:
            if self.price is None:
                raise ValueError("price is required for STOP_LIMIT orders")
            if self.stop_price is None:
                raise ValueError("stop_price is required for STOP_LIMIT orders")

        return self


# ── Response schemas ───────────────────────────────────────────────────────────

class OrderResponse(BaseModel):
    order_id: int = Field(..., description="Binance order ID")
    client_order_id: str
    symbol: str
    side: str
    order_type: str = Field(..., alias="type")
    status: str
    quantity: str = Field(..., alias="origQty")
    executed_qty: str = Field(..., alias="executedQty")
    avg_price: Optional[str] = Field(None, alias="avgPrice")
    price: Optional[str] = None
    stop_price: Optional[str] = Field(None, alias="stopPrice")
    time_in_force: Optional[str] = Field(None, alias="timeInForce")
    created_at: Optional[int] = Field(None, alias="updateTime")

    model_config = {"populate_by_name": True}


class PlaceOrderResponse(BaseModel):
    success: bool
    message: str
    request_summary: dict
    order: Optional[dict] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    binance_connected: bool
    message: str


class RecentLogsResponse(BaseModel):
    lines: list[str]
    log_file: str
    total_lines: int