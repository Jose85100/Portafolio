"""Per-arm instrumented cost with identical ledger and forecast origins."""
import sys
import time
import tracemalloc
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.vintages import Config, forecast, simulate
from run import write_csv
rows=[]
for n in (240,480,960):
    ledger,_=simulate(Config(n=n))
    for arm,rev,delay,mean in [("asof_ols",False,False,False),("final_no_delay",True,True,False),
                              ("released_mean",False,False,True)]:
        tracemalloc.start(); start=time.perf_counter()
        for origin in range(60,n): forecast(ledger,origin,rev,delay,mean)
        seconds=time.perf_counter()-start
        _,peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
        rows.append(dict(n=n,arm=arm,seconds=seconds,peak_traced_bytes=peak,origins=n-60))
write_csv("cost_by_arm.csv",rows)
