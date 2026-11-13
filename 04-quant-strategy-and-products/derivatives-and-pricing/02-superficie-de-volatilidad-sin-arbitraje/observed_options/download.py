#!/usr/bin/env python3
"""Capture delayed Cboe SPY quotes as observed points for surface research."""
import csv
import datetime as dt
import hashlib
import json
import re
import subprocess
from pathlib import Path

URL = 'https://cdn.cboe.com/api/global/delayed_quotes/options/SPY.json'
out = Path(__file__).resolve().parent / 'output'
out.mkdir(exist_ok=True)
raw = subprocess.run(['curl', '--fail', '--silent', '--show-error', '--location', '--max-time', '60', URL], check=True, capture_output=True).stdout
payload = json.loads(raw)
spot = float(payload['data']['current_price'])
asof = payload['timestamp']
rows = []
for q in payload['data']['options']:
    match = re.fullmatch(r'SPY(\d{6})([CP])(\d{8})', q['option'])
    if not match:
        continue
    expiry = dt.datetime.strptime(match[1], '%y%m%d').date()
    bid, ask, iv = float(q['bid']), float(q['ask']), float(q['iv'])
    if expiry <= dt.date.fromisoformat(asof[:10]) or bid <= 0 or ask < bid or iv <= 0:
        continue
    strike = int(match[3]) / 1000
    rows.append([asof, q['option'], expiry.isoformat(), match[2], strike, spot, strike / spot, bid, ask, iv, q['volume'], q['open_interest']])
if not rows:
    raise ValueError('No se encontraron cotizaciones válidas; revisar formato y horario de la fuente')
with (out / 'spy_quotes.csv').open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['source_timestamp', 'contract', 'expiry', 'type', 'strike', 'spot', 'strike_over_spot', 'bid', 'ask', 'source_iv', 'volume', 'open_interest'])
    w.writerows(rows)
manifest = {'url': URL, 'retrieved_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'source_timestamp': asof, 'raw_sha256': hashlib.sha256(raw).hexdigest(), 'rows': len(rows), 'spot': spot}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps(manifest, indent=2))
