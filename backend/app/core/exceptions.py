"""
Centralised custom exceptions for the trading bot.
"""


class TradingBotError(Exception):
    """Base exception for all trading bot errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(TradingBotError):
    """Raised when user input fails validation."""


class BinanceAPIError(TradingBotError):
    """Raised when Binance API returns an error response."""

    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(message, details)
        self.status_code = status_code


class BinanceNetworkError(TradingBotError):
    """Raised on network/connectivity failures."""


class BinanceAuthError(TradingBotError):
    """Raised when API credentials are invalid or missing."""


class OrderNotFoundError(TradingBotError):
    """Raised when a requested order cannot be found."""


class ConfigurationError(TradingBotError):
    """Raised when app configuration is invalid or incomplete."""