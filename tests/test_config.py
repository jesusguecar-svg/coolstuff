"""Minimal config and DB smoke tests."""

from __future__ import annotations

import os
import tempfile
from decimal import Decimal

import pytest


def test_config_defaults():
    """Config loads with safe defaults when env vars are set minimally."""
    os.environ["PRIVATE_KEY"] = "0x" + "ab" * 32
    os.environ["MODE"] = "paper"
    os.environ["DRY_RUN"] = "true"

    from polybot.config import Config

    cfg = Config()
    assert cfg.mode == "paper"
    assert cfg.dry_run is True
    assert cfg.max_bet_usd == Decimal("1.00")
    assert cfg.daily_budget_usd == Decimal("5.00")
    assert cfg.is_live is False


def test_config_invalid_mode():
    os.environ["PRIVATE_KEY"] = "0x" + "ab" * 32
    os.environ["MODE"] = "yolo"

    from polybot.config import Config

    with pytest.raises(ValueError, match="MODE must be paper|shadow|live"):
        Config()

    os.environ["MODE"] = "paper"  # reset


def test_database_schema():
    """DB initialises tables without error."""
    from polybot.db import Database

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db = Database(f.name)

    # Basic CRUD
    run_id = db.start_run("paper", "test")
    assert run_id >= 1

    db.finish_run(run_id, errors=0)

    # Spend tracking
    db.record_spend(Decimal("1.50"), order_id="test-001")
    assert db.daily_spend() >= Decimal("1.50")

    # API creds
    db.save_api_creds("key", "secret", "pass")
    creds = db.load_api_creds()
    assert creds is not None
    assert creds["api_key"] == "key"


def test_round_to_tick():
    """Tick-size rounding works correctly."""
    from polybot.execution import round_to_tick

    assert round_to_tick(Decimal("0.567"), Decimal("0.01")) == Decimal("0.56")
    assert round_to_tick(Decimal("0.561"), Decimal("0.01")) == Decimal("0.56")
    assert round_to_tick(Decimal("0.50"), Decimal("0.01")) == Decimal("0.50")
    assert round_to_tick(Decimal("0.5678"), Decimal("0.001")) == Decimal("0.567")


def test_round_size_up():
    """Min-size enforcement works."""
    from polybot.execution import round_size_up

    assert round_size_up(Decimal("3"), Decimal("5")) == Decimal("5")
    assert round_size_up(Decimal("10"), Decimal("5")) == Decimal("10")
