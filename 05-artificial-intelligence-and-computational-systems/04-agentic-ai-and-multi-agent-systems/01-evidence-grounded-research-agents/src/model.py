"""Deterministic evidence validator; no LLM/API dependency or fabricated citations."""

def audit_claims(claims, documents):
    index={d["id"]:d for d in documents}
    if len(index)!=len(documents): raise ValueError("duplicate document id")
    result=[]
    for c in claims:
        refs=c.get("evidence_ids",[])
        valid=bool(refs) and all(r in index and index[r].get("verified",False) for r in refs)
        result.append({"claim":c["claim"],"supported":valid,"missing":[r for r in refs if r not in index],"evidence_ids":refs})
    return result

def coverage(audited):
    return sum(x["supported"] for x in audited)/len(audited) if audited else 0.0
