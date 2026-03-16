class UATPError(Exception):
    """Base exception for the Ultimate AI Trading Platform."""


class RiskLimitExceeded(UATPError):
    """Raised when a risk limit is violated."""


class OrderRejected(UATPError):
    """Raised when an order fails risk checks or broker validation."""


class MarketDataError(UATPError):
    """Raised when market data is missing or invalid."""


class ExecutionError(UATPError):
    """Raised when there is a problem during order execution."""

