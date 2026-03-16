import logging
import os
from logging import Logger
from pathlib import Path

from .config import Config, ConfigError


def _ensure_log_dir(path: Path) -> None:
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def get_logger(name: str = "uatp") -> Logger:
    """
    Return a configured logger.

    Configuration is read from config/trading.json (logging section), e.g.:

    {
      "logging": {
        "level": "INFO",
        "file": "logs/uatp.log"
      }
    }
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    # Defaults
    level_name = "INFO"
    file_path: Path | None = None

    try:
        cfg = Config.load()
        level_name = str(cfg.get("logging.level", level_name))
        file_value = cfg.get("logging.file")
        if file_value:
            file_path = Path(str(file_value))
    except ConfigError:
        # Fallback to environment or defaults if config not available
        level_name = os.environ.get("UATP_LOG_LEVEL", level_name)
        file_env = os.environ.get("UATP_LOG_FILE")
        if file_env:
            file_path = Path(file_env)

    level = getattr(logging, level_name.upper(), logging.INFO)
    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if file_path is not None:
        _ensure_log_dir(file_path)
        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger

