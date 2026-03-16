
import json
from pathlib import Path
from typing import Iterable, List, Tuple

import yfinance as yf

from core.logging_utils import get_logger


class LiquidityScanner:
    def __init__(self) -> None:
        self._logger = get_logger("uatp.liquidity")

    def scan(self, symbols: Iterable[str]) -> List[Tuple[str, float]]:
        results: List[Tuple[str, float]] = []

        for s in symbols:
            try:
                data = yf.download(s, period="5d")
                if data.empty or "Volume" not in data:
                    self._logger.warning("No volume data for symbol %s", s)
                    continue
                volume = float(data["Volume"].mean())
                results.append((s, volume))
            except Exception as exc:  # pragma: no cover - defensive
                self._logger.error("Failed to fetch data for %s: %s", s, exc)

        return sorted(results, key=lambda x: x[1], reverse=True)

    def scan_and_save(
        self,
        symbols: Iterable[str],
        output_path: str | Path,
    ) -> List[Tuple[str, float]]:
        results = self.scan(symbols)
        path = Path(output_path)
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        self._logger.info("Saved liquidity scan results to %s", path)
        return results

