"""Polymarket Bridge API client -- fund trading account from Base.

Base URL: https://bridge.polymarket.com

The Bridge API facilitates deposits from external chains (e.g. Base) into
a Polymarket trading wallet on Polygon.  Workflow:

1. ``create_deposit_address()`` -> get a one-time deposit address on Base
2. User sends USDC (on Base) to that address manually (or via Coinbase)
3. ``get_deposit_status()`` -> poll until the funds are credited
"""

from __future__ import annotations

import logging
from typing import Any

from polybot.config import Config
from polybot.db import Database
from polybot.http import ApiClient

logger = logging.getLogger(__name__)


class BridgeClient:
    """Client for the Polymarket Bridge API."""

    def __init__(self, cfg: Config, db: Database) -> None:
        self.api = ApiClient(cfg.bridge_base, timeout=cfg.request_timeout)
        self.cfg = cfg
        self.db = db

    def create_deposit_address(self, destination_address: str | None = None) -> dict[str, Any]:
        """Request a deposit address for a Polymarket wallet.

        Args:
            destination_address: The Polymarket wallet that should receive
                the funds.  Defaults to ``cfg.funder_address``.

        Returns:
            API response containing the deposit address and instructions.
        """
        dest = destination_address or self.cfg.funder_address
        if not dest:
            raise ValueError(
                "No destination address provided. Set FUNDER_ADDRESS in .env "
                "or pass destination_address explicitly."
            )

        resp = self.api.post(
            "/deposit-address",
            json_data={"destinationAddress": dest},
        )
        resp.raise_for_status()
        data = resp.json()

        # Persist to DB for tracking
        deposit_addr = data.get("depositAddress", data.get("address", "unknown"))
        asset = data.get("asset", "USDC")
        chain = data.get("chain", "Base")
        self.db.record_deposit(deposit_addr, asset, chain)

        logger.info("Deposit address created: %s (chain=%s)", deposit_addr, chain)
        return data

    def get_supported_assets(self) -> list[dict[str, Any]]:
        """List assets/chains supported for deposits."""
        resp = self.api.get("/supported-assets")
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data
        return data.get("assets", data.get("data", []))

    def get_deposit_status(self, deposit_id: str | None = None, tx_hash: str | None = None) -> dict[str, Any]:
        """Check status of a deposit.

        Pass either ``deposit_id`` or ``tx_hash``.
        """
        params: dict[str, str] = {}
        if deposit_id:
            params["depositId"] = deposit_id
        if tx_hash:
            params["txHash"] = tx_hash
        if not params:
            raise ValueError("Provide deposit_id or tx_hash to check status.")

        resp = self.api.get("/deposit-status", params=params)
        resp.raise_for_status()
        return resp.json()

    def print_funding_instructions(self, deposit_data: dict[str, Any]) -> str:
        """Return human-readable funding instructions."""
        addr = deposit_data.get("depositAddress", deposit_data.get("address", "N/A"))
        chain = deposit_data.get("chain", "Base")
        asset = deposit_data.get("asset", "USDC")

        instructions = (
            f"\n{'='*60}\n"
            f"  FUNDING INSTRUCTIONS\n"
            f"{'='*60}\n"
            f"  1. Open Coinbase Wallet (or any Base-compatible wallet)\n"
            f"  2. Send {asset} on {chain} to:\n\n"
            f"     {addr}\n\n"
            f"  3. Wait for confirmation (check status with:\n"
            f"     python -m polybot funding status)\n"
            f"  4. Funds will be credited to your Polymarket account\n"
            f"     on Polygon automatically via the bridge.\n"
            f"\n"
            f"  WARNING: Only send {asset} on {chain}. Sending other\n"
            f"  tokens or using the wrong chain may result in loss.\n"
            f"{'='*60}\n"
        )
        return instructions
