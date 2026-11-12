#!/usr/bin/env python3
"""Market-conditioned CVA sensitivity, not an estimate of an actual counterparty."""
import csv, math, sys
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit('Usage: python3 public_proxy.py BAA10Y.csv DGS10.csv')
def load(path):
    with open(path, newline='') as f:
        rows = csv.reader(f)
        next(rows)
        out = {}
        for row in rows:
            try:
                out[row[0]] = float(row[1]) / 100
            except (ValueError, IndexError):
                continue
        return out
spreads, rates = map(load, sys.argv[1:])
dates = sorted(d for d in spreads.keys() & rates.keys() if '2020-01-01' <= d <= '2024-12-31' and spreads[d] > 0)
if not dates:
    raise SystemExit('No matching positive observations for 2020–2024')
# Each market date is a separate hypothetical valuation: constant five-year
# hazard and discount rate; fixed illustrative EPE and stressed EPE.
lgd, epe, years = 0.60, 1_000_000, 5
out = csv.writer(sys.stdout)
out.writerow(['date','baa_spread_pct','treasury_10y_pct','hazard_proxy','cva_fixed_epe_usd','cva_stress_epe_usd'])
for d in dates:
    s, r = spreads[d], rates[d]
    hazard = s / lgd  # strong assumption: all bond spread is default compensation
    # Explicit stress, not measured WWR: exposure rises 25% per 100 bp above 2%.
    stressed_epe = epe * (1 + 0.25 * max(s - 0.02, 0) / 0.01)
    weight = sum(math.exp(-r*t) * (math.exp(-hazard*(t-1))-math.exp(-hazard*t)) for t in range(1, years+1))
    out.writerow([d, s*100, r*100, hazard, round(lgd*epe*weight,2), round(lgd*stressed_epe*weight,2)])
