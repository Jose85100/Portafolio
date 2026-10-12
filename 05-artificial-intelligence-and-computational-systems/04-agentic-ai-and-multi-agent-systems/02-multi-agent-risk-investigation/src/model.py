"""Human-gated risk investigation workflow with deterministic transitions."""
STATES={"new":{"triaged"},"triaged":{"investigating","closed"},"investigating":{"review","triaged"},"review":{"approved","rejected"},"rejected":{"investigating"},"approved":{"closed"},"closed":set()}

def transition(case, new_state, actor, evidence=None):
    state=case.get("state","new")
    if new_state not in STATES.get(state,set()): raise ValueError("illegal transition")
    if new_state in {"approved","closed"} and actor.get("role")!="human": raise PermissionError("human approval required")
    if new_state=="review" and not evidence: raise ValueError("review needs evidence")
    updated={**case,"state":new_state}
    updated["history"]=[*case.get("history",[]),{"from":state,"to":new_state,"actor":actor["id"],"evidence":evidence or []}]
    return updated
