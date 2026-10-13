"""Pipeline medallon (bronce -> plata -> oro) sobre SQLite: transaccional, idempotente por lote e independiente del orden."""
from __future__ import annotations
import hashlib
import json
import sqlite3
from dataclasses import replace
import pandas as pd
from .contracts import Contract, Field, validate

EVENTS_CONTRACT = Contract("events", 1, (Field("event_id", "str"), Field("category", "str", allowed=("A", "B", "C", "D")), Field("amount", "float", min=0.0, max=1e6),
                                         Field("event_time", "timestamp")), primary_key=("event_id",))


class SimulatedCrash(Exception):
    """Falla inyectada para probar la atomicidad."""


def _rowhash(row) -> str:
    return hashlib.sha256(json.dumps([row["event_id"], row["category"], round(float(row["amount"]), 9), row["event_time"]], sort_keys=True).encode()).hexdigest()[:16]


class Pipeline:
    """Reglas: (1) un lote se aplica una sola vez (batch_id); (2) todo el lote o nada (transaccion); (3) por evento gana el de mayor
    (event_time, batch_id, huella_de_fila): el resultado no depende del orden de llegada; (4) el oro se recalcula solo para las fechas afectadas."""
    def __init__(self, path: str = ":memory:", contract: Contract = EVENTS_CONTRACT, allowed_lateness: pd.Timedelta = pd.Timedelta(hours=1)):
        self.con = sqlite3.connect(path); self.con.execute("PRAGMA foreign_keys=ON"); self.contract, self.lateness = contract, allowed_lateness
        self.con.executescript("""
        CREATE TABLE IF NOT EXISTS bronze_events(batch_id TEXT, row_n INTEGER, raw_json TEXT);
        CREATE TABLE IF NOT EXISTS batches(batch_id TEXT PRIMARY KEY, n_rows INTEGER, n_valid INTEGER, n_quarantine INTEGER, n_late INTEGER, n_superseded INTEGER);
        CREATE TABLE IF NOT EXISTS silver_events(event_id TEXT PRIMARY KEY, category TEXT, amount REAL, event_time TEXT, batch_id TEXT, rowhash TEXT);
        CREATE TABLE IF NOT EXISTS quarantine_events(batch_id TEXT, reason TEXT, raw_json TEXT);
        CREATE TABLE IF NOT EXISTS gold_daily(day TEXT, category TEXT, n INTEGER, total REAL, PRIMARY KEY(day, category));
        CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT);""")

    # ---------------- ingesta ----------------
    def watermark(self):
        r = self.con.execute("SELECT v FROM meta WHERE k='watermark'").fetchone(); return pd.Timestamp(r[0]) if r else None

    def ingest(self, df: pd.DataFrame, batch_id: str, fail_after_rows: int | None = None) -> dict:
        if self.con.execute("SELECT 1 FROM batches WHERE batch_id=?", (batch_id,)).fetchone(): return {"status": "duplicate_batch", "batch_id": batch_id}
        # La llave primaria NO se valida por lote: en un flujo con correcciones el mismo evento puede llegar varias veces en un lote
        # y la version vigente se decide por (event_time, huella), no por el orden de las filas. Quitarla del contrato de validacion evita
        # enviar a cuarentena una correccion legitima (error real que detecto la prueba de caos del notebook).
        rep = validate(df, replace(self.contract, primary_key=())); valid = rep.valid_rows.copy()
        valid["event_time"] = pd.to_datetime(valid["event_time"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        valid["amount"] = valid["amount"].astype(float); valid["rowhash"] = valid.apply(_rowhash, axis=1)
        n_validas = len(valid); valid = valid.sort_values(["event_id", "event_time", "rowhash"]).drop_duplicates("event_id", keep="last"); n_super = n_validas - len(valid)      # la mejor version de cada evento dentro del lote
        wm = self.watermark(); late = 0
        if wm is not None and len(valid): late = int((pd.to_datetime(valid["event_time"], utc=True) < wm - self.lateness).sum())
        try:
            with self.con:                                                                                                  # transaccion: todo o nada
                self.con.executemany("INSERT INTO bronze_events VALUES (?,?,?)", [(batch_id, i, json.dumps(r, default=str)) for i, r in enumerate(df.to_dict("records"))])
                if len(rep.quarantine): self.con.executemany("INSERT INTO quarantine_events VALUES (?,?,?)", [(batch_id, r["_reason"], json.dumps({k: v for k, v in r.items() if k != "_reason"}, default=str)) for r in rep.quarantine.to_dict("records")])
                afectadas = set()
                for i, r in enumerate(valid.to_dict("records")):
                    if fail_after_rows is not None and i >= fail_after_rows: raise SimulatedCrash(f"caida tras {i} filas")
                    viejo = self.con.execute("SELECT event_time FROM silver_events WHERE event_id=?", (r["event_id"],)).fetchone()
                    cur = self.con.execute("""INSERT INTO silver_events VALUES (?,?,?,?,?,?) ON CONFLICT(event_id) DO UPDATE SET category=excluded.category, amount=excluded.amount, event_time=excluded.event_time,
                        batch_id=excluded.batch_id, rowhash=excluded.rowhash WHERE excluded.event_time > silver_events.event_time OR (excluded.event_time = silver_events.event_time AND
                        (excluded.batch_id > silver_events.batch_id OR (excluded.batch_id = silver_events.batch_id AND excluded.rowhash > silver_events.rowhash)))""",
                                           (r["event_id"], r["category"], r["amount"], r["event_time"], batch_id, r["rowhash"]))
                    if cur.rowcount:
                        afectadas.add(r["event_time"][:10])
                        if viejo: afectadas.add(viejo[0][:10])
                self._recompute_gold(afectadas)
                if len(valid):
                    nuevo = max(valid["event_time"]); self.con.execute("INSERT INTO meta VALUES('watermark',?) ON CONFLICT(k) DO UPDATE SET v=MAX(v, excluded.v)", (nuevo,))
                self.con.execute("INSERT INTO batches VALUES (?,?,?,?,?,?)", (batch_id, len(df), len(valid), len(rep.quarantine), late, n_super))
        except SimulatedCrash:
            return {"status": "crashed", "batch_id": batch_id}
        return {"status": "ok", "batch_id": batch_id, "valid": len(valid), "quarantined": len(rep.quarantine), "superseded_in_batch": n_super, "late": late, "dates_recomputed": sorted(afectadas)}

    def _recompute_gold(self, dias):
        for d in dias:
            self.con.execute("DELETE FROM gold_daily WHERE day=?", (d,))
            self.con.execute("INSERT INTO gold_daily SELECT substr(event_time,1,10), category, COUNT(*), ROUND(SUM(amount), 6) FROM silver_events WHERE substr(event_time,1,10)=? GROUP BY 1,2", (d,))

    # ---------------- lectura y verificacion ----------------
    def silver(self) -> pd.DataFrame: return pd.read_sql("SELECT event_id, category, amount, event_time FROM silver_events ORDER BY event_id", self.con)
    def gold(self) -> pd.DataFrame: return pd.read_sql("SELECT * FROM gold_daily ORDER BY day, category", self.con)
    def quarantine(self) -> pd.DataFrame: return pd.read_sql("SELECT * FROM quarantine_events ORDER BY batch_id, reason", self.con)
    def batches(self) -> pd.DataFrame: return pd.read_sql("SELECT * FROM batches ORDER BY batch_id", self.con)

    def full_rebuild_gold(self) -> pd.DataFrame:
        return pd.read_sql("SELECT substr(event_time,1,10) AS day, category, COUNT(*) AS n, ROUND(SUM(amount), 6) AS total FROM silver_events GROUP BY 1,2 ORDER BY 1,2", self.con)

    def assert_gold_consistent(self) -> None:
        a, b = self.gold().reset_index(drop=True), self.full_rebuild_gold().reset_index(drop=True)
        if not a.equals(b): raise AssertionError("oro incremental distinto del reconstruido")

    def close(self) -> None:
        self.con.close()

    def __enter__(self): return self

    def __exit__(self, *exc): self.close()
