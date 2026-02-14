"""Order execution engine with tick-size/min-size validation, retry logic,
and state persistence.

Every order flows through ``ExecutionEngine.submit()`` which:
1. Validates tick-size and minimum-size compliance (Decimal arithmetic).
2. Checks risk guardrails via RiskManager.
3. Records the opportunity and order in the database for idempotency.
4. Delegates to the strategy's ``execute()`` method.
5. Handles CLOB rejection codes with automatic retry (once).
"""

from __future__ import annotations

import logging
import uuid
from decimal import ROUND_DOWN, ROUND_UP, Decimal
from typing import Any

from polybot.clob_client import PolyClobClient
from polybot.clob_rest import ClobRestClient
from polybot.config import Config
from polybot.db import Database
from polybot.risk import RiskManager
from polybot.strategies.base import ExecutionResult, Opportunity

logger = logging.getLogger(__name__)


def round_to_tick(price: Decimal, tick_size: Decimal) -> Decimal:
    """Round price DOWN to the nearest tick."""
    if tick_size <= 0:
        return price
    return (price / tick_size).quantize(Decimal("1"), rounding=ROUND_DOWN) * tick_size


def round_size_up(size: Decimal, min_size: Decimal) -> Decimal:
    """Ensure size meets minimum; round up if below."""
    if size < min_size:
        return min_size
    return size


