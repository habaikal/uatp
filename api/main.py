from typing import Any, Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from autonomous_hedge_fund.engine import AutonomousHedgeFund
from portfolio.portfolio_manager import PortfolioManager
from strategy_factory.strategy_factory import StrategyFactory
from execution_optimizer.execution_optimizer import ExecutionOptimizer
from brokers.paper import PaperBroker
from core.logging_utils import get_logger
from risk_governor.risk_governor import RiskGovernor

from .schemas import (
    DemoRunResponse,
    EquityPoint,
    PortfolioItem,
    PortfolioState,
    RiskSnapshot,
    Strategy,
)


app = FastAPI(title="Ultimate AI Trading Platform API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = get_logger("uatp.api")


def _build_engine() -> AutonomousHedgeFund:
    strategy_engine = StrategyFactory()
    portfolio_engine = PortfolioManager()
    broker = PaperBroker(starting_equity=100000.0)
    exec_engine = ExecutionOptimizer(broker=broker)
    return AutonomousHedgeFund(
        strategy_engine=strategy_engine,
        portfolio_engine=portfolio_engine,
        execution_engine=exec_engine,
    )


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/strategies", response_model=List[Strategy])
def list_strategies(limit: int = 20) -> List[Strategy]:
    factory = StrategyFactory()
    strategies = [factory.generate_strategy() for _ in range(limit)]
    return [Strategy(params=s) for s in strategies]


@app.post("/demo/run", response_model=DemoRunResponse)
def run_demo() -> DemoRunResponse:
    engine = _build_engine()
    market_data: Any = None
    engine.run_backtest_step(market_data)

    state_dict = engine.state
    state = PortfolioState(
        equity=state_dict.get("equity", 0.0),
        day_pnl=state_dict.get("day_pnl", 0.0),
        positions=state_dict.get("positions", {}),
        leverage=state_dict.get("leverage", 1.0),
    )

    # 현재 엔진은 포트폴리오 구성을 외부에 노출하지 않으므로,
    # 간단히 전략 샘플을 다시 생성해 가중치 없이 전달한다.
    factory = StrategyFactory()
    sample_strats = [factory.generate_strategy() for _ in range(10)]
    portfolio_items = [
        PortfolioItem(strategy=s, weight=0.0) for s in sample_strats
    ]

    executed_orders = 20  # demo step에서 제출되는 주문 수와 일치

    logger.info("Demo run completed via API")

    return DemoRunResponse(
        executed_orders=executed_orders,
        state=state,
        portfolio=portfolio_items,
    )


@app.get("/equity_curve", response_model=List[EquityPoint])
def equity_curve() -> List[EquityPoint]:
    engine = _build_engine()
    engine.run_backtest_step(None)
    points = [
        EquityPoint(t=int(p["t"]), equity=float(p["equity"]))
        for p in engine.equity_history
    ]
    return points


@app.get("/risk", response_model=RiskSnapshot)
def risk_snapshot() -> RiskSnapshot:
    engine = _build_engine()
    rg = RiskGovernor()
    state = engine.state
    equity = float(state.get("equity", 0.0))
    day_pnl = float(state.get("day_pnl", 0.0))
    max_daily_loss = rg.max_daily_loss(equity)
    max_leverage = rg.max_leverage()
    current_leverage = float(state.get("leverage", 1.0))
    return RiskSnapshot(
        equity=equity,
        day_pnl=day_pnl,
        max_daily_loss=max_daily_loss,
        max_leverage=max_leverage,
        current_leverage=current_leverage,
    )


@app.websocket("/ws/stream")
async def ws_stream(ws: WebSocket) -> None:
    await ws.accept()
    engine = _build_engine()
    try:
        for _ in range(10):
            engine.run_backtest_step(None)
            state = engine.state
            await ws.send_json(
                {
                    "equity": state.get("equity", 0.0),
                    "day_pnl": state.get("day_pnl", 0.0),
                    "leverage": state.get("leverage", 1.0),
                }
            )
        await ws.close()
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")


