from strategy_factory.strategy_factory import StrategyFactory
from portfolio.portfolio_manager import PortfolioManager
from execution_optimizer.execution_optimizer import ExecutionOptimizer
from brokers.paper import PaperBroker
from autonomous_hedge_fund.engine import AutonomousHedgeFund
from core.logging_utils import get_logger


def main() -> None:
    logger = get_logger("uatp.demo")

    strategy_engine = StrategyFactory()
    portfolio_engine = PortfolioManager()
    broker = PaperBroker(starting_equity=100000.0)
    exec_engine = ExecutionOptimizer(broker=broker)
    hedge_fund = AutonomousHedgeFund(
        strategy_engine=strategy_engine,
        portfolio_engine=portfolio_engine,
        execution_engine=exec_engine,
    )

    # In a real system, market_data would be live or historical prices.
    market_data = None
    hedge_fund.run_backtest_step(market_data)

    logger.info("Final state: %s", hedge_fund.state)


if __name__ == "__main__":
    main()

