---
title: Ultimate AI Trading Platform v4
layout: default
---

# Ultimate AI Trading Platform v4

Advanced personal AI trading research framework with a production‑oriented risk & execution pipeline.

## Overview

This project provides a modular pipeline for:

- Massive strategy generation (Strategy Factory)
- Alpha modeling (Alpha Discovery AI)
- Portfolio construction
- Risk management
- Order routing & execution (with broker abstraction)
- Autonomous hedge fund style orchestration

> GitHub 저장소 코드와 상세 매뉴얼은 아래 링크를 참고하세요.

- **Source Code (GitHub)**: [`habaikal/uatp`](https://github.com/habaikal/uatp)
- **User Manual**: [`USER_MANUAL.md`](USER_MANUAL.md)
- **Upgrade Plan**: [`uatp-production-upgrade_9d279c1f.plan.md`](uatp-production-upgrade_9d279c1f.plan.md)

## Quick Start (Local Demo)

```bash
git clone https://github.com/habaikal/uatp.git
cd uatp
pip install -r requirements.txt
python -m scripts.demo_paper_trading
```

This will:

- Generate a batch of strategies
- Construct a risk‑aware portfolio
- Run risk checks (daily loss, symbol exposure, leverage)
- Execute approved orders through an in‑memory paper broker

