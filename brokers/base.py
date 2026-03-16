from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any, List

from execution_optimizer.orders import Order, ExecutionReport


class BaseBroker(ABC):
    @abstractmethod
    def get_balance(self) -> float:
        ...

    @abstractmethod
    def get_positions(self) -> Dict[str, Dict[str, float]]:
        ...

    @abstractmethod
    def place_order(self, order: Order) -> ExecutionReport:
        ...

    @abstractmethod
    def cancel_order(self, client_order_id: str) -> None:
        ...

    @abstractmethod
    def get_open_orders(self) -> List[Order]:
        ...

