
import ray
import torch
import numpy as np
from typing import Dict, Any, Iterable, List

from core.config import Config
from core.logging_utils import get_logger


_logger = get_logger("uatp.gpu_backtest")
_cfg = Config.load()

ray_cfg = _cfg.get("backtest.ray", {}) or {}
ray.init(
    address=ray_cfg.get("address", None),
    ignore_reinit_error=True,
    num_cpus=ray_cfg.get("num_cpus", None),
    num_gpus=ray_cfg.get("num_gpus", None),
)


@ray.remote
def gpu_backtest(strategy: Dict[str, Any], returns: Iterable[float]) -> Dict[str, Any]:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    arr = np.asarray(list(returns), dtype=float)
    if arr.size == 0:
        sharpe = 0.0
    else:
        tensor = torch.tensor(arr, device=device)
        std = torch.std(tensor)
        if std.item() == 0:
            sharpe = 0.0
        else:
            sharpe = torch.mean(tensor) / std

    return {"strategy": strategy, "sharpe": float(sharpe)}


def run_gpu_backtests(
    strategies: List[Dict[str, Any]],
    returns_list: List[Iterable[float]],
) -> List[Dict[str, Any]]:
    """
    Convenience helper to run many backtests in parallel on the GPU cluster.
    """
    if len(strategies) != len(returns_list):
        raise ValueError("strategies and returns_list must have the same length")

    futures = [
        gpu_backtest.remote(strategy, rets)
        for strategy, rets in zip(strategies, returns_list)
    ]
    _logger.info("Submitted %d GPU backtests", len(futures))
    return ray.get(futures)

