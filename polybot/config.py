"""Configuration loaded from environment / .env file.

All monetary values and prices use ``Decimal`` to avoid floating-point
rounding errors that would violate tick-size or minimum-size constraints.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv


def _load_env() -> None:
    """Load the nearest .env file (project root)."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)


_load_env()


def _env(key: str, default: str | None = None, *, required: bool = False) -> str:
    val = os.getenv(key, default)
    if required and not val:
        raise EnvironmentError(f"Required env var {key} is not set. See .env.example.")
    return val or ""


@dataclass(frozen=True)
class Config:
    """Immutable bot configuration."""

    # ── Auth ──────────────────────────────────────────────────────────
    private_key: str = field(repr=False, default_factory=lambda: _env("PRIVATE_KEY", required=True))
    funder_address: str = field(default_factory=lambda: _env("FUNDER_ADDRESS", default=""))
    signature_type: int = field(default_factory=lambda: int(_env("SIGNATURE_TYPE", "0")))

    # ── Mode / Safety ────────────────────────────────────────────────
    mode: str = field(default_factory=lambda: _env("MODE", "paper"))  # paper | shadow | live
    dry_run: bool = field(default_factory=lambda: _env("DRY_RUN", "true").lower() in ("true", "1", "yes"))

    # ── Budget / Risk ────────────────────────────────────────────────
    max_bet_usd: Decimal = field(default_factory=lambda: Decimal(_env("MAX_BET_USD", "1.00")))
    daily_budget_usd: Decimal = field(default_factory=lambda: Decimal(_env("DAILY_BUDGET_USD", "5.00")))
    max_open_orders: int = field(default_factory=lambda: int(_env("MAX_OPEN_ORDERS", "3")))

    # ── Strategy: underdog ───────────────────────────────────────────
    favorite_min_price: Decimal = field(default_factory=lambda: Decimal(_env("FAVORITE_MIN_PRICE", "0.75")))
    underdog_max_price: Decimal = field(default_factory=lambda: Decimal(_env("UNDERDOG_MAX_PRICE", "0.25")))

    # ── Strategy: arbitrage ──────────────────────────────────────────
    min_arb_edge: Decimal = field(default_factory=lambda: Decimal(_env("MIN_ARB_EDGE", "0.01")))

    # ── Market filters ───────────────────────────────────────────────
    min_liquidity: Decimal = field(default_factory=lambda: Decimal(_env("MIN_LIQUIDITY", "1000")))
    min_volume: Decimal = field(default_factory=lambda: Decimal(_env("MIN_VOLUME", "1000")))
    max_spread: Decimal = field(default_factory=lambda: Decimal(_env("MAX_SPREAD", "0.05")))
    max_slippage: Decimal = field(default_factory=lambda: Decimal(_env("MAX_SLIPPAGE", "0.05")))

    # ── Networking ───────────────────────────────────────────────────
    request_timeout: int = field(default_factory=lambda: int(_env("REQUEST_TIMEOUT_SECONDS", "15")))

    # ── Logging ──────────────────────────────────────────────────────
    log_level: str = field(default_factory=lambda: _env("LOG_LEVEL", "INFO"))

    # ── API base URLs ────────────────────────────────────────────────
    gamma_base: str = "https://gamma-api.polymarket.com"
    clob_base: str = "https://clob.polymarket.com"
    data_base: str = "https://data-api.polymarket.com"
    bridge_base: str = "https://bridge.polymarket.com"

    # ── Paths ────────────────────────────────────────────────────────
    db_path: str = field(default_factory=lambda: _env("DB_PATH", "polybot.db"))

    # ── Risk: error-rate stop ────────────────────────────────────────
    max_api_errors_per_window: int = 10
    api_error_window_seconds: int = 300
    min_wallet_balance_usd: Decimal = field(default_factory=lambda: Decimal("0.50"))

    # ── Chain ────────────────────────────────────────────────────────
    chain_id: int = 137  # Polygon

    def __post_init__(self) -> None:
        if self.mode not in ("paper", "shadow", "live"):
            raise ValueError(f"MODE must be paper|shadow|live, got '{self.mode}'")
        if self.private_key and self.private_key.startswith("0x"):
            pass  # valid hex key
        elif self.private_key:
            # Accept keys without 0x prefix
            object.__setattr__(self, "private_key", "0x" + self.private_key)

    @property
    def is_live(self) -> bool:
        return self.mode == "live" and not self.dry_run


def get_config() -> Config:
    """Return a fresh Config from the current environment."""
    return Config()
