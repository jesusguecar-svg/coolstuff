"""Gamma API client -- market discovery & metadata.

Base URL: https://gamma-api.polymarket.com

Gamma provides event/market metadata including:
- event titles, start times, tags
- market questions, outcomes, clobTokenIds
- indicative prices, volume, liquidity
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any

from polybot.config import Config
from polybot.http import ApiClient

logger = logging.getLogger(__name__)


@dataclass
class Market:
    """Parsed representation of a Gamma market."""

    condition_id: str
    question: str
    outcomes: list[str]
    clob_token_ids: list[str]
    outcome_prices: list[Decimal]
    volume: Decimal
    liquidity: Decimal
    event_title: str
    start_time: str | None
    end_time: str | None
    is_binary: bool
    active: bool
    tags: list[str] = field(default_factory=list)
    slug: str = ""
    market_id: str = ""
    raw: dict[str, Any] = field(default_factory=dict, repr=False)


def _safe_decimal(val: Any, default: Decimal = Decimal("0")) -> Decimal:
    if val is None:
        return default
    try:
        return Decimal(str(val))
    except (InvalidOperation, ValueError):
        return default


def _parse_market(raw: dict[str, Any], event_title: str = "", event_tags: list[str] | None = None) -> Market | None:
    """Parse a raw Gamma market dict into a ``Market``, or None if unusable."""
    condition_id = raw.get("conditionId") or raw.get("condition_id") or ""
    question = raw.get("question", "")
    if not condition_id or not question:
        return None

    # Outcomes
    outcomes_raw = raw.get("outcomes")
    if isinstance(outcomes_raw, str):
        # Sometimes comes as JSON-encoded string: '["Yes","No"]'
        import json

        try:
            outcomes_raw = json.loads(outcomes_raw)
        except (json.JSONDecodeError, TypeError):
            outcomes_raw = []
    outcomes: list[str] = outcomes_raw if isinstance(outcomes_raw, list) else []

    # clobTokenIds
    clob_raw = raw.get("clobTokenIds")
    if isinstance(clob_raw, str):
        import json

        try:
            clob_raw = json.loads(clob_raw)
        except (json.JSONDecodeError, TypeError):
            clob_raw = []
    clob_token_ids: list[str] = clob_raw if isinstance(clob_raw, list) else []

    # Prices
    prices_raw = raw.get("outcomePrices")
    if isinstance(prices_raw, str):
        import json

        try:
            prices_raw = json.loads(prices_raw)
        except (json.JSONDecodeError, TypeError):
            prices_raw = []
    outcome_prices = [_safe_decimal(p) for p in (prices_raw or [])]

    is_binary = len(outcomes) == 2 and len(clob_token_ids) == 2

    return Market(
        condition_id=condition_id,
        question=question,
        outcomes=outcomes,
        clob_token_ids=clob_token_ids,
        outcome_prices=outcome_prices,
        volume=_safe_decimal(raw.get("volume")),
        liquidity=_safe_decimal(raw.get("liquidity")),
        event_title=event_title,
        start_time=raw.get("startDate") or raw.get("start_date"),
        end_time=raw.get("endDate") or raw.get("end_date"),
        is_binary=is_binary,
        active=raw.get("active", True) is not False,
        tags=event_tags or [],
        slug=raw.get("slug", ""),
        market_id=raw.get("id", condition_id),
        raw=raw,
    )


class GammaClient:
    """Client for the Gamma market-discovery API."""

    def __init__(self, cfg: Config) -> None:
        self.api = ApiClient(cfg.gamma_base, timeout=cfg.request_timeout)
        self.cfg = cfg

    def get_events(
        self,
        limit: int = 20,
        offset: int = 0,
        tag: str | None = None,
        active: bool = True,
        closed: bool = False,
    ) -> list[dict[str, Any]]:
        """Fetch events from Gamma with optional tag filter."""
        params: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "active": str(active).lower(),
            "closed": str(closed).lower(),
        }
        if tag:
            params["tag"] = tag
        resp = self.api.get("/events", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_markets(
        self,
        limit: int = 50,
        offset: int = 0,
        active: bool = True,
        closed: bool = False,
    ) -> list[dict[str, Any]]:
        """Fetch markets directly."""
        params: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "active": str(active).lower(),
            "closed": str(closed).lower(),
        }
        resp = self.api.get("/markets", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_market(self, condition_id: str) -> dict[str, Any] | None:
        """Fetch a single market by conditionId."""
        resp = self.api.get(f"/markets/{condition_id}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def discover_binary_markets(
        self,
        limit: int = 50,
        tag: str | None = None,
        min_volume: Decimal | None = None,
        min_liquidity: Decimal | None = None,
    ) -> list[Market]:
        """Discover binary markets suitable for trading strategies.

        Returns only markets that are:
        - Active and not closed
        - Truly binary (exactly 2 outcomes with 2 clobTokenIds)
        - Above minimum volume/liquidity thresholds
        """
        min_vol = min_volume if min_volume is not None else self.cfg.min_volume
        min_liq = min_liquidity if min_liquidity is not None else self.cfg.min_liquidity

        markets: list[Market] = []
        offset = 0
        page_size = min(limit, 100)

        while len(markets) < limit:
            try:
                events = self.get_events(limit=page_size, offset=offset, tag=tag, active=True, closed=False)
            except Exception:
                logger.exception("Failed to fetch events at offset %d", offset)
                break

            if not events:
                break

            for event in events:
                event_title = event.get("title", "")
                event_tags = event.get("tags", [])
                raw_markets = event.get("markets", [])

                for raw_mkt in raw_markets:
                    parsed = _parse_market(raw_mkt, event_title=event_title, event_tags=event_tags)
                    if parsed is None:
                        continue
                    if not parsed.is_binary:
                        continue
                    if not parsed.active:
                        continue
                    if parsed.volume < min_vol:
                        continue
                    if parsed.liquidity < min_liq:
                        continue
                    markets.append(parsed)
                    if len(markets) >= limit:
                        break
                if len(markets) >= limit:
                    break

            offset += page_size

        logger.info("Discovered %d binary markets (requested %d)", len(markets), limit)
        return markets
