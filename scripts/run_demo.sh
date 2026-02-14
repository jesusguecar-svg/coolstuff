#!/usr/bin/env bash
# run_demo.sh -- Quick-start demo for Polybot
#
# Prerequisites:
#   1. Copy .env.example to .env and set PRIVATE_KEY + FUNDER_ADDRESS
#   2. pip install -r requirements.txt
#
# This script runs the bot in paper mode (no real orders) to show
# how scanning and execution work.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "============================================"
echo "  Polybot Demo (paper mode)"
echo "============================================"
echo ""

# Ensure .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env not found. Copy .env.example to .env and configure it."
    exit 1
fi

echo "Step 1: Scanning for underdog opportunities..."
echo "----------------------------------------------"
python -m polybot scan --strategy underdog --limit 5
echo ""

echo "Step 2: Scanning for arbitrage opportunities..."
echo "------------------------------------------------"
python -m polybot scan --strategy arb --limit 5
echo ""

echo "Step 3: Running a single paper-mode cycle (underdog)..."
echo "-------------------------------------------------------"
python -m polybot run --strategy underdog --once
echo ""

echo "Step 4: Checking open orders..."
echo "-------------------------------"
python -m polybot orders open
echo ""

echo "Step 5: Checking positions..."
echo "-----------------------------"
python -m polybot positions
echo ""

echo "Step 6: Running backtest on logged trades..."
echo "---------------------------------------------"
python -m polybot backtest
echo ""

echo "============================================"
echo "  Demo complete!"
echo ""
echo "  Next steps:"
echo "    - Review logs/ directory for detailed output"
echo "    - Try: python -m polybot run --strategy arb --interval 30"
echo "    - To go live: set MODE=live and DRY_RUN=false in .env"
echo "    - To fund: python -m polybot funding deposit-address"
echo "============================================"
