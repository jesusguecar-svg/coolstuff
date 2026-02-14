"""Direct REST calls to public CLOB endpoints.

These supplement ``clob_client.py`` for queries that don't require
authenticated py-clob-client access (order books, price, tick size,
minimum size, market info).
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from polybot.config import Config
from polybot.http import ApiClient

logger = logging.getLogger(__name__)

# Polymarket's standard tick sizes
DEFAULT_TICK_SIZE = Decimal("0.01")
DEFAULT_MIN_SIZE = Decimal("5")  # $5 notional minimum is common


class ClobRestClient:
    """Public-endpoint CLOB REST helper."""

    def __init__(self, cfg: Config) -> None:
        self.api = ApiClient(cfg.clob_base, timeout=cfg.request_timeout)
        self.cfg = cfg
        self._tick_size_cache: dict[str, Decimal] = {}
        self._min_size_cache: dict[str, Decimal] = {}

    def get_order_book(self, token_id: str) -> dict[str, Any]:
        """GET /book?token_id=..."""
        resp = self.api.get("/book", params={"token_id": token_id})
        resp.raise_for_status()
        return resp.json()

    def get_price(self, token_id: str) -> dict[str, Any]:
        """GET /price?token_id=..."""
        resp = self.api.get("/price", params={"token_id": token_id})
        resp.raise_for_status()
        return resp.json()

    def get_midpoint(self, token_id: str) -> Decimal | None:
        """Return midpoint price for a token, or None."""
        try:
            data = self.get_price(token_id)
            mid = data.get("mid") or data.get("midpoint")
            if mid is not None:
                return Decimal(str(mid))
        except Exception:
            logger.debug("Could not fetch midpoint for %s", token_id)
        return None

    def get_spread(self, token_id: str) -> Decimal | None:
        """Return spread for a token, or None."""
        try:
            data = self.get_price(token_id)
            spread = data.get("spread")
            if spread is not None:
                return Decimal(str(spread))
        except Exception:
            logger.debug("Could not fetch spread for %s", token_id)
        return None

    def get_tick_size(self, token_id: str) -> Decimal:
        """Return the tick size for a given token.

        Caches results per token_id to minimize requests.
        Falls back to DEFAULT_TICK_SIZE if the API doesn't expose it.
        """
        if token_id in self._tick_size_cache:
            return self._tick_size_cache[token_id]

        try:
            resp = self.api.get("/tick-size", params={"token_id": token_id})
            if resp.ok:
                data = resp.json()
                ts = Decimal(str(data.get("minimum_tick_size", DEFAULT_TICK_SIZE)))
                self._tick_size_cache[token_id] = ts
                return ts
        except Exception:
            logger.debug("Tick-size endpoint unavailable for %s, using default", token_id)

        self._tick_size_cache[token_id] = DEFAULT_TICK_SIZE
        return DEFAULT_TICK_SIZE

    def get_min_size(self, token_id: str) -> Decimal:
        """Return minimum order size.

        Falls back to DEFAULT_MIN_SIZE if the API doesn't expose it.
        """
        if token_id in self._min_size_cache:
            return self._min_size_cache[token_id]

        # The CLOB may not have a dedicated endpoint; use default.
        self._min_size_cache[token_id] = DEFAULT_MIN_SIZE
        return DEFAULT_MIN_SIZE

    def invalidate_tick_cache(self, token_id: str) -> None:
        """Drop cached tick size so the next call re-fetches."""
        self._tick_size_cache.pop(token_id, None)

    def invalidate_min_size_cache(self, token_id: str) -> None:
        """Drop cached min size."""
        self._min_size_cache.pop(token_id, None)
