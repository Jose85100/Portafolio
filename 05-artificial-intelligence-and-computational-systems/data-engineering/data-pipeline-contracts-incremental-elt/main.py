"""Demostracion corta: un flujo con duplicados, desorden, reenvios y correcciones; el pipeline converge a la verdad."""
import pathlib, sys
import numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))
from dataplatform.pipeline import Pipeline

rg = np.random.default_rng(0); n = 1500; t0 = pd.Timestamp("2024-03-01", tz="UTC")
base = pd.DataFrame({"event_id": [f"o{i}" for i in range(n)], "category": rg.choice(list("ABCD"), n), "amount": rg.lognormal(3.5, .8, n).round(2), "event_time": t0 + pd.to_timedelta(rg.integers(0, 5 * 86400, n), unit="s")})
corr = base.sample(frac=.15, random_state=1).copy(); corr["event_time"] += pd.Timedelta(hours=3); corr["amount"] = (corr.amount * 1.2).round(2)
verdad = pd.concat([base, corr]).sort_values(["event_id", "event_time"]).drop_duplicates("event_id", keep="last")
entregas = pd.concat([base, corr, base.sample(frac=.1, random_state=2)], ignore_index=True).sample(frac=1.0, random_state=3)
lotes = [(f"b{i}", entregas.iloc[i::12]) for i in range(12)]; lotes += lotes[:3]                                  # lotes reenviados completos
p = Pipeline()
for i in rg.permutation(len(lotes)): p.ingest(lotes[i][1], lotes[i][0])
s = p.silver().set_index("event_id"); v = verdad.set_index("event_id")
print(f"verdad {len(v)} eventos | pipeline {len(s)} | montos distintos {(np.abs(s.amount - v.amount.reindex(s.index)) > 1e-6).sum()} | oro consistente: ", end="")
p.assert_gold_consistent(); print("si")
