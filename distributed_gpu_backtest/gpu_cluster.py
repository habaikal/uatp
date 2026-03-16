
import ray
import torch
import numpy as np

ray.init(ignore_reinit_error=True)

@ray.remote
def gpu_backtest(strategy, returns):

    device = "cuda" if torch.cuda.is_available() else "cpu"

    tensor = torch.tensor(returns, device=device)

    sharpe = torch.mean(tensor) / torch.std(tensor)

    return {"strategy": strategy, "sharpe": sharpe.item()}
