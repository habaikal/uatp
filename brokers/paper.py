from __future__ import annotations

import itertools
from typing import Dict, Any, List

from execution_optimizer.orders import Order, ExecutionReport
from core.logging_utils import get_logger
from .base import BaseBroker


class PaperBroker(BaseBroker):
    """
    Simple in-memory paper trading broker.
    """

    _ids = itertools.count(1)

    def __init__(self, starting_equity: float = 100000.0) -> None:
        self._logger = get_logger("uatp.broker.paper")
        self._equity = starting_equity
        self._positions: Dict[str, Dict[str, float]] = {}
        self._open_orders: Dict[str, Order] = {}

    def get_balance(self) -> float:
        return self._equity

    def get_positions(self) -> Dict[str, Dict[str, float]]:
        return self._positions

    def get_open_orders(self) -> List[Order]:
        return list(self._open_orders.values())

    def place_order(self, order: Order) -> ExecutionReport:
        # Simplified: assume immediate full fill at given price (or 0 for market)
        if order.client_order_id is None:
            order.client_order_id = f"paper-{next(self._ids)}"

        price = order.price if order.price is not None else 0.0
        notional = price * order.quantity

        # Update equity and positions in a naive way
        pos = self._positions.setdefault(order.symbol, {"qty": 0.0, "value": 0.0})
        if order.side == "BUY":
            pos["qty"] += order.quantity
            pos["value"] += notional
            self._equity -= notional
        else:
            pos["qty"] -= order.quantity
            pos["value"] -= notional
            self._equity += notional

        report = ExecutionReport(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=price,
            status="FILLED",
        )
        self._logger.info(
            "Paper filled order: %s side=%s qty=%.4f price=%.4f",
            order.symbol,
            order.side,
            order.quantity,
            price,
        )
        return report

    def cancel_order(self, client_order_id: str) -> None:
        if client_order_id in self._open_orders:
            del self._open_orders[client_order_id]
            self._logger.info("Cancelled open order: %s", client_order_id)

