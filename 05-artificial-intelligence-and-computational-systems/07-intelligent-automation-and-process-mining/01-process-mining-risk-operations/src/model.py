"""Directly-follows graph and process duration metrics from event logs."""
from collections import Counter,defaultdict
from datetime import datetime

def discover(events):
    cases=defaultdict(list)
    for e in events:
        t=datetime.fromisoformat(e["timestamp"].replace("Z","+00:00"))
        if t.tzinfo is None: raise ValueError("timezone required")
        cases[e["case_id"]].append((t,e["activity"]))
    edges=Counter();durations=[]
    for case in cases.values():
        case.sort()
        edges.update(zip((x[1] for x in case[:-1]),(x[1] for x in case[1:])))
        durations.append((case[-1][0]-case[0][0]).total_seconds())
    return {"edges":dict(edges),"cases":len(cases),"mean_duration_seconds":sum(durations)/len(durations) if durations else 0}
