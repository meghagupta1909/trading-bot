"""Integration tests for the FastAPI endpoints."""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self):
        with patch(
            "app.api.health.check_connectivity",
            new_callable=AsyncMock,
            return_value={"connected": True, "server_time": 1700000000000},
        ):
            resp = client.get("/api/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["binance_connected"] is True
            assert data["status"] == "ok"

    def test_health_degraded_when_disconnected(self):
        with patch(
            "app.api.health.check_connectivity",
            new_callable=AsyncMock,
            return_value={"connected": False, "error": "timeout"},
        ):
            resp = client.get("/api/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["binance_connected"] is False
            assert data["status"] == "degraded"


class TestPlaceOrderEndpoint:
    def test_market_order_success(self):
        mock_result = {
            "success": True,
            "message": "Order placed successfully [orderId=12345]",
            "request_summary": {
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "MARKET",
                "quantity": "0.01",
                "price": "N/A",
                "stop_price": "N/A",
            },
            "order": {
                "orderId": 12345,
                "clientOrderId": "test123",
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "MARKET",
                "status": "FILLED",
                "origQty": "0.01",
                "executedQty": "0.01",
                "avgPrice": "65000.00",
                "price": "0",
                "stopPrice": None,
                "timeInForce": "GTC",
                "updateTime": 1700000000000,
                "cumQuote": "650.00",
                "reduceOnly": False,
                "closePosition": False,
            },
            "error": None,
        }

        with patch(
            "app.api.orders.place_order",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            resp = client.post(
                "/api/orders/place",
                json={
                    "symbol": "BTCUSDT",
                    "side": "BUY",
                    "type": "MARKET",
                    "quantity": "0.01",
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert data["order"]["orderId"] == 12345

    def test_limit_order_missing_price_returns_422(self):
        resp = client.post(
            "/api/orders/place",
            json={
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "LIMIT",
                "quantity": "0.01",
                # price intentionally omitted
            },
        )
        assert resp.status_code == 422

    def test_invalid_side_returns_422(self):
        resp = client.post(
            "/api/orders/place",
            json={
                "symbol": "BTCUSDT",
                "side": "LONG",  # invalid
                "type": "MARKET",
                "quantity": "0.01",
            },
        )
        assert resp.status_code == 422

    def test_negative_quantity_returns_422(self):
        resp = client.post(
            "/api/orders/place",
            json={
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "MARKET",
                "quantity": "-1",
            },
        )
        assert resp.status_code == 422


class TestLogsEndpoint:
    def test_recent_logs_returns_200(self):
        with patch(
            "app.api.health.read_recent_logs",
            return_value={"lines": ["log line 1", "log line 2"], "log_file": "trading_bot.log", "total_lines": 2},
        ):
            resp = client.get("/api/logs/recent")
            assert resp.status_code == 200
            data = resp.json()
            assert "lines" in data