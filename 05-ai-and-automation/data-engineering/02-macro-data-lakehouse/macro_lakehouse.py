"""Point-in-time macro vintage store with SQLite."""
import datetime as dt
import math
import sqlite3

class VintageStore:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.execute("""CREATE TABLE IF NOT EXISTS observations (
            series TEXT NOT NULL, observation_date TEXT NOT NULL,
            release_date TEXT NOT NULL, value REAL NOT NULL,
            PRIMARY KEY(series, observation_date, release_date))""")

    def ingest(self, series, observation_date, release_date, value):
        if not series.strip():
            raise ValueError("empty series")
        observation = dt.date.fromisoformat(observation_date)
        release = dt.date.fromisoformat(release_date)
        if release < observation or not math.isfinite(float(value)):
            raise ValueError("invalid release or value")
        self.db.execute("INSERT OR REPLACE INTO observations VALUES (?, ?, ?, ?)",
                        (series, observation.isoformat(), release.isoformat(), float(value)))
        self.db.commit()

    def as_of(self, series, cutoff):
        dt.date.fromisoformat(cutoff)
        rows = self.db.execute("""SELECT observation_date, value FROM (
            SELECT observation_date, value, ROW_NUMBER() OVER (
                PARTITION BY observation_date ORDER BY release_date DESC) AS rank
            FROM observations WHERE series=? AND release_date<=?
        ) WHERE rank=1 ORDER BY observation_date""", (series, cutoff))
        return [(date, value) for date, value in rows]

    def close(self):
        self.db.close()
