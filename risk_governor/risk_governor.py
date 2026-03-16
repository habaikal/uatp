
import numpy as np
from typing import Iterable, List, Dict, Any, Tuple

from core.config import Config
from core.exceptions import RiskLimitExceeded
from core.logging_utils import get_logger


class RiskGovernor:
    def __init__(self) -> None:
        self._cfg = Config.load()
        self._logger = get_logger("uatp.risk")

    def max_drawdown(self, returns: Iterable[float]) -> float:
        arr = np.asarray(list(returns), dtype=float)
        if arr.size == 0:
            return 0.0
        cumulative = np.cumsum(arr)
        peak = np.maximum.accumulate(cumulative)
        drawdown = cumulative - peak
        return float(drawdown.min())

    def realized_volatility(self, returns: Iterable[float]) -> float:
        arr = np.asarray(list(returns), dtype=float)
        if arr.size == 0:
            return 0.0
        return float(np.std(arr, ddof=1))

    def position_limit(self, equity: float, risk_per_trade: float | None = None) -> float:
        if risk_per_trade is None:
            cfg_risk = self._cfg.get("risk.risk_per_trade_pct", 0.01)
            risk_per_trade = float(cfg_risk)
        return equity * risk_per_trade

    def max_symbol_exposure(self, equity: float) -> float:
        pct = float(self._cfg.get("risk.max_symbol_exposure_pct", 0.1))
        return equity * pct

    def max_daily_loss(self, equity: float) -> float:
        pct = float(self._cfg.get("risk.max_daily_loss_pct", 0.03))
        return equity * pct

    def max_leverage(self) -> float:
        return float(self._cfg.get("risk.max_leverage", 3.0))

    def validate_orders(
        self,
        portfolio_state: Dict[str, Any],
        candidate_orders: List[Dict[str, Any]],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Validate a list of candidate orders against risk limits.

        portfolio_state:
            {
              "equity": float,
              "day_pnl": float,
              "positions": {symbol: {"qty": float, "value": float}},
              "leverage": float
            }
        """
        equity = float(portfolio_state.get("equity", 0.0))
        day_pnl = float(portfolio_state.get("day_pnl", 0.0))
        current_leverage = float(portfolio_state.get("leverage", 1.0))
        positions = portfolio_state.get("positions", {}) or {}

        max_daily_loss = self.max_daily_loss(equity)
        max_symbol_exp = self.max_symbol_exposure(equity)
        max_leverage = self.max_leverage()

        if -day_pnl > max_daily_loss:
            self._logger.error(
                "Daily loss limit exceeded: day_pnl=%.2f, max_daily_loss=%.2f",
                day_pnl,
                max_daily_loss,
            )
            raise RiskLimitExceeded("Daily loss limit exceeded")

        approved: List[Dict[str, Any]] = []
        violations: List[Dict[str, Any]] = []

        for order in candidate_orders:
            symbol = order.get("symbol")
            notional = float(order.get("notional", 0.0))

            # Symbol exposure check
            current_symbol_value = float(
                positions.get(symbol, {}).get("value", 0.0)
            )
            projected_symbol_value = current_symbol_value + notional
            if abs(projected_symbol_value) > max_symbol_exp:
                violations.append(
                    {
                        "order": order,
                        "reason": "max_symbol_exposure",
                        "limit": max_symbol_exp,
                        "projected": projected_symbol_value,
                    }
                )
                continue

            # Leverage check (approximate: assume notional scales leverage linearly)
            projected_leverage = current_leverage
            if equity > 0:
                projected_leverage = (equity * current_leverage + abs(notional)) / equity

            if projected_leverage > max_leverage:
                violations.append(
                    {
                        "order": order,
                        "reason": "max_leverage",
                        "limit": max_leverage,
                        "projected": projected_leverage,
                    }
                )
                continue

            approved.append(order)

        if violations:
            self._logger.warning(
                "Some orders were rejected by risk checks: %d violations",
                len(violations),
            )

        return approved, violations

