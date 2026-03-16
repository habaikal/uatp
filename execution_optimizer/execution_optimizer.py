
from typing import List, Dict, Any

from core.logging_utils import get_logger
from brokers.base import BaseBroker
from execution_optimizer.orders import Order, ExecutionReport


class ExecutionOptimizer:
    def __init__(self, broker: BaseBroker) -> None:
        self._broker = broker
        self._logger = get_logger("uatp.exec")

    def execute_orders(self, orders: List[Dict[str, Any]]) -> List[ExecutionReport]:
        """
        Execute a batch of order dictionaries via the underlying broker.

        Each order dict should contain at least: symbol, side, quantity.
        Optional keys: order_type, price, time_in_force, client_order_id.
        """
        reports: List[ExecutionReport] = []
        for od in orders:
            order = Order(
                symbol=str(od["symbol"]),
                side=str(od.get("side", "BUY")).upper(),  # type: ignore[arg-type]
                quantity=float(od["quantity"]),
                order_type=str(od.get("order_type", "MARKET")).upper(),  # type: ignore[arg-type]
                price=float(od["price"]) if "price" in od and od["price"] is not None else None,
                time_in_force=str(od.get("time_in_force", "GTC")).upper(),  # type: ignore[arg-type]
                client_order_id=od.get("client_order_id"),
                notional=float(od["notional"]) if "notional" in od else None,
            )
            report = self._broker.place_order(order)
            reports.append(report)
        self._logger.info("Executed %d orders", len(reports))
        return reports

