"""Report assumption-preserving versus assumption-breaking synthetic scenarios."""
import importlib.util
import json
from pathlib import Path
import sys
p=Path(__file__).resolve().parents[1]/"src"/"counterexamples.py"
s=importlib.util.spec_from_file_location("counterexamples",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
def run():
    return {"did":{"parallel":m.did_counterexample(n=10000,seed=3),
                   "violated":m.did_counterexample(n=10000,differential_trend=1.5,seed=3)},
            "phillips":{"exogenous":m.phillips_policy_counterexample(n=10000,seed=3),
                       "feedback":m.phillips_policy_counterexample(n=10000,feedback=1,seed=3)},
            "credit":{"independent":m.portfolio_loss_tail(n=20000,seed=3),
                      "correlated":m.portfolio_loss_tail(n=20000,common_factor_loading=.8,seed=3)}}
if __name__=="__main__":print(json.dumps(run(),indent=2))
