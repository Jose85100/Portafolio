"""Dimension de cambio lento tipo 2 en SQLite: historial con intervalos de vigencia contiguos."""
from __future__ import annotations
import sqlite3
import pandas as pd


class SCD2:
    """Invariante por llave: intervalos [valid_from, valid_to) contiguos y sin solape, con exactamente una fila abierta (valid_to NULL)."""
    def __init__(self, key: str, tracked: list[str], con: sqlite3.Connection | None = None):
        self.key, self.tracked = key, list(tracked); self.con = con or sqlite3.connect(":memory:")
        cols = ", ".join(f"{c} TEXT" for c in self.tracked)
        self.con.execute(f"CREATE TABLE IF NOT EXISTS dim({key} TEXT, {cols}, valid_from TEXT, valid_to TEXT)")
        self.stale_changes = 0

    def _current(self, k):
        r = self.con.execute(f"SELECT {', '.join(self.tracked)}, valid_from FROM dim WHERE {self.key}=? AND valid_to IS NULL", (k,)).fetchone(); return r

    def apply_changes(self, df: pd.DataFrame, effective_ts: str = "effective_ts") -> dict:
        """Aplica cambios ordenados por `effective_ts` dentro de cada llave. Idempotente: repetir un lote no cambia nada.
        Un cambio con effective_ts anterior a la vigencia abierta se descarta y se cuenta en `stale_changes`."""
        cerrados = abiertos = 0
        with self.con:
            for k, g in df.sort_values([self.key, effective_ts]).groupby(self.key, sort=True):
                for r in g.to_dict("records"):
                    ts = pd.Timestamp(r[effective_ts]).isoformat(); vals = tuple(str(r[c]) for c in self.tracked); cur = self._current(k)
                    if cur is None:
                        self.con.execute(f"INSERT INTO dim VALUES (?{', ?' * len(self.tracked)}, ?, NULL)", (str(k), *vals, ts)); abiertos += 1; continue
                    if ts < cur[-1]: self.stale_changes += 1; continue
                    if tuple(cur[:-1]) == vals: continue
                    if ts == cur[-1]:                                  # mismo instante: se reemplaza la version abierta
                        self.con.execute(f"UPDATE dim SET {', '.join(c + '=?' for c in self.tracked)} WHERE {self.key}=? AND valid_to IS NULL", (*vals, str(k))); continue
                    self.con.execute(f"UPDATE dim SET valid_to=? WHERE {self.key}=? AND valid_to IS NULL", (ts, str(k)))
                    self.con.execute(f"INSERT INTO dim VALUES (?{', ?' * len(self.tracked)}, ?, NULL)", (str(k), *vals, ts)); cerrados += 1; abiertos += 1
        return {"closed": cerrados, "opened": abiertos}

    def table(self) -> pd.DataFrame: return pd.read_sql(f"SELECT * FROM dim ORDER BY {self.key}, valid_from", self.con)

    def as_of(self, ts: str) -> pd.DataFrame:
        t = pd.Timestamp(ts).isoformat()
        return pd.read_sql(f"SELECT * FROM dim WHERE valid_from <= ? AND (valid_to IS NULL OR ? < valid_to) ORDER BY {self.key}", self.con, params=(t, t))

    def check_invariants(self) -> list[str]:
        problemas = []; t = self.table()
        for k, g in t.groupby(self.key):
            g = g.sort_values("valid_from"); abiertas = g.valid_to.isna().sum()
            if abiertas != 1: problemas.append(f"{k}: {abiertas} filas abiertas")
            ends = g.valid_to.iloc[:-1].tolist(); starts = g.valid_from.iloc[1:].tolist()
            if ends != starts: problemas.append(f"{k}: intervalos no contiguos")
            if (g.valid_to.dropna() <= g.valid_from[g.valid_to.notna()]).any(): problemas.append(f"{k}: intervalo vacio o negativo")
        return problemas

    def close(self) -> None:
        self.con.close()

    def __enter__(self): return self

    def __exit__(self, *exc): self.close()
