
import random

class StrategyFactory:

    indicators = ["sma","ema","rsi","macd","momentum","volatility"]

    def generate_strategy(self):

        return {
            "indicator": random.choice(self.indicators),
            "window": random.randint(5,200),
            "threshold": random.uniform(0.1,0.9)
        }

    def generate_many(self,n=1000000):

        for _ in range(n):
            yield self.generate_strategy()
