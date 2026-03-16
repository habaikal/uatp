from dataclasses import dataclass
from typing import Optional, Literal


OrderSide = Literal["BUY", "SELL"]
OrderType = Literal["MARKET", "LIMIT"]
TimeInForce = Literal["GTC", "IOC", "FOK"]


@dataclass
class Order:
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType = "MARKET"
    price: Optional[float] = None
    time_in_force: TimeInForce = "GTC"
    client_order_id: Optional[str] = None
    notional: Optional[float] = None


@dataclass
class ExecutionReport:
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    status: Literal["FILLED", "PARTIALLY_FILLED", "REJECTED"]
    reason: Optional[str] = None

