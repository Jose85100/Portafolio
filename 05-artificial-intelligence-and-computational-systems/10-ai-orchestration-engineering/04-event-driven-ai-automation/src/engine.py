"""Local transactional inbox. No claim of distributed exactly-once delivery."""
from __future__ import annotations
from dataclasses import dataclass
import re
import sqlite3
from pathlib import Path

_ID = re.compile(r"^[A-Za-z0-9_-]{1,40}$")

@dataclass(frozen=True)
class Event:
    event_id: str
    amount: int

def valid(event: Event) -> bool:
    return (
        isinstance(event.event_id, str)
        and bool(_ID.fullmatch(event.event_id))
        and type(event.amount) is int
        and 0 <= event.amount <= 1000
    )

class InjectedFault(RuntimeError):
    """Controlled crash between the effect write and transaction commit."""

class Inbox:
    def __init__(self, database: str | Path = ":memory:") -> None:
        self.db = sqlite3.connect(str(database), isolation_level=None)
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS inbox (
                event_id TEXT PRIMARY KEY,
                amount INTEGER NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('pending','done')),
                attempts INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS effects (
                event_id TEXT PRIMARY KEY REFERENCES inbox(event_id),
                amount INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS dlq (
                delivery_key TEXT PRIMARY KEY,
                reason TEXT NOT NULL
            );
        """)
        self.duplicates = 0
        self.conflicts = 0
        self.invalid = 0
        self.faults = 0
        self._faulted: set[str] = set()

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> Inbox:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def receive(self, event: Event, fail_once: set[str] | frozenset[str] = frozenset()) -> str:
        """Durably admit an event and attempt its local effect. Returns a status."""
        if not valid(event):
            self.invalid += 1
            key = f"invalid-{self.invalid}"
            self.db.execute("INSERT INTO dlq VALUES (?, ?)", (key, "invalid_schema"))
            return "invalid"
        row = self.db.execute(
            "SELECT amount FROM inbox WHERE event_id=?", (event.event_id,)
        ).fetchone()
        if row is not None:
            if row[0] != event.amount:
                self.conflicts += 1
                return "conflict"
            self.duplicates += 1
            return "duplicate"
        self.db.execute(
            "INSERT INTO inbox(event_id,amount,status) VALUES (?,?,'pending')",
            (event.event_id, event.amount),
        )
        self.attempt(event.event_id, fail_once)
        return "accepted"

    def attempt(self, event_id: str, fail_once: set[str] | frozenset[str] = frozenset()) -> bool:
        row = self.db.execute(
            "SELECT amount,status FROM inbox WHERE event_id=?", (event_id,)
        ).fetchone()
        if row is None:
            raise KeyError(event_id)
        if row[1] == "done":
            return True
        self.db.execute("BEGIN IMMEDIATE")
        try:
            self.db.execute(
                "INSERT INTO effects(event_id,amount) VALUES (?,?)", (event_id, row[0])
            )
            if event_id in fail_once and event_id not in self._faulted:
                self._faulted.add(event_id)
                raise InjectedFault(event_id)
            self.db.execute(
                "UPDATE inbox SET status='done',attempts=attempts+1 WHERE event_id=?",
                (event_id,),
            )
            self.db.execute("COMMIT")
            return True
        except InjectedFault:
            self.db.execute("ROLLBACK")
            self.db.execute(
                "UPDATE inbox SET attempts=attempts+1 WHERE event_id=?", (event_id,)
            )
            self.faults += 1
            return False
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def drain(self) -> int:
        """Retry pending events once; injected faults are one-shot."""
        pending = [r[0] for r in self.db.execute(
            "SELECT event_id FROM inbox WHERE status='pending' ORDER BY event_id"
        )]
        for event_id in pending:
            self.attempt(event_id)
        return len(pending)

    def totals(self) -> tuple[int, int]:
        row = self.db.execute("SELECT COUNT(*),COALESCE(SUM(amount),0) FROM effects").fetchone()
        assert row is not None
        return int(row[0]), int(row[1])

    def pending(self) -> int:
        return int(self.db.execute(
            "SELECT COUNT(*) FROM inbox WHERE status='pending'"
        ).fetchone()[0])

    def assert_integrity(self) -> None:
        assert self.pending() == 0
        assert self.db.execute(
            "SELECT COUNT(*) FROM effects e LEFT JOIN inbox i USING(event_id) "
            "WHERE i.status IS NULL OR i.status!='done' OR e.amount!=i.amount"
        ).fetchone()[0] == 0
        assert self.db.execute(
            "SELECT COUNT(*) FROM inbox WHERE status='done'"
        ).fetchone()[0] == self.totals()[0]
