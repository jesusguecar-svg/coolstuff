"""High-level wrapper around ``py-clob-client`` for authenticated CLOB
operations.

Handles:
- L2 API credential derivation from L1 private key (once) and caching
  to SQLite so credentials survive restarts.
- Order creation, posting, cancellation.
- Open-order queries.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs, OrderType

from polybot.config import Config
from polybot.db import Database

logger = logging.getLogger(__name__)

# Map friendly names to py-clob-client OrderType enum
ORDER_TYPE_MAP: dict[str, OrderType] = {
    "GTC": OrderType.GTC,
    "FOK": OrderType.FOK,
    "GTD": OrderType.GTD,
}


class PolyClobClient:
    """Manages a ``ClobClient`` instance with cached credentials."""

    def __init__(self, cfg: Config, db: Database) -> None:
        self.cfg = cfg
        self.db = db
        self._client: ClobClient | None = None

    @property
    def client(self) -> ClobClient:
        if self._client is None:
            self._client = self._init_client()
        return self._client

    def _init_client(self) -> ClobClient:
        """Build the ClobClient. Re-use cached API creds if available;
        otherwise derive fresh ones from the L1 private key and persist them.
        """
        clob = ClobClient(
            self.cfg.clob_base,
            key=self.cfg.private_key,
            chain_id=self.cfg.chain_id,
            signature_type=self.cfg.signature_type,
            funder=self.cfg.funder_address or None,
        )

        cached = self.db.load_api_creds()
        if cached:
            logger.info("Loaded cached L2 API credentials from database.")
            clob.set_api_creds(
                ApiCreds(
                    api_key=cached["api_key"],
                    api_secret=cached["api_secret"],
                    api_passphrase=cached["api_passphrase"],
                )
            )
        else:
            logger.info("Deriving fresh L2 API credentials from L1 signer...")
            try:
                creds = clob.derive_api_key()
                logger.info("L2 API credentials derived successfully.")
            except Exception:
                logger.exception("Failed to derive API key. Is the private key correct?")
                raise
            # creds is an ApiCreds or dict depending on version
            if isinstance(creds, dict):
                api_key = creds.get("apiKey", creds.get("api_key", ""))
                api_secret = creds.get("secret", creds.get("api_secret", ""))
                api_passphrase = creds.get("passphrase", creds.get("api_passphrase", ""))
            else:
                api_key = getattr(creds, "api_key", "") or getattr(creds, "apiKey", "")
                api_secret = getattr(creds, "api_secret", "") or getattr(creds, "secret", "")
                api_passphrase = getattr(creds, "api_passphrase", "") or getattr(creds, "passphrase", "")

            self.db.save_api_creds(api_key, api_secret, api_passphrase)
            clob.set_api_creds(ApiCreds(api_key=api_key, api_secret=api_secret, api_passphrase=api_passphrase))

        return clob

    # ── Order Book ───────────────────────────────────────────────────

    def get_order_book(self, token_id: str) -> dict[str, Any]:
        """Fetch the order book for a given token_id.

        Returns dict with ``bids`` and ``asks`` lists, each entry
        having ``price`` (str) and ``size`` (str).
        """
        try:
            book = self.client.get_order_book(token_id)
        except Exception:
            logger.exception("Failed to fetch order book for token %s", token_id)
            raise

        # Normalize to dict regardless of py-clob-client version
        if isinstance(book, dict):
            return book
        return {
            "bids": getattr(book, "bids", []),
            "asks": getattr(book, "asks", []),
        }

    def best_ask(self, token_id: str) -> Decimal | None:
        """Return the lowest ask price, or None if no asks."""
        book = self.get_order_book(token_id)
        asks = book.get("asks", [])
        if not asks:
            return None
        prices = []
        for a in asks:
            p = a.get("price") if isinstance(a, dict) else getattr(a, "price", None)
            if p is not None:
                prices.append(Decimal(str(p)))
        return min(prices) if prices else None

    def best_bid(self, token_id: str) -> Decimal | None:
        """Return the highest bid price, or None if no bids."""
        book = self.get_order_book(token_id)
        bids = book.get("bids", [])
        if not bids:
            return None
        prices = []
        for b in bids:
            p = b.get("price") if isinstance(b, dict) else getattr(b, "price", None)
            if p is not None:
                prices.append(Decimal(str(p)))
        return max(prices) if prices else None

    def best_ask_with_size(self, token_id: str) -> tuple[Decimal, Decimal] | None:
        """Return (price, size) of the best ask, or None."""
        book = self.get_order_book(token_id)
        asks = book.get("asks", [])
        if not asks:
            return None
        best = None
        for a in asks:
            if isinstance(a, dict):
                p, s = Decimal(str(a["price"])), Decimal(str(a["size"]))
            else:
                p, s = Decimal(str(a.price)), Decimal(str(a.size))
            if best is None or p < best[0]:
                best = (p, s)
        return best

    # ── Order Management ─────────────────────────────────────────────

    def create_and_post_order(
        self,
        token_id: str,
        price: float,
        size: float,
        side: str,
        order_type: str = "GTC",
    ) -> dict[str, Any]:
        """Create, sign, and post an order to the CLOB.

        ``price`` and ``size`` must already be tick-size/min-size compliant.
        They are floats here because py-clob-client expects floats.
        """
        ot = ORDER_TYPE_MAP.get(order_type, OrderType.GTC)
        order_args = OrderArgs(
            price=price,
            size=size,
            side=side,
            token_id=token_id,
        )
        try:
            signed = self.client.create_order(order_args)
            resp = self.client.post_order(signed, ot)
        except Exception:
            logger.exception("Order creation/posting failed for token %s", token_id)
            raise

        if isinstance(resp, dict):
            return resp
        # Some versions return an object; convert
        return {"success": True, "raw": str(resp)}

    def cancel_order(self, order_id: str) -> dict[str, Any]:
        """Cancel a single order by ID."""
        try:
            resp = self.client.cancel(order_id)
        except Exception:
            logger.exception("Failed to cancel order %s", order_id)
            raise
        if isinstance(resp, dict):
            return resp
        return {"success": True, "raw": str(resp)}

    def cancel_all_orders(self) -> dict[str, Any]:
        """Cancel all open orders (panic button)."""
        try:
            resp = self.client.cancel_all()
        except Exception:
            logger.exception("Failed to cancel all orders")
            raise
        if isinstance(resp, dict):
            return resp
        return {"success": True, "raw": str(resp)}

    def get_open_orders(self) -> list[dict[str, Any]]:
        """Retrieve currently open orders from the CLOB."""
        try:
            orders = self.client.get_orders()
        except AttributeError:
            # Fallback: some versions use get_open_orders
            orders = self.client.get_open_orders()  # type: ignore[attr-defined]
        except Exception:
            logger.exception("Failed to fetch open orders")
            raise

        if isinstance(orders, list):
            return [o if isinstance(o, dict) else vars(o) for o in orders]
        return []

    # ── Tick Size ────────────────────────────────────────────────────

    def get_tick_size(self, token_id: str) -> Decimal:
        """Return tick size for a token. Defaults to 0.01 if unavailable."""
        try:
            ts = self.client.get_tick_size(token_id)
            return Decimal(str(ts))
        except Exception:
            logger.warning("Could not fetch tick size for %s, defaulting to 0.01", token_id)
            return Decimal("0.01")

    def get_neg_risk(self, token_id: str) -> bool:
        """Check if a market uses neg-risk."""
        try:
            return bool(self.client.get_neg_risk(token_id))
        except Exception:
            return False
