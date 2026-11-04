from pathlib import Path
import json, platform, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.lgd_uncertainty import Scenario, evaluate, write_results
root=Path(__file__).resolve().parents[1]
raw=json.loads((root/'benchmarks/config.json').read_text())['scenario']
s=Scenario(**raw)
r=write_results(s,root/'results')
# Compare the analytical expectation with high-accuracy independent quadrature
# written as composite Simpson integration, with the same time-varying EAD.
def simpson(n=4096):
    h=s.hazard_default+s.hazard_prepay; step=s.horizon/n; total=0.0
    for i in range(n+1):
        t=i*step; e=s.ead_start+(s.ead_end-s.ead_start)*t/s.horizon
        y=s.hazard_default*__import__('math').exp(-h*t)*e*s.lgd_alpha/(s.lgd_alpha+s.lgd_beta)
        total += y*(1 if i in (0,n) else (4 if i%2 else 2))
    return total*step/3
assert abs(simpson()-r.expected_loss)<1e-10
import matplotlib.pyplot as plt
import numpy as np
alphas=np.linspace(.5,12,80); betas=alphas*2/3
sds=[]
for a,b in zip(alphas,betas):
    sds.append(evaluate(Scenario(s.ead_start,s.ead_end,s.horizon,s.hazard_default,s.hazard_prepay,float(a),float(b))).loss_sd)
fig,ax=plt.subplots(figsize=(7,4)); ax.plot(alphas,sds,label='Uncertain Beta LGD'); ax.set(xlabel='Beta concentration α+β (mean LGD fixed at 0.6)',ylabel='Std. dev. of undiscounted loss (currency)',title='LGD parameter uncertainty at fixed mean'); ax.grid(alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(root/'results/lgd_uncertainty.png',dpi=150)
(root/'results/run_metadata.json').write_text(json.dumps({'python':platform.python_version(),'platform':platform.platform(),'simpson4096_abs_error':abs(simpson()-r.expected_loss)},indent=2)+'\n')
print(json.dumps({'mean_loss':r.expected_loss,'sd_uncertain':r.loss_sd,'sd_plugin_variance':r.plugin_variance**.5,'simpson_error':abs(simpson()-r.expected_loss)}))
