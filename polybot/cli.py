"""CLI entry point using Typer.

Commands:
  funding deposit-address   Create a deposit address for bridging from Base
  funding supported-assets  Show supported deposit assets
  funding status            Check deposit status
  scan                      Discover opportunities without executing
  run                       Execute strategy in a loop
  run --once                Single execution cycle
  orders open               Show open orders
  orders cancel-all         Cancel all open orders (panic)
  positions                 Show current positions
  backtest                  Replay logged trades and compute basic PnL
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Optional

import typer

from polybot.logging_setup import setup_logging

app = typer.Typer(
    name="polybot",
    help="Educational Polymarket trading bot MVP. NOT financial advice.",
    no_args_is_help=True,
)
funding_app = typer.Typer(help="Funding / bridge operations.")
orders_app = typer.Typer(help="Order management.")
app.add_typer(funding_app, name="funding")
app.add_typer(orders_app, name="orders")


def _init() -> "tuple[Config, Bot]":  # type: ignore[name-defined]
    """Lazy imports to avoid heavy init on --help."""
    from polybot.bot import Bot
    from polybot.config import get_config

    cfg = get_config()
    setup_logging(cfg.log_level)
    return cfg, Bot(cfg)


# ── Funding ──────────────────────────────────────────────────────────


@funding_app.command("deposit-address")
def funding_deposit_address(
    address: Optional[str] = typer.Option(None, "--address", "-a", help="Override FUNDER_ADDRESS"),
) -> None:
    """Create a deposit address for bridging USDC from Base to Polymarket."""
    cfg, bot = _init()
    from polybot.bridge import BridgeClient

    bridge = BridgeClient(cfg, bot.db)
    try:
        data = bridge.create_deposit_address(destination_address=address)
        instructions = bridge.print_funding_instructions(data)
        typer.echo(instructions)
        typer.echo(f"Raw response: {json.dumps(data, indent=2)}")
    except Exception as exc:
        typer.echo(f"Error creating deposit address: {exc}", err=True)
        raise typer.Exit(1)


@funding_app.command("supported-assets")
def funding_supported_assets() -> None:
    """Show assets and chains supported for deposits."""
    cfg, bot = _init()
    from polybot.bridge import BridgeClient

    bridge = BridgeClient(cfg, bot.db)
    try:
        assets = bridge.get_supported_assets()
        typer.echo(json.dumps(assets, indent=2))
    except Exception as exc:
        typer.echo(f"Error fetching supported assets: {exc}", err=True)
        raise typer.Exit(1)


@funding_app.command("status")
def funding_status(
    deposit_id: Optional[str] = typer.Option(None, "--deposit-id", "-d"),
    tx_hash: Optional[str] = typer.Option(None, "--tx-hash", "-t"),
) -> None:
    """Check the status of a deposit."""
    cfg, bot = _init()
    from polybot.bridge import BridgeClient

    bridge = BridgeClient(cfg, bot.db)
    try:
        status = bridge.get_deposit_status(deposit_id=deposit_id, tx_hash=tx_hash)
        typer.echo(json.dumps(status, indent=2))
    except ValueError as ve:
        typer.echo(f"Error: {ve}", err=True)
        raise typer.Exit(1)
    except Exception as exc:
        typer.echo(f"Error checking deposit status: {exc}", err=True)
        raise typer.Exit(1)


# ── Scan ─────────────────────────────────────────────────────────────


@app.command("scan")
def scan(
    strategy: str = typer.Option("underdog", "--strategy", "-s", help="Strategy name (underdog, arb)"),
    limit: int = typer.Option(20, "--limit", "-l", help="Max opportunities to return"),
) -> None:
    """Scan markets for opportunities without placing orders."""
    cfg, bot = _init()
    logger = logging.getLogger(__name__)

    try:
        results = bot.scan_only(strategy, limit=limit)
    except ValueError as ve:
        typer.echo(f"Error: {ve}", err=True)
        raise typer.Exit(1)
    except Exception as exc:
        typer.echo(f"Scan failed: {exc}", err=True)
        logger.exception("Scan failed")
        raise typer.Exit(1)

    if not results:
        typer.echo("No opportunities found.")
        return

    typer.echo(f"\n{'='*70}")
    typer.echo(f"  Found {len(results)} opportunities (strategy={strategy})")
    typer.echo(f"{'='*70}\n")

    for i, r in enumerate(results, 1):
        typer.echo(f"  #{i}")
        typer.echo(f"  Market:    {r['market']}")
        typer.echo(f"  Event:     {r['event']}")
        typer.echo(f"  Outcome:   {r['outcome']} ({r['side']})")
        typer.echo(f"  Price:     {r['price']}")
        typer.echo(f"  Size:      {r['size']}")
        typer.echo(f"  Volume:    {r['volume']}")
        typer.echo(f"  Liquidity: {r['liquidity']}")
        typer.echo(f"  Reason:    {r['reason']}")
        typer.echo()


# ── Run ──────────────────────────────────────────────────────────────


@app.command("run")
def run(
    strategy: str = typer.Option("underdog", "--strategy", "-s", help="Strategy name"),
    interval: int = typer.Option(30, "--interval", "-i", help="Seconds between cycles"),
    once: bool = typer.Option(False, "--once", help="Run a single cycle then exit"),
) -> None:
    """Run the bot (loop or single cycle)."""
    cfg, bot = _init()
    logger = logging.getLogger(__name__)

    typer.echo(f"Mode: {cfg.mode} | Dry-run: {cfg.dry_run} | Strategy: {strategy}")
    typer.echo(f"Budget: ${cfg.daily_budget_usd}/day | Max bet: ${cfg.max_bet_usd}")
    typer.echo()

    if cfg.is_live:
        typer.echo("*** LIVE MODE -- REAL ORDERS WILL BE PLACED ***")
        if not typer.confirm("Continue?"):
            raise typer.Abort()

    try:
        if once:
            summary = bot.run_once(strategy)
            typer.echo(json.dumps(summary, indent=2, default=str))
        else:
            bot.run_loop(strategy, interval_seconds=interval)
    except Exception as exc:
        logger.exception("Bot run failed")
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)


# ── Orders ───────────────────────────────────────────────────────────


@orders_app.command("open")
def orders_open() -> None:
    """Show currently open orders."""
    cfg, bot = _init()
    orders = bot.db.get_open_orders()

    if not orders:
        typer.echo("No open orders.")
        return

    typer.echo(f"\n  Open Orders ({len(orders)}):\n")
    for o in orders:
        typer.echo(
            f"  {o['id'][:16]}...  {o['side']:4s}  "
            f"price={o['price']}  size={o['size']}  "
            f"status={o['status']}  token={o['token_id'][:16]}..."
        )
    typer.echo()


@orders_app.command("cancel-all")
def orders_cancel_all() -> None:
    """PANIC: Cancel all open orders immediately."""
    cfg, bot = _init()
    typer.echo("Cancelling ALL open orders...")
    result = bot.panic()
    if result.get("success"):
        typer.echo("All orders cancelled successfully.")
    else:
        typer.echo(f"Cancel failed: {result.get('error', 'unknown')}", err=True)


# ── Positions ────────────────────────────────────────────────────────


@app.command("positions")
def positions(
    address: Optional[str] = typer.Option(None, "--address", "-a", help="Override FUNDER_ADDRESS"),
) -> None:
    """Show current positions from the Data API."""
    cfg, bot = _init()

    try:
        pos = bot.data_api.get_positions(address=address)
    except Exception as exc:
        typer.echo(f"Error fetching positions: {exc}", err=True)
        raise typer.Exit(1)

    if not pos:
        typer.echo("No positions found.")
        return

    typer.echo(f"\n  Positions ({len(pos)}):\n")
    for p in pos:
        typer.echo(f"  {json.dumps(p, indent=4)}")
    typer.echo()


# ── Backtest ─────────────────────────────────────────────────────────


@app.command("backtest")
def backtest(
    limit: int = typer.Option(100, "--limit", "-l", help="Max orders to review"),
) -> None:
    """Replay logged trades and compute basic PnL summary.

    This is a simplified backtest that reviews your own order history
    stored in the local database.  It does NOT fetch resolution data
    from Polymarket (that would require additional API integration).
    """
    cfg, bot = _init()
    orders = bot.db.get_all_orders(limit=limit)
    opportunities = bot.db.get_all_opportunities(limit=limit)

    if not orders:
        typer.echo("No orders in database to backtest.")
        return

    from decimal import Decimal

    total_cost = Decimal("0")
    total_orders = len(orders)
    by_status: dict[str, int] = {}
    by_strategy: dict[str, int] = {}

    for o in orders:
        price = Decimal(o["price"])
        size = Decimal(o["size"])
        cost = price * size
        total_cost += cost
        by_status[o["status"]] = by_status.get(o["status"], 0) + 1

    for opp in opportunities:
        by_strategy[opp["strategy"]] = by_strategy.get(opp["strategy"], 0) + 1

    typer.echo(f"\n{'='*50}")
    typer.echo(f"  BACKTEST SUMMARY (last {limit} orders)")
    typer.echo(f"{'='*50}")
    typer.echo(f"  Total orders:    {total_orders}")
    typer.echo(f"  Total cost:      ${total_cost:.2f}")
    typer.echo(f"  Avg cost/order:  ${(total_cost / total_orders):.2f}" if total_orders else "")
    typer.echo(f"\n  By status:")
    for status, count in sorted(by_status.items()):
        typer.echo(f"    {status:20s}: {count}")
    typer.echo(f"\n  By strategy:")
    for strat, count in sorted(by_strategy.items()):
        typer.echo(f"    {strat:20s}: {count}")
    typer.echo()
    typer.echo(
        "  Note: PnL requires resolution data. This summary shows order\n"
        "  history only. Extend with resolved-market lookups for full PnL."
    )
    typer.echo(f"{'='*50}\n")


if __name__ == "__main__":
    app()
