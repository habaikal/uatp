
## Ultimate AI Trading Platform v4

Experimental research framework for an advanced personal AI trading system, now with a production-leaning risk and execution pipeline.

### Modules

1. **Distributed GPU Backtest Cluster**
2. **Strategy Factory** (1M strategies scaffold)
3. **Alpha Discovery AI**
4. **Global Liquidity Scanner**
5. **Risk Governor AI**
6. **Autonomous Hedge Fund Engine**
7. **Execution Engine & Broker Abstraction (Paper broker included)**

### Pipeline

Market Data  
→ Tick Data Lake  
→ Feature Engineering  
→ Strategy Factory  
→ Distributed GPU Backtesting  
→ Alpha Discovery AI  
→ Portfolio Construction  
→ Risk Governor  
→ Execution Optimizer  
→ Autonomous Hedge Fund Engine

### Quick Start (Paper Trading Demo)

```bash
pip install -r requirements.txt
python -m scripts.demo_paper_trading
```

This will:
- Generate a batch of strategies
- Allocate a portfolio with basic risk-aware weights
- Run risk checks (daily loss, symbol exposure, leverage)
- Execute approved orders through an in-memory paper broker
- Log the final portfolio state

