"""Abstract base class for all trading strategies.

Every strategy must implement ``scan()`` and ``execute()``.

- ``scan()`` discovers opportunities from current market data and returns
  a list of ``Opportunity`` dataclasses.
- ``execute()`` takes a single opportunity and returns an ``ExecutionResult``.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from polybot.clob_client import PolyClobClient
from polybot.clob_rest import ClobRestClient
from polybot.config import Config
from polybot.db import Database
from polybot.gamma import GammaClient, Market


@dataclass
class Opportunity:
    """A trading opportunity identified by a strategy."""

    strategy: str
    market: Market
    side: str  # "BUY" or "SELL"
    token_id: str
    outcome: str
    price: Decimal
    size: Decimal
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    extra: dict[str, Any] = field(default_factory=dict)

    # For arb, we may have a paired leg
    paired_opportunity: Opportunity | None = field(default=None, repr=False)


@dataclass
class ExecutionResult:
    """Result of attempting to execute an opportunity."""

    success: bool
    order_id: str | None = None
    status: str = ""
    message: str = ""
    raw_response: dict[str, Any] = field(default_factory=dict)


class BaseStrategy(abc.ABC):
    """Interface that all strategies must implement."""

    name: str = "base"

    def __init__(
        self,
        cfg: Config,
        db: Database,
        gamma: GammaClient,
        clob: PolyClobClient,
        clob_rest: ClobRestClient,
    ) -> None:
        self.cfg = cfg
        self.db = db
        self.gamma = gamma
        self.clob = clob
        self.clob_rest = clob_rest

    @abc.abstractmethod
    def scan(self, limit: int = 20) -> list[Opportunity]:
        """Scan markets and return actionable opportunities.

        Must NOT place any orders -- purely observational.
        """

    @abc.abstractmethod
    def execute(self, opportunity: Opportunity) -> ExecutionResult:
        """Execute a single opportunity (place order or simulate).

        Should respect ``cfg.mode`` and ``cfg.dry_run``.
        """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} mode={self.cfg.mode} dry_run={self.cfg.dry_run}>"
