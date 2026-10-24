"""Two independent SQLite transactions; no remote exactly-once assertion."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Literal

Mode = Literal["no_dedup", "key_only", "key_hash"]


class PayloadConflict(ValueError):
    """An existing idempotency key was reused with a different intent."""


class LostAcknowledgement(RuntimeError):
    """Injected crash after provider commit, before sender ACK."""


def connect(path: Path) -> sqlite3.Connection:
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA synchronous=FULL")
    return db


def fingerprint(amount: int) -> str:
    # Version/tenant/operation are part of the semantic envelope and key namespace.
    if type(amount) is not int or amount <= 0:
        raise ValueError("amount must be a positive integer")
    raw = json.dumps(
        {"version": 1, "operation": "synthetic_effect", "amount": amount},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode()).hexdigest()


def initialize(sender: Path, provider: Path) -> None:
    if sender.resolve() == provider.resolve():
        raise ValueError("sender and provider must be independent databases")
    with closing(connect(sender)) as db, db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS jobs (key TEXT PRIMARY KEY, amount INTEGER NOT NULL)"
        )
        db.execute(
            "CREATE TABLE IF NOT EXISTS outbox (key TEXT PRIMARY KEY, amount INTEGER NOT NULL, digest TEXT NOT NULL, ack INTEGER NOT NULL DEFAULT 0)"
        )
    with closing(connect(provider)) as db, db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS effects (id INTEGER PRIMARY KEY, key TEXT NOT NULL, amount INTEGER NOT NULL)"
        )
        db.execute(
            "CREATE TABLE IF NOT EXISTS receipts (key TEXT PRIMARY KEY, digest TEXT NOT NULL, effect_id INTEGER NOT NULL)"
        )


def enqueue(sender: Path, key: str, amount: int) -> None:
    digest = fingerprint(amount)
    if not key:
        raise ValueError("nonempty namespaced key required")
    with closing(connect(sender)) as db, db:
        db.execute("BEGIN IMMEDIATE")
        old = db.execute("SELECT digest FROM outbox WHERE key=?", (key,)).fetchone()
        if old:
            if old[0] != digest:
                raise PayloadConflict(key)
            return
        db.execute("INSERT INTO jobs VALUES (?,?)", (key, amount))
        db.execute(
            "INSERT INTO outbox(key,amount,digest) VALUES (?,?,?)",
            (key, amount, digest),
        )


def apply(provider: Path, key: str, amount: int, mode: Mode) -> int:
    """Provider receipt and effect are atomic *inside provider* only."""
    if mode not in ("no_dedup", "key_only", "key_hash"):
        raise ValueError("unknown policy")
    if not key:
        raise ValueError("nonempty key required")
    digest = fingerprint(amount)
    with closing(connect(provider)) as db, db:
        db.execute("BEGIN IMMEDIATE")
        if mode != "no_dedup":
            old = db.execute(
                "SELECT digest,effect_id FROM receipts WHERE key=?", (key,)
            ).fetchone()
            if old:
                if mode == "key_hash" and old[0] != digest:
                    raise PayloadConflict(key)
                return int(old[1])
        cursor = db.execute(
            "INSERT INTO effects(key,amount) VALUES (?,?)", (key, amount)
        )
        effect = int(cursor.lastrowid or 0)
        if mode != "no_dedup":
            db.execute("INSERT INTO receipts VALUES (?,?,?)", (key, digest, effect))
        return effect


def dispatch(
    sender: Path,
    provider: Path,
    key: str,
    mode: Mode,
    crash_after_provider: bool = False,
    hard_exit: bool = False,
) -> bool:
    """One delivery attempt; crashes leave pending outbox for later retry."""
    with closing(connect(sender)) as db:
        row = db.execute("SELECT amount,ack FROM outbox WHERE key=?", (key,)).fetchone()
    if row is None:
        raise KeyError(key)
    if row[1]:
        return False
    apply(provider, key, int(row[0]), mode)
    if crash_after_provider:
        if hard_exit:
            __import__("os")._exit(77)
        raise LostAcknowledgement(key)
    with closing(connect(sender)) as db, db:
        db.execute("UPDATE outbox SET ack=1 WHERE key=?", (key,))
    return True


def metrics(sender: Path, provider: Path) -> dict[str, int]:
    with closing(connect(sender)) as db:
        jobs = int(db.execute("SELECT count(*) FROM jobs").fetchone()[0])
        ack = int(db.execute("SELECT coalesce(sum(ack),0) FROM outbox").fetchone()[0])
    with closing(connect(provider)) as db:
        effects = int(db.execute("SELECT count(*) FROM effects").fetchone()[0])
        distinct = int(
            db.execute("SELECT count(DISTINCT key) FROM effects").fetchone()[0]
        )
    return {
        "jobs": jobs,
        "acknowledged": ack,
        "effects": effects,
        "duplicates": effects - distinct,
        "missing_effects": jobs - distinct,
    }
