"""Strategy plugin registry.

Import strategies here so they can be looked up by name via ``get_strategy()``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from polybot.strategies.arbitrage import ArbitrageStrategy
from polybot.strategies.base import BaseStrategy
from polybot.strategies.underdog import UnderdogStrategy

if TYPE_CHECKING:
    from polybot.clob_client import PolyClobClient
    from polybot.clob_rest import ClobRestClient
    from polybot.config import Config
    from polybot.db import Database
    from polybot.gamma import GammaClient

_STRATEGY_MAP: dict[str, type[BaseStrategy]] = {
    "arb": ArbitrageStrategy,
    "arbitrage": ArbitrageStrategy,
    "underdog": UnderdogStrategy,
}


def get_strategy(
    name: str,
    cfg: "Config",
    db: "Database",
    gamma: "GammaClient",
    clob: "PolyClobClient",
    clob_rest: "ClobRestClient",
) -> BaseStrategy:
    """Instantiate a strategy by name."""
    cls = _STRATEGY_MAP.get(name.lower())
    if cls is None:
        available = ", ".join(sorted(_STRATEGY_MAP.keys()))
        raise ValueError(f"Unknown strategy '{name}'. Available: {available}")
    return cls(cfg=cfg, db=db, gamma=gamma, clob=clob, clob_rest=clob_rest)


__all__ = [
    "BaseStrategy",
    "ArbitrageStrategy",
    "UnderdogStrategy",
    "get_strategy",
]
