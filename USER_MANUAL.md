## Ultimate AI Trading Platform v4 – 특징 및 사용자 매뉴얼

### 1. 플랫폼 전체 개요

**Ultimate AI Trading Platform v4**는  
연구용 수준을 넘어, 실전 자동매매에 근접한 구조를 갖춘 **개인용 AI 트레이딩 연구·실험 프레임워크**입니다.

- **목표**
  - 수백~수만 개 전략을 자동으로 생성/선별
  - GPU/분산 백테스트로 성능 검증
  - 리스크/포트폴리오/실행 엔진을 통해 실전 구조에 가까운 파이프라인 제공
  - 브로커 어댑터만 추가하면 실시간 자동매매로 확장 가능한 설계

---

### 2. 핵심 특징

- **모듈형 아키텍처**
  - `StrategyFactory` / `AlphaDiscoveryModel` / `RiskGovernor` / `PortfolioManager` / `ExecutionOptimizer` / `AutonomousHedgeFund` / `LiquidityScanner` 등이 각각 독립 모듈로 분리.
  - 각 모듈을 따로 실험하거나, 통합 파이프라인으로 묶어 실행 가능.

- **실전 지향 리스크 & 실행 파이프라인**
  - 일일 손실 한도, 심볼별 최대 익스포저, 레버리지 한도 등 **리스크 제한**을 설정 기반으로 관리.
  - 브로커 추상화 계층(`BaseBroker`)과 페이퍼 브로커(`PaperBroker`)로, 실전 브로커를 쉽게 교체할 수 있는 구조.

- **분산 GPU 백테스트**
  - `ray` + `torch` 기반 GPU 병렬 백테스트로, 대량 전략의 샤프비 계산 및 비교를 고속 처리.

- **구성 파일 기반 운영(`config/trading.json`)**
  - 모드(`backtest`/`paper`/향후 live 확장), 로깅 레벨/파일, 리스크 파라미터, 포트폴리오 제약, 백테스트용 Ray 설정 등을 한 곳에서 관리.

- **로깅 및 예외 처리**
  - `core/logging_utils.get_logger`를 통한 통일된 로그 포맷.
  - 공통 예외(`RiskLimitExceeded`, `OrderRejected`, `ExecutionError` 등)로 오류 원인을 명확하게 구분.

---

### 3. 모듈별 핵심 기능

#### 3.1 설정·코어 유틸 (`core/`, `config/`)

- **`core/config.py` – `Config`**
  - `config/trading.json`(또는 `UATP_CONFIG_PATH` 환경변수)에서 설정 로드.
  - `"risk.max_daily_loss_pct"`처럼 **점 표기(dotted key)** 로 중첩 설정 접근.

- **`core/logging_utils.py` – `get_logger(name)`**
  - 설정 파일의 `logging.level`, `logging.file`에 따라 콘솔 및 파일 로그를 설정.
  - 통일된 포맷: `시간 | 레벨 | 로거이름 | 메시지`.

- **`core/exceptions.py`**
  - `UATPError` (베이스), `RiskLimitExceeded`, `OrderRejected`, `MarketDataError`, `ExecutionError` 등 정의.

- **`config/trading.json`**
  - 모드, 리스크 한도, 포트폴리오 제약, Ray 설정 등 중앙 관리.

---

#### 3.2 전략 생성 (`strategy_factory/strategy_factory.py`)

- **`StrategyFactory`**
  - 임의의 지표(`sma`, `ema`, `rsi`, `macd`, `momentum`, `volatility`)와 윈도우/threshold를 조합해 전략 파라미터를 생성.
  - `generate_strategy()` : 단일 전략 딕셔너리 반환.
  - `generate_many(n=1000000)` : 대량 전략을 제너레이터로 생성(메모리 효율적).

---

#### 3.3 알파 모델 (`alpha_discovery_ai/alpha_model.py`)

