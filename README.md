# Polybot -- Educational Polymarket Trading Bot

**WARNING: This is an educational project. It is NOT financial advice. Trading
prediction markets involves real financial risk. You can lose your entire
investment. Use at your own risk.**

## What This Bot Does

Polybot is an MVP trading bot for [Polymarket](https://polymarket.com), a
decentralized prediction market on Polygon where binary outcome shares (YES/NO)
are priced between 0 and 1 (representing implied probability).

The bot follows this pipeline:

```
Gamma API (discover markets)
    -> CLOB API (fetch order books, real prices)
        -> Strategy (evaluate edge)
            -> Risk Manager (enforce guardrails)
                -> Execution Engine (validate & submit)
                    -> SQLite (persist state)
```

## Strategies

### Strategy A: Binary Intra-Market Arbitrage (`arb`)

For a binary market, if `best_ask(YES) + best_ask(NO) < 1 - MIN_ARB_EDGE`,
there is a theoretical arbitrage: buying both sides for less than $1 guarantees
$1 at resolution.

**Why arb is not always risk-free:**
- **Slippage**: asks can move between your two leg orders.
- **Partial fills**: you may buy only one side, leaving directional exposure.
- **Resolution disputes**: ambiguous outcomes can delay or void payouts.
- **Fees**: trading fees reduce thin edges.
- **Timing**: the book can change between placing two orders.

### Strategy B: Underdog Threshold (`underdog`)

Discovers binary sports markets, identifies the underdog (lower-priced
outcome), and places a small limit buy when:
- Favorite price >= `FAVORITE_MIN_PRICE` (default 0.75)
- Underdog price <= `UNDERDOG_MAX_PRICE` (default 0.25)
- Book spread <= `MAX_SPREAD` (default 0.05)

### Future Strategies (scaffolded)

- **Market Maker**: two-sided quotes around midpoint
- **Weather Mispricing**: NOAA data vs market prices
- **Whale Copy**: follow profitable wallets
- **NegRisk Rebalance**: multi-outcome arbitrage

## Safety Modes

| Mode     | Behavior |
|----------|----------|
| `paper`  | Simulates fills, logs what would happen. No API calls to place orders. |
| `shadow` | Observes real markets and computes signals, but does NOT place orders. |
| `live`   | Real orders. Requires explicit `DRY_RUN=false` to actually send. |

Default configuration is maximally safe: `MODE=paper` + `DRY_RUN=true`.

## Quick Start

### 1. Install

```bash
git clone <this-repo>
cd polybot
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env: set PRIVATE_KEY and FUNDER_ADDRESS
```

### 3. Run Demo

```bash
# Scan for opportunities (no orders placed)
python -m polybot scan --strategy underdog --limit 10
python -m polybot scan --strategy arb --limit 10

# Run a single paper-mode cycle
python -m polybot run --strategy underdog --once

# Run continuous loop (paper mode)
python -m polybot run --strategy arb --interval 30

# Or use the demo script:
bash scripts/run_demo.sh
```

## Funding from Base

Polymarket trading occurs on Polygon (chain ID 137). To fund your account
from Base (e.g., Coinbase Wallet), use the bridge helper:

```bash
# Step 1: Create a deposit address
python -m polybot funding deposit-address

# Step 2: The command will print instructions like:
#   Send USDC on Base to: 0x...
#   (Use Coinbase Wallet or any Base-compatible wallet)

# Step 3: Check deposit status
python -m polybot funding status --tx-hash 0x...
```

**Do NOT automate Coinbase withdrawals.** Manually send USDC on Base to the
printed deposit address. The bridge will credit your Polymarket wallet on
Polygon.

## CLI Reference

```
polybot funding deposit-address   Create deposit address for bridging
polybot funding supported-assets  Show supported deposit assets/chains
polybot funding status            Check deposit status

polybot scan -s underdog -l 20    Scan for underdog opportunities
polybot scan -s arb -l 50         Scan for arb opportunities

polybot run -s underdog -i 30     Run underdog strategy, 30s interval
polybot run -s arb -i 10          Run arb strategy, 10s interval
polybot run --once                Single cycle then exit

polybot orders open               Show open orders
polybot orders cancel-all         PANIC: cancel everything

polybot positions                 Show current positions
polybot backtest                  Review logged trade history
```

## Troubleshooting

### Tick Size Errors

```
INVALID_ORDER_MIN_TICK_SIZE
```

The bot automatically re-fetches the tick size and retries once. If it
persists, the market may have changed its tick-size configuration. Check:

```bash
python -m polybot scan -s arb -l 1  # observe logged tick sizes
```

### Minimum Size Errors

```
INVALID_ORDER_MIN_SIZE
```

The bot bumps the order size to the minimum and retries once. If your budget
is too small for the minimum order size, increase `MAX_BET_USD`.

### Insufficient Balance / Allowance

```
Insufficient balance or allowance
```

1. Check your balance: `python -m polybot positions`
2. Fund via bridge: `python -m polybot funding deposit-address`
3. Ensure the CLOB contract has token allowance (this is usually set during
   first trade via py-clob-client).

### Rate Limiting / Timeouts

The bot uses automatic retry with exponential backoff for HTTP 429/5xx.
If you see persistent rate-limit errors, increase `REQUEST_TIMEOUT_SECONDS`
and reduce scan frequency (increase `--interval`).

### "No opportunities found"

- The strategy filters are conservative by default. Try relaxing:
  - `MIN_LIQUIDITY=500`
  - `MIN_VOLUME=500`
  - `UNDERDOG_MAX_PRICE=0.35`
  - `MIN_ARB_EDGE=0.005`
- Markets may genuinely have no qualifying opportunities at the moment.

## Architecture

```
polybot/
  __init__.py          Package init
  __main__.py          Entry point for python -m polybot
  config.py            Environment-based configuration
  db.py                SQLite persistence (all tables)
  http.py              HTTP session with retry/backoff
  logging_setup.py     Structured logging + rotating file
  gamma.py             Gamma API client (market discovery)
  clob_client.py       py-clob-client wrapper (auth, orders)
  clob_rest.py         Public CLOB REST (order books, tick sizes)
  data_api.py          Data API (positions, history)
  bridge.py            Bridge API (deposits from Base)
  strategies/
    __init__.py         Strategy registry
    base.py             Abstract strategy interface
    underdog.py         Underdog threshold strategy
    arbitrage.py        Binary intra-market arb strategy
    market_maker_skeleton.py
    weather_skeleton.py
    whale_copy_skeleton.py
    negrisk_skeleton.py
  risk.py              Risk manager / guardrails
  execution.py         Order validation + submission engine
  bot.py               Main bot orchestrator
  cli.py               Typer CLI
scripts/
  run_demo.sh          Quick-start demo script
tests/
  test_config.py       Smoke tests
```

## Database Tables

| Table | Purpose |
|-------|---------|
| `api_creds_cache` | Cached L2 API credentials (derived once from private key) |
| `runs` | Timestamped run records with mode and error counts |
| `opportunities` | Every opportunity the bot identified |
| `orders` | Every order (pending, sent, accepted, filled, canceled) |
| `spend_tracking` | Daily spend tracking for budget enforcement |
| `deposits` | Bridge deposit addresses and statuses |
| `watched_wallets` | Wallet addresses for whale-copy strategy |
| `config_snapshot` | Configuration at time of each run |

## Sample Terminal Output

```
$ python -m polybot scan --strategy underdog --limit 3

======================================================================
  Found 3 opportunities (strategy=underdog)
======================================================================

  #1
  Market:    Will Team X win the championship?
  Event:     Championship Finals 2025
  Outcome:   No (BUY)
  Price:     0.18
  Size:      5
  Volume:    25000
  Liquidity: 12000
  Reason:    Underdog 'No' at 0.1800 (favorite at 0.8200). Spread OK. Size=5.

  #2
  Market:    Will Candidate A win the primary?
  Event:     State Primary Election
  Outcome:   No (BUY)
  Price:     0.22
  Size:      4
  Volume:    18000
  Liquidity: 8500
  Reason:    Underdog 'No' at 0.2200 (favorite at 0.7800). Spread OK. Size=4.

  #3
  Market:    Over/Under 45.5 points?
  Event:     Football Week 12
  Outcome:   Under (BUY)
  Price:     0.24
  Size:      4
  Volume:    31000
  Liquidity: 15000
  Reason:    Underdog 'Under' at 0.2400 (favorite at 0.7600). Spread OK. Size=4.
```

```
$ python -m polybot run --strategy underdog --once
Mode: paper | Dry-run: True | Strategy: underdog
Budget: $5.00/day | Max bet: $1.00

{
  "run_id": 1,
  "strategy": "underdog",
  "mode": "paper",
  "opportunities_found": 2,
  "executed": 2,
  "errors": 0,
  "results": [
    {
      "opportunity": "Underdog 'No' at 0.1800 ...",
      "success": true,
      "status": "simulated",
      "order_id": "sim-a1b2c3d4e5f6",
      "message": "[PAPER] Order simulated"
    }
  ]
}
```

## License

Educational use. No warranty. Not financial advice.
