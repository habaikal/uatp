
import numpy as np

class RiskGovernor:

    def max_drawdown(self,returns):

        cumulative = np.cumsum(returns)

        peak = np.maximum.accumulate(cumulative)

        drawdown = cumulative - peak

        return drawdown.min()

    def position_limit(self,equity, risk_per_trade=0.01):

        return equity * risk_per_trade
