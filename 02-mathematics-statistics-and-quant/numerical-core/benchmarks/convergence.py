"""Deterministic accuracy/convergence evidence; outputs JSON for CI artifact."""
import importlib.util
import json
from math import exp
from pathlib import Path
import sys
spec=importlib.util.spec_from_file_location("numerical_core",Path(__file__).resolve().parents[1]/"src"/"numerical_core.py")
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

def run():
    exact=100*exp(.1)
    rows=[{"steps":n,"dt":1/n,"absolute_error":abs(m.euler_maruyama_gbm(100,.1,0,1,n,1)[0]-exact)}
          for n in (5,10,20,40,80,160)]
    mc=m.mc_call(100,100,.05,.2,1,paths=25000,seed=42)
    analytical=m.bs_call(100,100,.05,.2,1)
    output={"euler_deterministic_convergence":rows,"black_scholes":analytical,
            "monte_carlo":mc,"absolute_pricing_error":abs(mc["price"]-analytical)}
    assert all(a["absolute_error"]>b["absolute_error"] for a,b in zip(rows,rows[1:]))
    assert output["absolute_pricing_error"] <= 4*mc["standard_error"]
    return output

if __name__=="__main__": print(json.dumps(run(),indent=2))
