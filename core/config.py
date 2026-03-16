import json
import os
from pathlib import Path
from typing import Any, Dict


class ConfigError(Exception):
    pass


class Config:
    """
    Simple JSON-based configuration loader.

    Usage:
        cfg = Config.load()
        mode = cfg.get("mode", "backtest")
    """

    DEFAULT_PATH = Path("config") / "trading.json"

    def __init__(self, data: Dict[str, Any], path: Path) -> None:
        self._data = data
        self._path = path

    @classmethod
    def load(cls, path: str | os.PathLike[str] | None = None) -> "Config":
        if path is None:
            path = os.environ.get("UATP_CONFIG_PATH", str(cls.DEFAULT_PATH))

        config_path = Path(path)
        if not config_path.is_file():
            raise ConfigError(f"Config file not found: {config_path}")

        try:
            with config_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in config file {config_path}: {e}") from e

        return cls(data=data, path=config_path)

    @property
    def path(self) -> Path:
        return self._path

    def get(self, key: str, default: Any | None = None) -> Any:
        # Support dotted keys, e.g. "risk.max_daily_loss"
        if "." not in key:
            return self._data.get(key, default)

        current: Any = self._data
        for part in key.split("."):
            if not isinstance(current, dict):
                return default
            if part not in current:
                return default
            current = current[part]
        return current

