"""Tests for input validators."""
import pytest
from decimal import Decimal
from app.core.exceptions import ValidationError
from app.validators.order_validator import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_place_order_inputs,
)


class TestValidateSymbol:
    def test_valid_symbol(self):
        assert validate_symbol("btcusdt") == "BTCUSDT"

    def test_strips_whitespace(self):
        assert validate_symbol("  ETHUSDT  ") == "ETHUSDT"

    def test_invalid_symbol_special_chars(self):
        with pytest.raises(ValidationError):
            validate_symbol("BTC-USDT")

    def test_too_short(self):
        with pytest.raises(ValidationError):
            validate_symbol("B")


class TestValidateSide:
    def test_buy(self):
        assert validate_side("buy") == "BUY"

    def test_sell(self):
        assert validate_side("SELL") == "SELL"

    def test_invalid(self):
        with pytest.raises(ValidationError):
            validate_side("LONG")


class TestValidateOrderType:
    def test_market(self):
        assert validate_order_type("market") == "MARKET"

    def test_limit(self):
        assert validate_order_type("LIMIT") == "LIMIT"

    def test_stop_limit(self):
        assert validate_order_type("stop_limit") == "STOP_LIMIT"

    def test_invalid(self):
        with pytest.raises(ValidationError):
            validate_order_type("TWAP")


class TestValidateQuantity:
    def test_valid_decimal(self):
        assert validate_quantity("0.01") == Decimal("0.01")

    def test_valid_int(self):
        assert validate_quantity(5) == Decimal("5")

    def test_zero_raises(self):
        with pytest.raises(ValidationError):
            validate_quantity(0)

    def test_negative_raises(self):
        with pytest.raises(ValidationError):
            validate_quantity(-1)

    def test_string_garbage_raises(self):
        with pytest.raises(ValidationError):
            validate_quantity("abc")


class TestValidatePrice:
    def test_none_not_required(self):
        assert validate_price(None) is None

    def test_none_required_raises(self):
        with pytest.raises(ValidationError):
            validate_price(None, required=True)

    def test_valid_price(self):
        assert validate_price("65000") == Decimal("65000")

    def test_negative_raises(self):
        with pytest.raises(ValidationError):
            validate_price(-100)


class TestValidatePlaceOrderInputs:
    def test_market_order(self):
        result = validate_place_order_inputs("BTCUSDT", "BUY", "MARKET", "0.01")
        assert result["symbol"] == "BTCUSDT"
        assert result["side"] == "BUY"
        assert result["order_type"] == "MARKET"
        assert result["quantity"] == Decimal("0.01")
        assert result["price"] is None

    def test_limit_requires_price(self):
        with pytest.raises(ValidationError, match="is required for this order type"):
            validate_place_order_inputs("BTCUSDT", "BUY", "LIMIT", "0.01")

    def test_limit_with_price_ok(self):
        result = validate_place_order_inputs("BTCUSDT", "BUY", "LIMIT", "0.01", price="65000")
        assert result["price"] == Decimal("65000")

    def test_stop_limit_requires_both_prices(self):
        with pytest.raises(ValidationError):
            validate_place_order_inputs(
                "BTCUSDT", "BUY", "STOP_LIMIT", "0.01", price="65000"
            )

    def test_stop_limit_full(self):
        result = validate_place_order_inputs(
            "BTCUSDT", "BUY", "STOP_LIMIT", "0.01",
            price="65000", stop_price="64500"
        )
        assert result["stop_price"] == Decimal("64500")