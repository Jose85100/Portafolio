import csv, json
from pathlib import Path
from evsi import Price
from prior_sensitivity import concentration_grid

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results"; OUT.mkdir(exist_ok=True)
prices=[Price("A",100,11,9),Price("B",180,5,15)]
rows=concentration_grid(prices,20,1,[0.25,0.5,1,2,4,10,100])
with (OUT/"prior_sensitivity.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
(OUT/"prior_sensitivity.json").write_text(json.dumps({"synthetic":True,"hypothesis":"EVSI decreases as common prior concentration grows at fixed means and sample size","rows":rows},indent=2)+"\n")
import matplotlib.pyplot as plt
plt.plot([r["concentration_multiplier"] for r in rows],[r["evsi"] for r in rows],marker="o")
plt.xscale("log"); plt.xlabel("Prior concentration multiplier (mean held fixed)"); plt.ylabel("EVSI (abstract contribution units/customer)"); plt.grid(True,alpha=.3)
plt.tight_layout(); plt.savefig(OUT/"prior_sensitivity.png",dpi=150)
print(json.dumps(rows,indent=2))
