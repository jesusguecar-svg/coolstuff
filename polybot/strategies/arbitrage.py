"""Binary Intra-Market Arbitrage Strategy.

For a binary market with outcomes YES and NO:
- If best_ask(YES) + best_ask(NO) < 1 - MIN_ARB_EDGE, there is a
  theoretical arbitrage: buy both sides for less than $1, guaranteed
  to receive $1 at resolution.

IMPORTANT CAVEATS (must be understood):
- Slippage: the asks may move before your orders fill.
- Partial fills: you might buy only one side, leaving you with directional
  exposure instead of a hedge.
- Resolution risk: disputed or ambiguous resolution can delay or void payouts.
- Fees: trading fees reduce or eliminate thin edges.
- Timing: between placing two orders, the book can change.

This strategy is educational.  It demonstrates the math but is NOT a
guaranteed profit machine.
"""

from __future__ import annotations

import logging
from decimal import Decimal

from polybot.strategies.base import BaseStrategy, ExecutionResult, Opportunity

logger = logging.getLogger(__name__)


class ArbitrageStrategy(BaseStrategy):
    """Detect and (optionally) exploit binary intra-market arb."""

    name = "arb"

    def scan(self, limit: int = 50) -> list[Opportunity]:
        """Scan binary markets for arb opportunities where
        best_ask(YES) + best_ask(NO) < 1 - min_arb_edge.
        """
        markets = self.gamma.discover_binary_markets(limit=limit * 2)
        opportunities: list[Opportunity] = []

        for market in markets:
            if len(market.clob_token_ids) != 2:
                continue

            token_yes = market.clob_token_ids[0]
            token_no = market.clob_token_ids[1]
            outcome_yes = market.outcomes[0] if market.outcomes else "Yes"
            outcome_no = market.outcomes[1] if len(market.outcomes) > 1 else "No"

            # Fetch CLOB order book best asks
            try:
                ask_yes_data = self.clob.best_ask_with_size(token_yes)
                ask_no_data = self.clob.best_ask_with_size(token_no)
            except Exception:
                logger.debug("Order book fetch failed for %s, skipping", market.question)
                continue

            if ask_yes_data is None or ask_no_data is None:
                continue

            ask_yes_price, ask_yes_size = ask_yes_data
            ask_no_price, ask_no_size = ask_no_data

            total_cost = ask_yes_price + ask_no_price
            edge = Decimal("1") - total_cost

            if edge < self.cfg.min_arb_edge:
                continue

            # Check spread on both sides
            try:
                spread_yes = self._compute_spread(token_yes)
                spread_no = self._compute_spread(token_no)
            except Exception:
                continue

            if spread_yes is not None and spread_yes > self.cfg.max_spread:
                continue
            if spread_no is not None and spread_no > self.cfg.max_spread:
                continue

            # Size: limited by available liquidity on both sides AND budget
            budget_shares = self.cfg.max_bet_usd / total_cost if total_cost > 0 else Decimal("0")
            max_shares = min(ask_yes_size, ask_no_size, budget_shares).quantize(Decimal("1"))

            if max_shares <= Decimal("0"):
                continue

            # Create paired opportunities (YES leg + NO leg)
            opp_yes = Opportunity(
                strategy=self.name,
                market=market,
                side="BUY",
                token_id=token_yes,
                outcome=outcome_yes,
                price=ask_yes_price,
                size=max_shares,
                reason=(
                    f"ARB: ask({outcome_yes})={ask_yes_price:.4f} + "
                    f"ask({outcome_no})={ask_no_price:.4f} = {total_cost:.4f}. "
                    f"Edge={edge:.4f} (min={self.cfg.min_arb_edge}). "
                    f"Shares={max_shares}."
                ),
                extra={"edge": str(edge), "total_cost": str(total_cost)},
            )

            opp_no = Opportunity(
                strategy=self.name,
                market=market,
                side="BUY",
                token_id=token_no,
                outcome=outcome_no,
                price=ask_no_price,
                size=max_shares,
                reason=f"ARB paired leg: {outcome_no} @ {ask_no_price:.4f}",
                extra={"edge": str(edge), "total_cost": str(total_cost)},
            )

            opp_yes.paired_opportunity = opp_no
            opportunities.append(opp_yes)

            if len(opportunities) >= limit:
                break

        logger.info("Arb scan found %d opportunities", len(opportunities))
        return opportunities

    def _compute_spread(self, token_id: str) -> Decimal | None:
        bid = self.clob.best_bid(token_id)
        ask = self.clob.best_ask(token_id)
        if bid is not None and ask is not None:
            return ask - bid
        return None

    def execute(self, opportunity: Opportunity) -> ExecutionResult:
        """Execute an arb opportunity (both legs).

        In paper/shadow mode, simulates.  In live + dry_run=False,
        places both leg orders.
        """
        paired = opportunity.paired_opportunity

        if self.cfg.mode in ("paper", "shadow"):
            msg = (
                f"[{self.cfg.mode.upper()}] SIMULATED ARB:\n"
                f"  Leg 1: BUY {opportunity.size} '{opportunity.outcome}' @ {opportunity.price}\n"
            )
            if paired:
                msg += f"  Leg 2: BUY {paired.size} '{paired.outcome}' @ {paired.price}\n"
            msg += f"  Edge: {opportunity.extra.get('edge', '?')}"
            logger.info(msg)
            return ExecutionResult(
                success=True,
                order_id=f"sim-arb-{opportunity.timestamp}",
                status="simulated",
                message=msg,
            )

        if self.cfg.dry_run:
            payload_1 = {
                "token_id": opportunity.token_id,
                "side": "BUY",
                "price": str(opportunity.price),
                "size": str(opportunity.size),
                "order_type": "GTC",
            }
            payload_2 = None
            if paired:
                payload_2 = {
                    "token_id": paired.token_id,
                    "side": "BUY",
                    "price": str(paired.price),
                    "size": str(paired.size),
                    "order_type": "GTC",
                }
            logger.info("[DRY-RUN] Arb leg 1: %s", payload_1)
            if payload_2:
                logger.info("[DRY-RUN] Arb leg 2: %s", payload_2)
            return ExecutionResult(
                success=True,
                order_id=None,
                status="dry_run",
                message=f"Dry-run arb payloads logged",
                raw_response={"leg1": payload_1, "leg2": payload_2},
            )

        # Live execution -- place both legs
        results: list[dict] = []
        for leg_label, leg in [("leg1", opportunity), ("leg2", paired)]:
            if leg is None:
                continue
            try:
                resp = self.clob.create_and_post_order(
                    token_id=leg.token_id,
                    price=float(leg.price),
                    size=float(leg.size),
                    side=leg.side,
                    order_type="GTC",
                )
                results.append({"leg": leg_label, "response": resp, "success": True})
                logger.info("Arb %s placed: %s", leg_label, resp)
            except Exception as exc:
                logger.error("Arb %s failed: %s", leg_label, exc)
                results.append({"leg": leg_label, "error": str(exc), "success": False})

        all_ok = all(r["success"] for r in results)
        return ExecutionResult(
            success=all_ok,
            order_id=results[0].get("response", {}).get("orderID") if results else None,
            status="sent" if all_ok else "partial",
            message="Both arb legs placed" if all_ok else "Partial fill -- check orders!",
            raw_response={"legs": results},
        )
