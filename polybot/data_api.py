"""Polymarket Data API client -- positions, trade history, wallet activity.

Base URL: https://data-api.polymarket.com
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from polybot.config import Config
from polybot.http import ApiClient

logger = logging.getLogger(__name__)


class DataApiClient:
    """Client for the Polymarket Data API."""

    def __init__(self, cfg: Config) -> None:
        self.api = ApiClient(cfg.data_base, timeout=cfg.request_timeout)
        self.cfg = cfg
        self.funder = cfg.funder_address

    def get_positions(self, address: str | None = None) -> list[dict[str, Any]]:
        """Retrieve open positions for an address.

        Falls back to ``cfg.funder_address`` if no address supplied.
        """
        addr = address or self.funder
        if not addr:
            logger.warning("No address provided and FUNDER_ADDRESS not set; cannot fetch positions.")
            return []

        resp = self.api.get("/positions", params={"user": addr})
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data
        return data.get("positions", data.get("data", []))

    def get_trades(self, address: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        """Retrieve recent trades for an address."""
        addr = address or self.funder
        if not addr:
            return []
        resp = self.api.get("/trades", params={"user": addr, "limit": limit})
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data
        return data.get("trades", data.get("data", []))

    def get_balance(self, address: str | None = None) -> Decimal:
        """Attempt to retrieve USDC balance / collateral.

        This may not be directly available from the Data API; if not,
        returns Decimal("-1") to indicate unknown.
        """
        addr = address or self.funder
        if not addr:
            return Decimal("-1")
        try:
            resp = self.api.get("/balance", params={"user": addr})
            if resp.ok:
                data = resp.json()
                bal = data.get("balance") or data.get("collateral") or data.get("total")
                if bal is not None:
                    return Decimal(str(bal))
        except Exception:
            logger.debug("Balance endpoint unavailable or errored for %s", addr)
        return Decimal("-1")

    def get_wallet_activity(self, address: str, limit: int = 20) -> list[dict[str, Any]]:
        """Fetch activity for a watched wallet (whale-copy scaffolding)."""
        try:
            resp = self.api.get("/activity", params={"user": address, "limit": limit})
            if resp.ok:
                data = resp.json()
                if isinstance(data, list):
                    return data
                return data.get("activity", data.get("data", []))
        except Exception:
            logger.debug("Activity endpoint unavailable for %s", address)
        return []
