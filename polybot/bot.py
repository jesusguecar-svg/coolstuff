"""Main bot loop -- ties together discovery, strategy, risk, and execution.

Supports:
- ``run_once()``: single scan + execute cycle
- ``run_loop()``: repeating cycle on an interval
- ``scan_only()``: just display opportunities without executing
"""

from __future__ import annotations

import dataclasses
import json
import logging
import signal
import time
from typing import Any

from polybot.clob_client import PolyClobClient
from polybot.clob_rest import ClobRestClient
from polybot.config import Config
from polybot.data_api import DataApiClient
from polybot.db import Database
from polybot.execution import ExecutionEngine
from polybot.gamma import GammaClient
from polybot.risk import RiskManager
from polybot.strategies import get_strategy
from polybot.strategies.base import BaseStrategy

logger = logging.getLogger(__name__)


class Bot:
    """Orchestrator for the trading bot."""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.db = Database(cfg.db_path)
        self.gamma = GammaClient(cfg)
        self.clob = PolyClobClient(cfg, self.db)
        self.clob_rest = ClobRestClient(cfg)
        self.data_api = DataApiClient(cfg)
        self.risk = RiskManager(cfg, self.db, self.clob, self.data_api)
        self.engine = ExecutionEngine(cfg, self.db, self.clob, self.clob_rest, self.risk)
        self._running = False

    def get_strategy(self, name: str) -> BaseStrategy:
        return get_strategy(
            name, cfg=self.cfg, db=self.db, gamma=self.gamma,
            clob=self.clob, clob_rest=self.clob_rest,
        )

    def scan_only(self, strategy_name: str, limit: int = 20) -> list[dict[str, Any]]:
        """Run a scan and return opportunities as dicts (no execution)."""
        strategy = self.get_strategy(strategy_name)
        logger.info("Scanning with strategy '%s' (limit=%d)...", strategy_name, limit)

        opportunities = strategy.scan(limit=limit)

        results = []
        for opp in opportunities:
            entry = {
                "strategy": opp.strategy,
                "market": opp.market.question,
                "event": opp.market.event_title,
                "outcome": opp.outcome,
                "side": opp.side,
                "price": str(opp.price),
                "size": str(opp.size),
                "reason": opp.reason,
                "volume": str(opp.market.volume),
                "liquidity": str(opp.market.liquidity),
            }
            results.append(entry)

        return results

    def run_once(self, strategy_name: str) -> dict[str, Any]:
        """Single scan -> risk check -> execute cycle."""
        run_id = self.db.start_run(self.cfg.mode, strategy_name)

        # Save config snapshot
        try:
            snapshot = {k: str(v) for k, v in dataclasses.asdict(self.cfg).items() if k != "private_key"}
            self.db.save_config_snapshot(run_id, snapshot)
        except Exception:
            pass

        strategy = self.get_strategy(strategy_name)
        errors = 0
        executed = 0
        results: list[dict[str, Any]] = []

        try:
            logger.info(
                "Run #%d | strategy=%s | mode=%s | dry_run=%s",
                run_id, strategy_name, self.cfg.mode, self.cfg.dry_run,
            )

            opportunities = strategy.scan()
            logger.info("Found %d opportunities.", len(opportunities))

            for opp in opportunities:
                if self.risk.is_halted:
                    logger.warning("Risk halt active, stopping execution.")
                    break

                result = self.engine.submit(opp, run_id=run_id)
                results.append({
                    "opportunity": opp.reason,
                    "success": result.success,
                    "status": result.status,
                    "order_id": result.order_id,
                    "message": result.message,
                })

                if result.success:
                    executed += 1
                else:
                    errors += 1

        except Exception:
            logger.exception("Unhandled error during run")
            errors += 1
        finally:
            self.db.finish_run(run_id, errors=errors)

        summary = {
            "run_id": run_id,
            "strategy": strategy_name,
            "mode": self.cfg.mode,
            "opportunities_found": len(results),
            "executed": executed,
            "errors": errors,
            "results": results,
        }
        logger.info("Run #%d complete: %d executed, %d errors.", run_id, executed, errors)
        return summary

    def run_loop(self, strategy_name: str, interval_seconds: int = 30) -> None:
        """Repeating scan+execute loop with configurable interval.

        Stops on SIGINT/SIGTERM or risk halt.
        """
        self._running = True

        def _stop(signum: int, frame: Any) -> None:
            logger.info("Received signal %d, stopping loop...", signum)
            self._running = False

        signal.signal(signal.SIGINT, _stop)
        signal.signal(signal.SIGTERM, _stop)

        logger.info(
            "Starting bot loop: strategy=%s interval=%ds mode=%s",
            strategy_name, interval_seconds, self.cfg.mode,
        )

        while self._running:
            if self.risk.is_halted:
                logger.critical("Risk halt active: %s. Stopping loop.", self.risk.halt_reason)
                break

            try:
                summary = self.run_once(strategy_name)
                _log_summary(summary)
            except Exception:
                logger.exception("Error in bot loop iteration")
                self.risk.record_api_error()

            if not self._running:
                break

            logger.info("Sleeping %ds until next cycle...", interval_seconds)
            # Sleep in small increments to catch signals quickly
            for _ in range(interval_seconds * 2):
                if not self._running:
                    break
                time.sleep(0.5)

        logger.info("Bot loop stopped.")

    def panic(self) -> dict:
        """Cancel all open orders (emergency stop)."""
        return self.risk.panic_cancel_all()


def _log_summary(summary: dict[str, Any]) -> None:
    """Pretty-log a run summary."""
    logger.info(
        "=== Run #%s Summary ===\n"
        "  Strategy:      %s\n"
        "  Mode:          %s\n"
        "  Opportunities: %d\n"
        "  Executed:      %d\n"
        "  Errors:        %d",
        summary["run_id"],
        summary["strategy"],
        summary["mode"],
        summary["opportunities_found"],
        summary["executed"],
        summary["errors"],
    )
