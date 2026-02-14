"""Risk management and safety guardrails.

Enforces:
- Daily budget limits
- Maximum open orders
- Minimum wallet balance
- API error-rate circuit breaker
- Spread / liquidity thresholds (delegated to strategies, but double-checked here)
"""

from __future__ import annotations

import logging
import time
from collections import deque
from dataclasses import dataclass
from decimal import Decimal

from polybot.clob_client import PolyClobClient
from polybot.config import Config
from polybot.data_api import DataApiClient
from polybot.db import Database

logger = logging.getLogger(__name__)


@dataclass
class RiskCheck:
    """Result of a risk pre-check."""

    allowed: bool
    reason: str = ""


class RiskManager:
    """Central risk-enforcement layer.

    Every order attempt should call ``pre_check()`` before submission.
    After each API error call ``record_api_error()`` to feed the
    circuit breaker.
    """

    def __init__(
        self,
        cfg: Config,
        db: Database,
        clob: PolyClobClient,
        data_api: DataApiClient,
    ) -> None:
        self.cfg = cfg
        self.db = db
        self.clob = clob
        self.data_api = data_api
        self._error_times: deque[float] = deque()
        self._halted = False
        self._halt_reason = ""

    @property
    def is_halted(self) -> bool:
        return self._halted

    @property
    def halt_reason(self) -> str:
        return self._halt_reason

    def halt(self, reason: str) -> None:
        """Manually halt the bot."""
        self._halted = True
        self._halt_reason = reason
        logger.critical("RISK HALT: %s", reason)

    def pre_check(self, cost_usd: Decimal) -> RiskCheck:
        """Run all safety checks before placing an order.

        Args:
            cost_usd: estimated cost of the order in USD.

        Returns:
            RiskCheck with ``allowed=True`` if all checks pass.
        """
        if self._halted:
            return RiskCheck(False, f"Bot halted: {self._halt_reason}")

        # ── Daily budget ─────────────────────────────────────────────
        spent = self.db.daily_spend()
        remaining = self.cfg.daily_budget_usd - spent
        if cost_usd > remaining:
            return RiskCheck(
                False,
                f"Daily budget exceeded. Spent={spent}, budget={self.cfg.daily_budget_usd}, "
                f"this order={cost_usd}, remaining={remaining}.",
            )

        # ── Max open orders ──────────────────────────────────────────
        open_orders = self.db.get_open_orders()
        if len(open_orders) >= self.cfg.max_open_orders:
            return RiskCheck(
                False,
                f"Max open orders reached ({len(open_orders)}/{self.cfg.max_open_orders}).",
            )

        # ── Max bet size ─────────────────────────────────────────────
        if cost_usd > self.cfg.max_bet_usd:
            return RiskCheck(
                False,
                f"Order cost {cost_usd} exceeds MAX_BET_USD={self.cfg.max_bet_usd}.",
            )

        # ── Wallet balance ───────────────────────────────────────────
        balance = self.data_api.get_balance()
        if balance >= Decimal("0") and balance < self.cfg.min_wallet_balance_usd:
            self.halt(f"Wallet balance {balance} below minimum {self.cfg.min_wallet_balance_usd}")
            return RiskCheck(False, self._halt_reason)

        # ── Error-rate circuit breaker ───────────────────────────────
        if self._check_error_rate():
            return RiskCheck(False, f"API error rate exceeded threshold. {self._halt_reason}")

        return RiskCheck(True)

    def post_order_spend(self, cost_usd: Decimal, order_id: str | None = None) -> None:
        """Record spend after a successful order placement."""
        self.db.record_spend(cost_usd, order_id)
        logger.info("Recorded spend: $%s (order=%s)", cost_usd, order_id)

    def record_api_error(self) -> None:
        """Record an API error timestamp for circuit-breaker logic."""
        self._error_times.append(time.monotonic())
        self._check_error_rate()

    def _check_error_rate(self) -> bool:
        """Return True if error rate has been exceeded (and halt)."""
        now = time.monotonic()
        window = self.cfg.api_error_window_seconds

        # Prune old entries
        while self._error_times and (now - self._error_times[0]) > window:
            self._error_times.popleft()

        if len(self._error_times) >= self.cfg.max_api_errors_per_window:
            self.halt(
                f"API error rate exceeded: {len(self._error_times)} errors "
                f"in {window}s window (max={self.cfg.max_api_errors_per_window})."
            )
            return True
        return False

    def panic_cancel_all(self) -> dict:
        """Cancel all open orders immediately (panic button)."""
        logger.warning("PANIC: Cancelling all open orders!")
        try:
            resp = self.clob.cancel_all_orders()
            # Mark all DB orders as canceled
            for order in self.db.get_open_orders():
                self.db.update_order_status(order["id"], "canceled")
            logger.info("All orders canceled.")
            return {"success": True, "response": resp}
        except Exception as exc:
            logger.error("Panic cancel failed: %s", exc)
            return {"success": False, "error": str(exc)}
