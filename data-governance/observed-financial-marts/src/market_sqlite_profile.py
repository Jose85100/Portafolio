"""Read-only profiling of canonical InvestmentOS SQLite, without publication of raw."""
import argparse
import hashlib
import json
import math
import sqlite3
from pathlib import Path


def inspect(path, symbols=("SPY", "QQQ", "AAPL")):
    path = Path(path)
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
        tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {"prices", "macro_observations"}.issubset(tables):
            raise ValueError("Missing required market tables")
        cols = {r[1] for r in db.execute("PRAGMA table_info(prices)")}
        if not {"symbol", "date", "close", "adjusted_close", "high", "low", "open"}.issubset(cols):
            raise ValueError("Unexpected market price schema")
        report = {
            "prices_rows": db.execute("SELECT COUNT(*) FROM prices").fetchone()[0],
            "macro_rows": db.execute("SELECT COUNT(*) FROM macro_observations").fetchone()[0],
            "symbols_count": db.execute("SELECT COUNT(DISTINCT symbol) FROM prices").fetchone()[0],
            "earliest_latest": db.execute("SELECT min(date), max(date) FROM prices").fetchone(),
            "ohlc_inconsistencies": db.execute("SELECT COUNT(*) FROM prices WHERE high<low OR open>high OR open<low OR close>high OR close<low").fetchone()[0],
            "nonpositive_adjusted": db.execute("SELECT COUNT(*) FROM prices WHERE adjusted_close<=0").fetchone()[0],
            "raw_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "market_vintage_validated": False,
            "corporate_actions_validated": False,
            "status": "DESCRIPTIVE_AUDIT_ONLY",
        }
        report["per_symbol"] = []
        for symbol in symbols:
            x = db.execute("SELECT date,adjusted_close FROM prices WHERE symbol=? ORDER BY date", (symbol,)).fetchall()
            if len(x) < 30 or any(v is None or v<=0 for _,v in x):
                report["per_symbol"].append({"symbol":symbol,"status":"NOT_ELIGIBLE"})
                continue
            returns = [math.log(b[1]/a[1]) for a,b in zip(x,x[1:])]
            mean = sum(returns)/len(returns)
            volatility = math.sqrt(252*sum((r-mean)**2 for r in returns)/(len(returns)-1))
            report["per_symbol"].append({"symbol":symbol,"observations":len(x),"first":x[0][0],
                                         "last":x[-1][0],"annualized_volatility":volatility,
                                         "status":"DESCRIPTIVE_NOT_BACKTESTED"})
        return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--file",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    result=inspect(a.file)
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False))
