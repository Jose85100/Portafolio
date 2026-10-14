"""SQLite workflow recovery: naive, split checkpoint and atomic idempotent modes.

The effects are deliberately restricted to the same SQLite database as the
checkpoint. No exactly-once guarantee is claimed for remote tools/APIs.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Literal

Mode = Literal["naive", "split", "atomic"]
STEPS = ("reserve", "finalize")


class InjectedCrash(RuntimeError):
    """Deterministic failpoint after a committed effect."""


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path, timeout=5)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=FULL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def initialize(path: Path, mode: Mode) -> None:
    if mode not in ("naive", "split", "atomic"):
        raise ValueError("invalid mode")
    with closing(connect(path)) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS workflows (job_id TEXT PRIMARY KEY, next_step INTEGER NOT NULL DEFAULT 0 CHECK(next_step BETWEEN 0 AND 2), done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0,1)))")
        conn.execute("CREATE TABLE IF NOT EXISTS effects (effect_id INTEGER PRIMARY KEY, job_id TEXT NOT NULL, step TEXT NOT NULL, payload TEXT NOT NULL)")
        if mode == "atomic":
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS once_per_step ON effects(job_id,step)")


def run_job(path: Path, mode: Mode, job_id: str, crash_after_step: int | None = None) -> None:
    """Run a two-step job; crash_after_step is an injected, one-shot process death.

    Caller must catch InjectedCrash, discard connection and retry with None.
    SQLite transactions are committed before the exception is raised.
    """
    if not job_id or len(job_id) > 128:
        raise ValueError("job_id must have length 1..128")
    if crash_after_step is not None and crash_after_step not in (0, 1):
        raise ValueError("invalid crash point")
    with closing(connect(path)) as conn:
        conn.execute("INSERT OR IGNORE INTO workflows(job_id) VALUES (?)", (job_id,))
        conn.commit()
        next_step, done = conn.execute(
            "SELECT next_step,done FROM workflows WHERE job_id=?", (job_id,)
        ).fetchone()
        if done:
            return
        start = 0 if mode == "naive" else next_step
        for i in range(start, len(STEPS)):
            step = STEPS[i]
            if mode == "atomic":
                # One ACID transaction contains both the effect and its checkpoint.
                conn.execute("BEGIN IMMEDIATE")
                conn.execute(
                    "INSERT OR IGNORE INTO effects(job_id,step,payload) VALUES (?,?,?)",
                    (job_id, step, f"synthetic:{job_id}:{step}"),
                )
                conn.execute("UPDATE workflows SET next_step=? WHERE job_id=?", (i + 1, job_id))
                conn.commit()
            else:
                # A committed effect is not atomically coupled to the checkpoint.
                conn.execute(
                    "INSERT INTO effects(job_id,step,payload) VALUES (?,?,?)",
                    (job_id, step, f"synthetic:{job_id}:{step}"),
                )
                conn.commit()
            if crash_after_step == i:
                raise InjectedCrash(f"crash after committed effect: {job_id}/{step}")
            if mode == "split":
                conn.execute("UPDATE workflows SET next_step=? WHERE job_id=?", (i + 1, job_id))
                conn.commit()
        conn.execute("UPDATE workflows SET done=1,next_step=2 WHERE job_id=?", (job_id,))
        conn.commit()


def inspect(path: Path) -> dict[str, int]:
    with closing(connect(path)) as conn:
        jobs, completed = conn.execute("SELECT COUNT(*),COALESCE(SUM(done),0) FROM workflows").fetchone()
        total, distinct = conn.execute(
            "SELECT COUNT(*),COUNT(DISTINCT job_id || ':' || step) FROM effects"
        ).fetchone()
        bad_payloads = conn.execute(
            "SELECT COUNT(*) FROM effects WHERE payload != 'synthetic:' || job_id || ':' || step"
        ).fetchone()[0]
    return {"jobs": jobs, "completed": completed, "effect_rows": total,
            "unique_effects": distinct, "duplicate_effects": total - distinct,
            "bad_payloads": bad_payloads}
