
from global_liquidity_scanner.liquidity_scanner import LiquidityScanner

scanner=LiquidityScanner()

symbols=["AAPL","MSFT","TSLA","BTC-USD"]

print(scanner.scan(symbols))
