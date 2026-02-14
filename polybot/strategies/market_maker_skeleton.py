"""Market Making Strategy -- SKELETON / FUTURE PLUGIN.

Concept:
- Place two-sided quotes (bid + ask) around the midpoint of a binary market.
- Earn the spread when both sides fill.
- Optionally benefit from maker rebates if applicable.

Risks:
- Adverse selection (informed traders pick off your stale quotes).
- Inventory risk (accumulating one side).
- Resolution risk.

This file provides the interface scaffolding.  The scan/execute methods
raise NotImplementedError to signal that full implementation is pending.
"""

from __future__ import annotations

import logging

from polybot.strategies.base import BaseStrategy, ExecutionResult, Opportunity

logger = logging.getLogger(__name__)


class MarketMakerStrategy(BaseStrategy):
    """Two-sided quoting around midpoint. NOT YET IMPLEMENTED."""

    name = "market_maker"

    def scan(self, limit: int = 20) -> list[Opportunity]:
        """Placeholder: would discover markets with sufficient volume and
        spread for profitable market making.
        """
        raise NotImplementedError(
            "MarketMakerStrategy is a skeleton for future development. "
            "See market_maker_skeleton.py for design notes."
        )

    def execute(self, opportunity: Opportunity) -> ExecutionResult:
        """Placeholder: would place bid + ask around midpoint."""
        raise NotImplementedError("MarketMakerStrategy.execute not implemented.")
