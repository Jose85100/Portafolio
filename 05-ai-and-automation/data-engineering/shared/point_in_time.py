"""Point-in-time as-of feature join: no forward-looking leakage."""
from datetime import datetime

def asof_join(events, features, key="entity_id", event_time="decision_at",
              feature_time="available_at", feature_names=None):
    """Use only features available at or before decision, tie-break by version."""
    index = {}
    for f in features:
        t = datetime.fromisoformat(f[feature_time])
        idx = (str(f[key]), t)
        index.setdefault(str(f[key]), []).append((t, str(f.get("version", "")), f))
    for values in index.values():
        values.sort(key=lambda x: (x[0], x[1]))
    output = []
    for event in events:
        cutoff = datetime.fromisoformat(event[event_time])
        candidates = [x for x in index.get(str(event[key]), []) if x[0] <= cutoff]
        chosen = candidates[-1][2] if candidates else None
        row = dict(event)
        for name in feature_names or []:
            if name in row:
                raise ValueError("feature collision: " + name)
            row[name] = chosen.get(name) if chosen else None
        row["_feature_available_at"] = chosen[feature_time] if chosen else None
        output.append(row)
    return output
