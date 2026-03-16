from typing import Any, Dict, List

from pydantic import BaseModel


class Strategy(BaseModel):
    params: Dict[str, Any]


class PortfolioItem(BaseModel):
    strategy: Dict[str, Any]
    weight: float


class PortfolioState(BaseModel):
    equity: float
    day_pnl: float
    positions: Dict[str, Dict[str, float]]
    leverage: float


class DemoRunResponse(BaseModel):
    executed_orders: int
    state: PortfolioState
    portfolio: List[PortfolioItem]


class EquityPoint(BaseModel):
    t: int
    equity: float


class RiskSnapshot(BaseModel):
    equity: float
    day_pnl: float
    max_daily_loss: float
    max_leverage: float
    current_leverage: float

