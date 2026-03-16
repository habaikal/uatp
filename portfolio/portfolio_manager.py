
import numpy as np
from typing import List, Dict, Any, Tuple

from core.config import Config


class PortfolioManager:
    def __init__(self) -> None:
        self._cfg = Config.load()

    def _random_weights(self, n: int) -> np.ndarray:
        return np.random.dirichlet(np.ones(n))

    def _clipped_weights(self, raw_weights: np.ndarray) -> np.ndarray:
        max_w = float(self._cfg.get("portfolio.max_weight_per_strategy", 0.1))
        min_w = float(self._cfg.get("portfolio.min_weight_per_strategy", 0.0))

        clipped = np.clip(raw_weights, min_w, max_w)
        total = clipped.sum()
        if total <= 0:
            return self._random_weights(len(raw_weights))
        return clipped / total

    def allocate(
        self,
        strategies: List[Dict[str, Any]],
        expected_returns: List[float] | None = None,
        risks: List[float] | None = None,
        method: str = "risk_parity",
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Allocate weights to strategies.

        method:
          - \"risk_parity\": inverse-volatility style weights if risks are provided,
                            otherwise fall back to equal/random weights with clipping.
        """
        n = len(strategies)
        if n == 0:
            return []

        raw_weights: np.ndarray

        if method == "risk_parity" and risks is not None:
            arr_risk = np.asarray(risks, dtype=float)
            # Avoid division by zero
            arr_risk[arr_risk <= 0] = arr_risk[arr_risk > 0].min(initial=1.0)
            inv_risk = 1.0 / arr_risk
            total = inv_risk.sum()
            if total > 0:
                raw_weights = inv_risk / total
            else:
                raw_weights = np.ones(n) / n
        else:
            raw_weights = np.ones(n) / n

        weights = self._clipped_weights(raw_weights)
        return list(zip(strategies, weights.tolist()))

