"""SQLite persistence layer.

Handles schema creation, migrations, and typed helpers for every table
required by the bot (api_creds_cache, runs, opportunities, orders,
spend_tracking, deposits, watched_wallets).
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Generator

_SCHEMA = """
CREATE TABLE IF NOT EXISTS api_creds_cache (
    id           INTEGER PRIMARY KEY CHECK (id = 1),
    api_key      TEXT NOT NULL,
    api_secret   TEXT NOT NULL,
    api_passphrase TEXT NOT NULL,
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS runs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at   TEXT NOT NULL,
    finished_at  TEXT,
    mode         TEXT NOT NULL,
    strategy     TEXT,
    errors       INTEGER DEFAULT 0,
    notes        TEXT
);

CREATE TABLE IF NOT EXISTS opportunities (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id       INTEGER,
    strategy     TEXT NOT NULL,
    market_id    TEXT NOT NULL,
    question     TEXT,
    token_id     TEXT NOT NULL,
    outcome      TEXT,
    side         TEXT NOT NULL,
    price        TEXT NOT NULL,
    size         TEXT NOT NULL,
    reason       TEXT,
    created_at   TEXT NOT NULL,
    FOREIGN KEY (run_id) REFERENCES runs(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id           TEXT PRIMARY KEY,
    opportunity_id INTEGER,
    market_id    TEXT NOT NULL,
    token_id     TEXT NOT NULL,
    side         TEXT NOT NULL,
    price        TEXT NOT NULL,
    size         TEXT NOT NULL,
    order_type   TEXT NOT NULL DEFAULT 'GTC',
    status       TEXT NOT NULL DEFAULT 'pending',
    raw_payload  TEXT,
    response     TEXT,
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL,
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
);

CREATE TABLE IF NOT EXISTS spend_tracking (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    date         TEXT NOT NULL,
    amount_usd   TEXT NOT NULL,
    order_id     TEXT,
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS deposits (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    deposit_address TEXT,
    asset        TEXT,
    chain        TEXT,
    status       TEXT DEFAULT 'pending',
    amount       TEXT,
    tx_hash      TEXT,
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS watched_wallets (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    address      TEXT NOT NULL UNIQUE,
    label        TEXT,
    active       INTEGER DEFAULT 1,
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS config_snapshot (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id       INTEGER,
    snapshot     TEXT NOT NULL,
    created_at   TEXT NOT NULL,
    FOREIGN KEY (run_id) REFERENCES runs(id)
);
"""


class Database:
    """Thin wrapper around sqlite3 with schema management."""

    def __init__(self, db_path: str = "polybot.db") -> None:
        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self.conn() as con:
            con.executescript(_SCHEMA)

    @contextmanager
    def conn(self) -> Generator[sqlite3.Connection, None, None]:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    # ── API Creds ────────────────────────────────────────────────────

    def save_api_creds(self, api_key: str, api_secret: str, api_passphrase: str) -> None:
        now = _now_iso()
        with self.conn() as con:
            con.execute(
                "INSERT OR REPLACE INTO api_creds_cache (id, api_key, api_secret, api_passphrase, created_at) "
                "VALUES (1, ?, ?, ?, ?)",
                (api_key, api_secret, api_passphrase, now),
            )

    def load_api_creds(self) -> dict[str, str] | None:
        with self.conn() as con:
            row = con.execute("SELECT api_key, api_secret, api_passphrase FROM api_creds_cache WHERE id=1").fetchone()
        if row:
            return {"api_key": row["api_key"], "api_secret": row["api_secret"], "api_passphrase": row["api_passphrase"]}
        return None

    # ── Runs ─────────────────────────────────────────────────────────

    def start_run(self, mode: str, strategy: str | None = None) -> int:
        with self.conn() as con:
            cur = con.execute(
                "INSERT INTO runs (started_at, mode, strategy) VALUES (?, ?, ?)",
                (_now_iso(), mode, strategy),
            )
            return cur.lastrowid  # type: ignore[return-value]

    def finish_run(self, run_id: int, errors: int = 0, notes: str | None = None) -> None:
        with self.conn() as con:
            con.execute(
                "UPDATE runs SET finished_at=?, errors=?, notes=? WHERE id=?",
                (_now_iso(), errors, notes, run_id),
            )

    # ── Opportunities ────────────────────────────────────────────────

    def record_opportunity(
        self,
        run_id: int | None,
        strategy: str,
        market_id: str,
        question: str | None,
        token_id: str,
        outcome: str | None,
        side: str,
        price: Decimal,
        size: Decimal,
        reason: str | None = None,
    ) -> int:
        with self.conn() as con:
            cur = con.execute(
                "INSERT INTO opportunities "
                "(run_id, strategy, market_id, question, token_id, outcome, side, price, size, reason, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (run_id, strategy, market_id, question, token_id, outcome, side, str(price), str(size), reason, _now_iso()),
            )
            return cur.lastrowid  # type: ignore[return-value]

    # ── Orders ───────────────────────────────────────────────────────

    def record_order(
        self,
        order_id: str,
        opportunity_id: int | None,
        market_id: str,
        token_id: str,
        side: str,
        price: Decimal,
        size: Decimal,
        order_type: str = "GTC",
        status: str = "pending",
        raw_payload: dict[str, Any] | None = None,
    ) -> None:
        now = _now_iso()
        with self.conn() as con:
            con.execute(
                "INSERT OR IGNORE INTO orders "
                "(id, opportunity_id, market_id, token_id, side, price, size, order_type, status, raw_payload, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    order_id,
                    opportunity_id,
                    market_id,
                    token_id,
                    side,
                    str(price),
                    str(size),
                    order_type,
                    status,
                    json.dumps(raw_payload) if raw_payload else None,
                    now,
                    now,
                ),
            )

    def update_order_status(self, order_id: str, status: str, response: dict[str, Any] | None = None) -> None:
        with self.conn() as con:
            con.execute(
                "UPDATE orders SET status=?, response=?, updated_at=? WHERE id=?",
                (status, json.dumps(response) if response else None, _now_iso(), order_id),
            )

    def get_open_orders(self) -> list[dict[str, Any]]:
        with self.conn() as con:
            rows = con.execute(
                "SELECT * FROM orders WHERE status IN ('pending', 'sent', 'accepted') ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def get_order(self, order_id: str) -> dict[str, Any] | None:
        with self.conn() as con:
            row = con.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
        return dict(row) if row else None

    def order_exists(self, order_id: str) -> bool:
        with self.conn() as con:
            row = con.execute("SELECT 1 FROM orders WHERE id=?", (order_id,)).fetchone()
        return row is not None

    # ── Spend Tracking ───────────────────────────────────────────────

    def record_spend(self, amount_usd: Decimal, order_id: str | None = None) -> None:
        with self.conn() as con:
            con.execute(
                "INSERT INTO spend_tracking (date, amount_usd, order_id, created_at) VALUES (?, ?, ?, ?)",
                (date.today().isoformat(), str(amount_usd), order_id, _now_iso()),
            )

    def daily_spend(self, target_date: date | None = None) -> Decimal:
        d = (target_date or date.today()).isoformat()
        with self.conn() as con:
            row = con.execute(
                "SELECT COALESCE(SUM(CAST(amount_usd AS REAL)), 0) AS total FROM spend_tracking WHERE date=?",
                (d,),
            ).fetchone()
        return Decimal(str(row["total"])) if row else Decimal("0")

    # ── Deposits ─────────────────────────────────────────────────────

    def record_deposit(self, deposit_address: str, asset: str, chain: str) -> int:
        now = _now_iso()
        with self.conn() as con:
            cur = con.execute(
                "INSERT INTO deposits (deposit_address, asset, chain, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (deposit_address, asset, chain, now, now),
            )
            return cur.lastrowid  # type: ignore[return-value]

    def update_deposit_status(self, deposit_id: int, status: str, amount: str | None = None, tx_hash: str | None = None) -> None:
        with self.conn() as con:
            con.execute(
                "UPDATE deposits SET status=?, amount=?, tx_hash=?, updated_at=? WHERE id=?",
                (status, amount, tx_hash, _now_iso(), deposit_id),
            )

    # ── Watched Wallets ──────────────────────────────────────────────

    def add_watched_wallet(self, address: str, label: str | None = None) -> None:
        with self.conn() as con:
            con.execute(
                "INSERT OR IGNORE INTO watched_wallets (address, label, created_at) VALUES (?, ?, ?)",
                (address, label, _now_iso()),
            )

    def get_watched_wallets(self) -> list[dict[str, Any]]:
        with self.conn() as con:
            rows = con.execute("SELECT * FROM watched_wallets WHERE active=1").fetchall()
        return [dict(r) for r in rows]

    # ── Config Snapshot ──────────────────────────────────────────────

    def save_config_snapshot(self, run_id: int, snapshot: dict[str, Any]) -> None:
        with self.conn() as con:
            con.execute(
                "INSERT INTO config_snapshot (run_id, snapshot, created_at) VALUES (?, ?, ?)",
                (run_id, json.dumps(snapshot, default=str), _now_iso()),
            )

    # ── Backtest helpers ─────────────────────────────────────────────

    def get_all_orders(self, limit: int = 200) -> list[dict[str, Any]]:
        with self.conn() as con:
            rows = con.execute(
                "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

    def get_all_opportunities(self, limit: int = 200) -> list[dict[str, Any]]:
        with self.conn() as con:
            rows = con.execute(
                "SELECT * FROM opportunities ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
