from __future__ import annotations
import csv, json
from pathlib import Path
import matplotlib.pyplot as plt
from evsi import Price,evaluate
ROOT=Path(__file__).resolve().parents[1]
cfg=json.loads((ROOT/'config.json').read_text())
prices=[Price(**p) for p in cfg['prices']]
rows=[evaluate(prices,n,c) for n in cfg['pilot_sizes'] for c in cfg['pilot_costs']]
(ROOT/'results').mkdir(exist_ok=True)
with (ROOT/'results/sensitivity.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary=evaluate(prices,20,1)
(ROOT/'results/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
plt.figure(figsize=(7,4.2))
for c in cfg['pilot_costs']:
 subset=[r for r in rows if r['pilot_cost']==c]
 plt.plot([r['n_per_arm'] for r in subset],[r['net_evsi'] for r in subset],marker='o',label=f'costo piloto={c}')
plt.axhline(0,color='black',linewidth=.8);plt.xlabel('Tamaño del piloto (clientes sintéticos)');plt.ylabel('EVSI neto (unidades abstractas)')
plt.title('Cuándo comprar información antes de escalar');plt.legend();plt.tight_layout();plt.savefig(ROOT/'results/net_evsi.png',dpi=150)
print(json.dumps(summary,sort_keys=True))
