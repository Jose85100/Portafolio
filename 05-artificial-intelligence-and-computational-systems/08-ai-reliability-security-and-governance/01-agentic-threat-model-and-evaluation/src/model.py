"""Default-deny tool authorization with role, scope and action checks."""

def authorize(actor,tool,resource,policy):
    role=actor.get("role");rules=policy.get(role,[])
    return any(r.get("tool")==tool and (r.get("resource")==resource or r.get("resource")=="*") for r in rules)

def evaluate_attempts(attempts,policy):
    rows=[{"expected":a["expected"],"allowed":authorize(a["actor"],a["tool"],a["resource"],policy)} for a in attempts]
    return {"attempts":len(rows),"false_allows":sum(r["allowed"] and not r["expected"] for r in rows),"false_denies":sum(not r["allowed"] and r["expected"] for r in rows)}
