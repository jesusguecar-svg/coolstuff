"""Whale Copy Strategy -- SKELETON / FUTURE PLUGIN.

Concept:
- Maintain a watch-list of wallet addresses known for profitable
  Polymarket trading.
- Monitor their on-chain activity via the Data API.
- When a watched wallet places a trade, copy it at proportional size
  if slippage from their entry <= MAX_SLIPPAGE_FROM_WHALE.

Implementation notes:
- ``watched_wallets`` table in the database stores addresses and labels.
- The Data API ``/activity`` endpoint (or trades endpoint) provides
  recent wallet activity.
- Slippage estimation: compare whale entry price vs current best ask.

Risks:
- Whales may exit before you do.
- Latency between detection and execution.
- Front-running concerns.
- Whale may be hedging (their trade makes sense in context of their
  full portfolio, not in isolation).

This file provides the interface scaffolding only.
"""

from __future__ import annotations

import logging

from polybot.strategies.base import BaseStrategy, ExecutionResult, Opportunity

logger = logging.getLogger(__name__)


class WhaleCopyStrategy(BaseStrategy):
    """Copy proportional trades from watched wallets. NOT YET IMPLEMENTED."""

    name = "whale_copy"

    def scan(self, limit: int = 20) -> list[Opportunity]:
        """Placeholder: would poll watched wallets for new trades."""
        raise NotImplementedError(
            "WhaleCopyStrategy is a skeleton for future development. "
            "See whale_copy_skeleton.py for design notes."
        )

    def execute(self, opportunity: Opportunity) -> ExecutionResult:
        """Placeholder."""
        raise NotImplementedError("WhaleCopyStrategy.execute not implemented.")
