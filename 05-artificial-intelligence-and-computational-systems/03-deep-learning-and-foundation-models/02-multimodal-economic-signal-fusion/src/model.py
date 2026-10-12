"""As-of fusion: only signals published by decision time can enter features."""
from datetime import datetime,timezone

def parse_time(value):
    t=datetime.fromisoformat(value.replace("Z","+00:00"))
    if t.tzinfo is None: raise ValueError("timezone required")
    return t.astimezone(timezone.utc)

def fuse(decisions, signals):
    output=[]
    for d in decisions:
        cutoff=parse_time(d["decision_at"])
        row=dict(d)
        for name in sorted({s["channel"] for s in signals}):
            candidates=[s for s in signals if s["channel"]==name and parse_time(s["available_at"])<=cutoff]
            best=max(candidates,key=lambda s:(parse_time(s["available_at"]),str(s.get("version","")))) if candidates else None
            if name in row: raise ValueError("feature collision")
            row[name]=best["value"] if best else None
        output.append(row)
    return output
