"""
Low-level Binance Futures REST client.
Handles authentication (HMAC-SHA256 signatures), request dispatch,
and raw error handling. All business logic lives in the service layer.
"""
from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any, Optional
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.core.exceptions import (
    BinanceAPIError,
    BinanceAuthError,
    BinanceNetworkError,
    ConfigurationError,
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class BinanceClient:
    """
    Async Binance Futures Testnet REST client.

    Usage:
        async with BinanceClient() as client:
            data = await client.get("/fapi/v1/ping")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 15.0,
    ):
        self.api_key = api_key or settings.BINANCE_API_KEY
        self.secret_key = secret_key or settings.BINANCE_SECRET_KEY
        self.base_url = (base_url or settings.BINANCE_BASE_URL).rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

        logger.debug("BinanceClient initialised — base_url=%s", self.base_url)

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    async def __aenter__(self) -> "BinanceClient":
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"X-MBX-APIKEY": self.api_key},
        )
        return self

    async def __aexit__(self, *_) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={"X-MBX-APIKEY": self.api_key},
            )
        return self._client

    # ── Signing ────────────────────────────────────────────────────────────────

    def _sign(self, params: dict) -> dict:
        """Add timestamp + HMAC-SHA256 signature to params."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    # ── HTTP helpers ───────────────────────────────────────────────────────────

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        signed: bool = False,
    ) -> Any:
        client = await self._ensure_client()
        params = params or {}
        data = data or {}

        if signed:
            if method.upper() in ("GET", "DELETE"):
                params = self._sign(params)
            else:
                data = self._sign(data)

        logger.debug(
            "→ %s %s | params=%s | body=%s",
            method.upper(),
            path,
            {k: v for k, v in params.items() if k not in ("signature",)},
            {k: v for k, v in data.items() if k not in ("signature",)},
        )

        try:
            response = await client.request(
                method,
                path,
                params=params if params else None,
                data=data if data else None,
            )
        except httpx.ConnectError as exc:
            logger.error("Network connect error: %s", exc)
            raise BinanceNetworkError(
                f"Cannot connect to Binance API at {self.base_url}. "
                "Check your internet connection."
            ) from exc
        except httpx.TimeoutException as exc:
            logger.error("Request timed out: %s", exc)
            raise BinanceNetworkError(
                "Binance API request timed out. Please try again."
            ) from exc
        except httpx.HTTPError as exc:
            logger.error("HTTP error: %s", exc)
            raise BinanceNetworkError(f"HTTP error: {exc}") from exc

        logger.debug("← %s %s | status=%s", method.upper(), path, response.status_code)

        return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> Any:
        """Parse JSON and raise appropriate exceptions for non-2xx responses."""
        try:
            payload = response.json()
        except Exception:
            payload = {"msg": response.text, "code": response.status_code}

        if response.status_code == 401:
            logger.error("Authentication failure: %s", payload)
            raise BinanceAuthError(
                "Invalid API credentials. Check BINANCE_API_KEY and BINANCE_SECRET_KEY.",
                details=payload,
            )

        if not response.is_success:
            code = payload.get("code", response.status_code)
            msg = payload.get("msg", "Unknown Binance API error")
            logger.error(
                "Binance API error %s: %s | full_response=%s",
                code,
                msg,
                payload,
            )
            raise BinanceAPIError(
                message=f"Binance API error [{code}]: {msg}",
                status_code=response.status_code,
                details=payload,
            )

        logger.debug("Response payload: %s", payload)
        return payload

    # ── Public endpoints ───────────────────────────────────────────────────────

    async def ping(self) -> dict:
        """Test connectivity."""
        return await self._request("GET", "/fapi/v1/ping")

    async def get_server_time(self) -> dict:
        """Get Binance server time."""
        return await self._request("GET", "/fapi/v1/time")

    async def get_exchange_info(self) -> dict:
        """Get exchange trading rules and symbol info."""
        return await self._request("GET", "/fapi/v1/exchangeInfo")

    async def get_ticker_price(self, symbol: str) -> dict:
        """Get latest price for a symbol."""
        return await self._request("GET", "/fapi/v1/ticker/price", params={"symbol": symbol})

    # ── Private endpoints (signed) ─────────────────────────────────────────────

    async def get_account(self) -> dict:
        """Get account information including balances."""
        return await self._request("GET", "/fapi/v2/account", signed=True)

    async def place_order(self, order_params: dict) -> dict:
        """Place a new futures order."""
        logger.info("Placing order — params=%s", {k: v for k, v in order_params.items()})
        return await self._request("POST", "/fapi/v1/order", data=order_params, signed=True)

    async def get_order(self, symbol: str, order_id: int) -> dict:
        """Query an existing order by ID."""
        return await self._request(
            "GET",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id},
            signed=True,
        )

    async def cancel_order(self, symbol: str, order_id: int) -> dict:
        """Cancel an active order."""
        return await self._request(
            "DELETE",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id},
            signed=True,
        )

    async def get_open_orders(self, symbol: Optional[str] = None) -> list[dict]:
        """Get all open orders, optionally filtered by symbol."""
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/fapi/v1/openOrders", params=params, signed=True)

    def _validate_credentials(self) -> None:
        """Raise ConfigurationError if credentials are missing."""
        if not self.api_key or not self.secret_key:
            raise ConfigurationError(
                "BINANCE_API_KEY and BINANCE_SECRET_KEY must be set in .env"
            )