- **`AlphaDiscoveryModel(nn.Module)`**
  - 입력 크기 `input_size`와 은닉층 크기 `hidden`을 인자로 받는 간단한 MLP.
  - 전략 피처/시계열 특징을 입력 받아, 1차원 알파 스코어를 출력.

---

#### 3.4 리스크 거버너 (`risk_governor/risk_governor.py`)

- **추가 지표 및 한도**
  - `max_drawdown(returns)` : MDD 계산.
  - `realized_volatility(returns)` : 실현 변동성.
  - `position_limit(equity, risk_per_trade_pct)` : 1트레이드당 리스크 한도(설정 기반).
  - `max_symbol_exposure(equity)` : 종목당 최대 익스포저 금액.
  - `max_daily_loss(equity)` : 일일 손실 한도.
  - `max_leverage()` : 최대 레버리지.

- **핵심 인터페이스**
  - `validate_orders(portfolio_state, candidate_orders) -> (approved, violations)`
    - 일일 손실 한도, 심볼 익스포저, 레버리지 위반을 체크해:
      - 승인된 주문 리스트(`approved`)
      - 거절된 주문과 사유 리스트(`violations`) 반환.

---

#### 3.5 포트폴리오 매니저 (`portfolio/portfolio_manager.py`)

- **`PortfolioManager.allocate(...)`**
  - 입력:
    - `strategies`: 전략 설정 딕셔너리 리스트.
    - `expected_returns`: (옵션) 기대 수익률 리스트.
    - `risks`: (옵션) 각 전략의 리스크(예: 변동성).
    - `method`: `"risk_parity"` (기본).
  - 기능:
    - `risk_parity` + `risks` 제공 시: 역-리스크(1/volatility) 기반 가중치.
    - 설정 기반 `max_weight_per_strategy`, `min_weight_per_strategy`로 클리핑 후 재정규화.

---

#### 3.6 주문/실행 엔진 (`execution_optimizer/`, `brokers/`)

- **주문/체결 데이터 모델 (`execution_optimizer/orders.py`)**
  - `Order(symbol, side, quantity, order_type, price, time_in_force, client_order_id, notional)`
  - `ExecutionReport(symbol, side, quantity, price, status, reason)`

- **브로커 추상 클래스 (`brokers/base.py`)**
  - `get_balance()`, `get_positions()`, `place_order(order)`, `cancel_order(id)`, `get_open_orders()`

- **페이퍼 브로커 (`brokers/paper.py`)**
  - 메모리 상에서 주문을 즉시 체결하는 **페이퍼 트레이딩 브로커**.

- **실행 엔진 (`execution_optimizer/execution_optimizer.py`)**
  - `ExecutionOptimizer(broker: BaseBroker)`
  - `execute_orders(orders: List[dict]) -> List[ExecutionReport]`

---

#### 3.7 자율 헤지펀드 엔진 (`autonomous_hedge_fund/engine.py`)

- **상태 관리**
  - `_state` 에 `equity`, `day_pnl`, `positions`, `leverage` 등 계좌/포트폴리오 상태 저장.

- **주요 메서드**
  - `run_backtest_step(market_data)`
    - 전략 생성 → 포트폴리오 비중 계산 → 리스크 체크 → 주문 실행까지 한 스텝 수행.

---

#### 3.8 GPU 분산 백테스트 (`distributed_gpu_backtest/gpu_cluster.py`)

- 설정 기반 `ray.init`:
  - `config/trading.json` 의 `backtest.ray` 설정으로 CPU/GPU 자원 제어.

- **`gpu_backtest.remote(strategy, returns)`**
  - 단일 전략과 수익률 시퀀스로 샤프비 계산.

- **`run_gpu_backtests(strategies, returns_list)`**
  - 전략/수익률 리스트를 받아 병렬 실행 후 결과 리스트 반환.

---

#### 3.9 글로벌 유동성 스캐너 (`global_liquidity_scanner/liquidity_scanner.py`)

