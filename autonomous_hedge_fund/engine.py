
from typing import Any, Dict, Iterable, List

from core.config import Config
from core.logging_utils import get_logger
from risk_governor.risk_governor import RiskGovernor


class AutonomousHedgeFund:
    def __init__(
        self,
        strategy_engine: Any,
        portfolio_engine: Any,
        execution_engine: Any,
        risk_governor: RiskGovernor | None = None,
    ):
        self.strategy_engine = strategy_engine
        self.portfolio_engine = portfolio_engine
        self.execution_engine = execution_engine
        self.risk_governor = risk_governor or RiskGovernor()

        self._cfg = Config.load()
        self._logger = get_logger("uatp.engine")

        # Simple in-memory state for paper/backtest modes
        self._state: Dict[str, Any] = {
            "equity": 100000.0,
            "day_pnl": 0.0,
            "positions": {},
            "leverage": 1.0,
        }

    @property
    def state(self) -> Dict[str, Any]:
        return self._state

    def _build_orders_from_portfolio(
        self, portfolio: Iterable[tuple[Dict[str, Any], float]]
    ) -> List[Dict[str, Any]]:
        equity = float(self._state.get("equity", 0.0))
        orders: List[Dict[str, Any]] = []
        for strat, weight in portfolio:
            symbol = strat.get("symbol", "UNKNOWN")
            side = "BUY" if weight >= 0 else "SELL"
            notional = equity * abs(weight)
            orders.append(
                {
                    "symbol": symbol,
                    "side": side,
                    "quantity": 1.0,  # placeholder, to be refined by execution layer
                    "notional": notional,
                    "order_type": "MARKET",
                }
            )
        return orders

    def run_backtest_step(self, market_data: Any) -> None:
        """
        Single step for backtest/paper: generate strategies, allocate, risk-check, execute.
        """
        strategies_iter = self.strategy_engine.generate_many(1000)
        strategies = list(strategies_iter)[:20]

        # For now, we don't pass explicit expected_returns/risks
        portfolio = self.portfolio_engine.allocate(strategies)

        candidate_orders = self._build_orders_from_portfolio(portfolio)
        approved, violations = self.risk_governor.validate_orders(self._state, candidate_orders)

        if violations:
            self._logger.info("Risk violations: %d", len(violations))

        if not approved:
            self._logger.info("No orders approved after risk checks")
            return

        self.execution_engine.execute_orders(approved)