class ExecutionEngine:
    """Validates, records, and submits orders."""

    def __init__(
        self,
        cfg: Config,
        db: Database,
        clob: PolyClobClient,
        clob_rest: ClobRestClient,
        risk: RiskManager,
    ) -> None:
        self.cfg = cfg
        self.db = db
        self.clob = clob
        self.clob_rest = clob_rest
        self.risk = risk

    def submit(
        self,
        opportunity: Opportunity,
        run_id: int | None = None,
    ) -> ExecutionResult:
        """Full submission pipeline for an opportunity.

        Returns an ``ExecutionResult`` regardless of outcome.
        """
        # ── 1. Tick-size validation ──────────────────────────────────
        tick = self.clob_rest.get_tick_size(opportunity.token_id)
        original_price = opportunity.price
        compliant_price = round_to_tick(opportunity.price, tick)
        if compliant_price != original_price:
            logger.info(
                "Price %s rounded to %s (tick=%s)",
                original_price, compliant_price, tick,
            )
            opportunity.price = compliant_price

        if opportunity.price <= Decimal("0") or opportunity.price >= Decimal("1"):
            return ExecutionResult(
                success=False,
                status="rejected",
                message=f"Price {opportunity.price} out of valid range (0, 1).",
            )

        # ── 2. Min-size validation ───────────────────────────────────
        min_size = self.clob_rest.get_min_size(opportunity.token_id)
        if opportunity.size < min_size:
            logger.info(
                "Size %s below minimum %s, bumping up.",
                opportunity.size, min_size,
            )
            opportunity.size = round_size_up(opportunity.size, min_size)

        # ── 3. Cost estimate ─────────────────────────────────────────
        cost_usd = opportunity.price * opportunity.size

        # ── 4. Risk pre-check ────────────────────────────────────────
        check = self.risk.pre_check(cost_usd)
        if not check.allowed:
            logger.warning("Risk check blocked order: %s", check.reason)
            return ExecutionResult(
                success=False,
                status="risk_blocked",
                message=check.reason,
            )

        # ── 5. Record opportunity (idempotency) ─────────────────────
        opp_id = self.db.record_opportunity(
            run_id=run_id,
            strategy=opportunity.strategy,
            market_id=opportunity.market.condition_id,
            question=opportunity.market.question,
            token_id=opportunity.token_id,
            outcome=opportunity.outcome,
            side=opportunity.side,
            price=opportunity.price,
            size=opportunity.size,
            reason=opportunity.reason,
        )

        # ── 6. Dry-run / paper / shadow ──────────────────────────────
        if self.cfg.mode in ("paper", "shadow") or self.cfg.dry_run:
            payload = self._build_payload(opportunity)
            mode_label = "DRY-RUN" if self.cfg.dry_run else self.cfg.mode.upper()
            logger.info(
                "[%s] Would send: token=%s side=%s price=%s size=%s",
                mode_label,
                opportunity.token_id,
                opportunity.side,
                opportunity.price,
                opportunity.size,
            )
            sim_id = f"sim-{uuid.uuid4().hex[:12]}"
            self.db.record_order(
                order_id=sim_id,
                opportunity_id=opp_id,
                market_id=opportunity.market.condition_id,
                token_id=opportunity.token_id,
                side=opportunity.side,
                price=opportunity.price,
                size=opportunity.size,
                status="simulated",
                raw_payload=payload,
            )
            return ExecutionResult(
                success=True,
                order_id=sim_id,
                status="simulated",
                message=f"[{mode_label}] Order simulated",
                raw_response=payload,
            )

        # ── 7. Live order submission ─────────────────────────────────
        return self._submit_live(opportunity, opp_id, retry=True)

    def _submit_live(
        self,
        opportunity: Opportunity,
        opp_id: int,
        retry: bool = True,
    ) -> ExecutionResult:
        """Attempt live order placement with optional retry on specific errors."""
        payload = self._build_payload(opportunity)
        temp_id = f"pending-{uuid.uuid4().hex[:12]}"

        self.db.record_order(
            order_id=temp_id,
            opportunity_id=opp_id,
            market_id=opportunity.market.condition_id,
            token_id=opportunity.token_id,
            side=opportunity.side,
            price=opportunity.price,
            size=opportunity.size,
            status="pending",
            raw_payload=payload,
        )

        try:
            resp = self.clob.create_and_post_order(
                token_id=opportunity.token_id,
                price=float(opportunity.price),
                size=float(opportunity.size),
                side=opportunity.side,
                order_type="GTC",
            )
        except Exception as exc:
            error_msg = str(exc)
            logger.error("Order submission failed: %s", error_msg)

            # ── Retry logic for known rejection codes ────────────────
            if retry:
                result = self._handle_rejection(error_msg, opportunity, opp_id)
                if result is not None:
                    self.db.update_order_status(temp_id, "rejected", {"error": error_msg})
                    return result

            self.db.update_order_status(temp_id, "rejected", {"error": error_msg})
            self.risk.record_api_error()
            return ExecutionResult(
                success=False,
                order_id=temp_id,
                status="rejected",
                message=error_msg,
            )

        # Success path
        order_id = resp.get("orderID") or resp.get("order_id") or resp.get("id", temp_id)
        self.db.update_order_status(temp_id, "sent", resp)

        # If CLOB returned a different ID, update the record
        if str(order_id) != temp_id:
            self.db.record_order(
                order_id=str(order_id),
                opportunity_id=opp_id,
                market_id=opportunity.market.condition_id,
                token_id=opportunity.token_id,
                side=opportunity.side,
                price=opportunity.price,
                size=opportunity.size,
                status="accepted",
                raw_payload=payload,
            )

        # Record spend
        cost_usd = opportunity.price * opportunity.size
        self.risk.post_order_spend(cost_usd, str(order_id))

        logger.info("Order accepted: %s", order_id)
        return ExecutionResult(
            success=True,
            order_id=str(order_id),
            status="accepted",
            message="Order placed on CLOB",
            raw_response=resp,
        )

    def _handle_rejection(
        self,
        error_msg: str,
        opportunity: Opportunity,
        opp_id: int,
    ) -> ExecutionResult | None:
        """Handle specific CLOB rejection codes with a single retry.

        Returns an ExecutionResult if handled, or None to fall through.
        """
        upper = error_msg.upper()

        if "INVALID_ORDER_MIN_TICK_SIZE" in upper or "TICK_SIZE" in upper:
            logger.info("Tick-size rejection. Re-fetching and retrying once.")
            self.clob_rest.invalidate_tick_cache(opportunity.token_id)
            tick = self.clob_rest.get_tick_size(opportunity.token_id)
            opportunity.price = round_to_tick(opportunity.price, tick)
            return self._submit_live(opportunity, opp_id, retry=False)

        if "INVALID_ORDER_MIN_SIZE" in upper or "MIN_SIZE" in upper:
            logger.info("Min-size rejection. Bumping size and retrying once.")
            self.clob_rest.invalidate_min_size_cache(opportunity.token_id)
            min_size = self.clob_rest.get_min_size(opportunity.token_id)
            opportunity.size = round_size_up(opportunity.size, min_size)
            return self._submit_live(opportunity, opp_id, retry=False)

        if "INSUFFICIENT" in upper or "BALANCE" in upper or "ALLOWANCE" in upper:
            msg = (
                "Insufficient balance or allowance. Actions to fix:\n"
                "  1. Check your wallet balance: python -m polybot positions\n"
                "  2. Fund via bridge: python -m polybot funding deposit-address\n"
                "  3. Ensure token allowance is set for the CLOB contract.\n"
                f"  Raw error: {error_msg}"
            )
            logger.error(msg)
            self.risk.halt("Insufficient balance/allowance")
            return ExecutionResult(success=False, status="insufficient_funds", message=msg)

        return None

    def _build_payload(self, opportunity: Opportunity) -> dict[str, Any]:
        """Build the order payload dict (for logging / dry-run display)."""
        return {
            "token_id": opportunity.token_id,
            "side": opportunity.side,
            "price": str(opportunity.price),
            "size": str(opportunity.size),
            "order_type": "GTC",
            "market": opportunity.market.condition_id,
            "outcome": opportunity.outcome,
            "strategy": opportunity.strategy,
        }
