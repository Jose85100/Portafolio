"""Verify quotations against source text and detect missing/expired evidence."""
from datetime import date

def verify(citations,documents,as_of):
    day=date.fromisoformat(as_of);index={d["id"]:d for d in documents};out=[]
    for c in citations:
        doc=index.get(c["document_id"])
        valid=bool(doc and c["quote"] and c["quote"] in doc["text"] and date.fromisoformat(doc["published_at"])<=day)
        out.append({"document_id":c["document_id"],"verified":valid,"reason":"verified" if valid else "missing, future, or mismatched quotation"})
    return out
