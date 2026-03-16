
class AutonomousHedgeFund:

    def __init__(self, strategy_engine, portfolio_engine, execution_engine):

        self.strategy_engine = strategy_engine
        self.portfolio_engine = portfolio_engine
        self.execution_engine = execution_engine

    def run(self, market_data):

        strategies = self.strategy_engine.generate_many(1000)

        portfolio = self.portfolio_engine.allocate(list(strategies)[:20])

        for strategy, weight in portfolio:

            order = {"strategy": strategy, "weight": weight}

            self.execution_engine.execute(order)
