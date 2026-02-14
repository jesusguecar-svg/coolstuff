"""Underdog Threshold Strategy.

For binary markets:
1. Discover active binary markets via Gamma (sports-like tags preferred).
2. Determine favorite (higher price) vs underdog (lower price).
3. If favorite >= FAVORITE_MIN_PRICE and underdog <= UNDERDOG_MAX_PRICE,
   and the book spread <= MAX_SPREAD, place a small limit buy on the
   underdog at best_ask.

This is a demo-friendly strategy that is simple to understand and test.
It is NOT a guaranteed-profit strategy.
"""

from __future__ import annotations

import logging
from decimal import Decimal

from polybot.strategies.base import BaseStrategy, ExecutionResult, Opportunity

logger = logging.getLogger(__name__)


class UnderdogStrategy(BaseStrategy):
    """Buy underdog outcomes when the market structure matches thresholds."""

    name = "underdog"

    def scan(self, limit: int = 20) -> list[Opportunity]:
        """Discover underdog opportunities across binary markets."""
        markets = self.gamma.discover_binary_markets(limit=limit * 2)
        opportunities: list[Opportunity] = []

        for market in markets:
            if len(market.clob_token_ids) != 2 or len(market.outcome_prices) != 2:
                continue

            # Determine favorite / underdog by Gamma indicative prices
            price_0 = market.outcome_prices[0]
            price_1 = market.outcome_prices[1]

            if price_0 >= price_1:
                fav_idx, dog_idx = 0, 1
            else:
                fav_idx, dog_idx = 1, 0

            fav_price = market.outcome_prices[fav_idx]
            dog_price = market.outcome_prices[dog_idx]

            # Check threshold filters
            if fav_price < self.cfg.favorite_min_price:
                continue
            if dog_price > self.cfg.underdog_max_price:
                continue
            if dog_price <= Decimal("0"):
                continue

            # Fetch real book data for the underdog token
            dog_token = market.clob_token_ids[dog_idx]
            dog_outcome = market.outcomes[dog_idx] if dog_idx < len(market.outcomes) else f"outcome_{dog_idx}"

            try:
                ask_data = self.clob.best_ask_with_size(dog_token)
            except Exception:
                logger.debug("Could not fetch order book for %s, skipping", dog_token)
                continue

            if ask_data is None:
                continue

            best_ask_price, best_ask_size = ask_data

            # Check spread using CLOB book
            try:
                bid = self.clob.best_bid(dog_token)
            except Exception:
                bid = None

            if bid is not None:
                spread = best_ask_price - bid
                if spread > self.cfg.max_spread:
                    logger.debug(
                        "Spread %.4f > max %.4f for %s, skipping",
                        spread, self.cfg.max_spread, market.question,
                    )
                    continue

            # Size: min of max_bet / price, available ask size, respecting budget
            if best_ask_price > Decimal("0"):
                shares = (self.cfg.max_bet_usd / best_ask_price).quantize(Decimal("1"))
                size = min(shares, best_ask_size)
            else:
                continue

            if size <= Decimal("0"):
                continue

            opp = Opportunity(
                strategy=self.name,
                market=market,
                side="BUY",
                token_id=dog_token,
                outcome=dog_outcome,
                price=best_ask_price,
                size=size,
                reason=(
                    f"Underdog '{dog_outcome}' at {best_ask_price:.4f} "
                    f"(favorite at {fav_price:.4f}). "
                    f"Spread OK. Size={size}."
                ),
            )
            opportunities.append(opp)

            if len(opportunities) >= limit:
                break

        logger.info("Underdog scan found %d opportunities", len(opportunities))
        return opportunities

    def execute(self, opportunity: Opportunity) -> ExecutionResult:
        """Execute an underdog buy order.

        In paper/shadow mode, simulates the fill.  In live mode (when
        dry_run=False), places a real limit order at the best ask.
        """
        if self.cfg.mode in ("paper", "shadow"):
            logger.info(
                "[%s] SIMULATED BUY %s shares of '%s' @ %s on '%s'",
                self.cfg.mode.upper(),
                opportunity.size,
                opportunity.outcome,
                opportunity.price,
                opportunity.market.question,
            )
            return ExecutionResult(
                success=True,
                order_id=f"sim-{opportunity.timestamp}",
                status="simulated",
                message=f"[{self.cfg.mode}] Would buy {opportunity.size} @ {opportunity.price}",
            )

        if self.cfg.dry_run:
            payload = {
                "token_id": opportunity.token_id,
                "side": opportunity.side,
                "price": str(opportunity.price),
                "size": str(opportunity.size),
                "order_type": "GTC",
            }
            logger.info("[DRY-RUN] Would send order: %s", payload)
            return ExecutionResult(
                success=True,
                order_id=None,
                status="dry_run",
                message=f"Dry-run payload: {payload}",
                raw_response=payload,
            )

        # Live execution
        try:
            resp = self.clob.create_and_post_order(
                token_id=opportunity.token_id,
                price=float(opportunity.price),
                size=float(opportunity.size),
                side=opportunity.side,
                order_type="GTC",
            )
        except Exception as exc:
            logger.error("Order failed: %s", exc)
            return ExecutionResult(
                success=False,
                status="error",
                message=str(exc),
            )

        order_id = resp.get("orderID") or resp.get("order_id") or resp.get("id", "unknown")
        logger.info("Order placed: %s", order_id)
        return ExecutionResult(
            success=True,
            order_id=str(order_id),
            status="sent",
            message="Order placed successfully",
            raw_response=resp,
        )
