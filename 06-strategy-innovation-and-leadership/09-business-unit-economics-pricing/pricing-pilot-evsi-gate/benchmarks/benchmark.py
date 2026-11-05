from pathlib import Path
import sys,time,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from evsi import Price,evaluate
p=[Price('A',100,11,9),Price('B',180,5,15)]
for n in (5,10,20,40,80):
 t=time.perf_counter(); r=evaluate(p,n,1); dt=time.perf_counter()-t
 print(json.dumps({'n_per_arm':n,'seconds':dt,'outcomes':(n+1)**2,'net_evsi':r['net_evsi']}))
