"""Idempotent event processing with immutable event payload checks."""
from hashlib import sha256
import json

def apply_event(state,event):
    if not event.get("id") or not event.get("type"): raise ValueError("event id/type required")
    digest=sha256(json.dumps(event,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
    history=dict(state.get("seen",{}));previous=history.get(event["id"])
    if previous is not None:
        if previous!=digest: raise ValueError("idempotency key collision")
        return dict(state)
    history[event["id"]]=digest
    return {**state,"seen":history,"events":[*state.get("events",[]),event]}
