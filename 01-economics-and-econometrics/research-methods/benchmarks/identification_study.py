"""Monte Carlo evidence: bias/RMSE by instrument strength. Synthetic only."""
import importlib.util
import json
from pathlib import Path
import sys
from math import sqrt
spec=importlib.util.spec_from_file_location("econ_identification",Path(__file__).resolve().parents[1]/"src"/"identification.py")
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
def run():
    rows=[]
    for strength in (0.1,0.5,1.0,2.0):
        estimates={"ols":[],"iv":[]}
        for seed in range(60):
            d=m.generate_endogenous_dgp(n=600,instrument_strength=strength,seed=seed)
            for key,func in (("ols",m.ols_slope),("iv",lambda y,x:m.iv_slope(y,x,d["z"]))):
                estimates[key].append(func(d["y"],d["x"]))
        for name,values in estimates.items():
            truth=-1.5
            rows.append({"instrument_strength":strength,"estimator":name,"replications":len(values),
                         "bias":sum(v-truth for v in values)/len(values),
                         "rmse":sqrt(sum((v-truth)**2 for v in values)/len(values))})
    return rows
if __name__=="__main__":print(json.dumps(run(),indent=2))