- **`scan(symbols)`**
  - `yfinance`로 최근 5일 거래량을 기준으로 심볼별 유동성 계산.

- **`scan_and_save(symbols, output_path)`**
  - 스캔 결과를 JSON 파일로 저장.

---

#### 3.10 스크립트 (`scripts/`)

- **`run_liquidity_scan.py`**
  - 간단한 유동성 스캔 예제.

- **`demo_paper_trading.py`**
  - `StrategyFactory` → `PortfolioManager` → `RiskGovernor` → `ExecutionOptimizer` → `PaperBroker` → `AutonomousHedgeFund` 를 연결한 엔드 투 엔드 페이퍼 트레이딩 데모.

---

### 4. 설치 및 실행 방법 (사용자 매뉴얼)

#### 4.1 요구 사항

- Python 3.10+ (권장)
- GPU 사용 시:
  - CUDA가 설치된 환경 + GPU 지원 PyTorch 버전
- 인터넷 연결 (`yfinance` 사용 시)

#### 4.2 설치

```bash
git clone https://github.com/habaikal/uatp.git
cd uatp
pip install -r requirements.txt
```

#### 4.3 기본 설정 편집

- `config/trading.json`에서 다음 항목을 필요에 맞게 조정:
  - `mode`: `"backtest"` / `"paper"` (향후 `"live"` 확장 가능)
  - `logging.level`: `"INFO"`, `"DEBUG"` 등
  - `risk.*`: 일일 손실 한도, 심볼별 익스포저, 레버리지 한도, 트레이드당 리스크 비율
  - `portfolio.*`: 전략별 최대/최소 비중
  - `backtest.ray.*`: GPU/CPU 자원 설정

---

#### 4.4 페이퍼 트레이딩 데모 실행

```bash
python -m scripts.demo_paper_trading
```

- 내부적으로 수행되는 일:
  - 랜덤 전략 여러 개 생성.
  - 포트폴리오 엔진이 위험 균형 기반 비중 계산.
  - 리스크 거버너가 일일 손실/익스포저/레버리지 제한 체크.
  - 승인된 주문만 페이퍼 브로커에 전달, 체결 시뮬레이션.
  - 최종 계좌 상태를 로그로 출력.

---

#### 4.5 GPU 백테스트 실행 예시

```python
from distributed_gpu_backtest.gpu_cluster import run_gpu_backtests
from strategy_factory.strategy_factory import StrategyFactory

factory = StrategyFactory()
strategies = [factory.generate_strategy() for _ in range(1000)]
returns_list = [...]  # 각 전략에 대한 수익률 시계열 리스트

results = run_gpu_backtests(strategies, returns_list)
```

---

#### 4.6 유동성 스캔 사용 예시

```python
from global_liquidity_scanner.liquidity_scanner import LiquidityScanner

scanner = LiquidityScanner()
symbols = ["AAPL", "MSFT", "TSLA", "BTC-USD"]
results = scanner.scan_and_save(symbols, "outputs/liquidity.json")
```

---

### 5. 실전 확장 가이드(요약)

- **브로커 연동**
  - `brokers/base.py`의 `BaseBroker`를 상속한 실제 브로커 어댑터(예: `BinanceBroker`, `IBBroker`, `KoreanBroker`)를 구현.
  - 이 브로커 인스턴스를 `ExecutionOptimizer`에 주입 → `AutonomousHedgeFund`에 연결.

- **실시간 루프**
  - `AutonomousHedgeFund`에 `run_live_loop()` (또는 유사 메서드)를 추가해, 일정 주기(초/분 단위)로 `run_backtest_step`과 유사한 로직을 돌리도록 확장.

- **모니터링/대시보드**
  - 현재 로그 구조를 바탕으로 ELK, Grafana, Prometheus 등과 연동하면, 실시간 리스크/포지션 모니터링 시스템으로 자연스럽게 확장 가능.

