"""Validity-window retrieval with publication-time safeguards; no legal advice."""
from datetime import date

def retrieve(rules,as_of,query):
    day=date.fromisoformat(as_of)
    terms=set(query.lower().split())
    matches=[]
    for r in rules:
        start=date.fromisoformat(r["valid_from"]);end=date.fromisoformat(r["valid_to"]) if r.get("valid_to") else date.max
        published=date.fromisoformat(r["published_at"])
        if not published<=day or not start<=day<end: continue
        overlap=len(terms & set(r["text"].lower().split()))
        if overlap: matches.append({"id":r["id"],"score":overlap,"source":r["source"],"text":r["text"]})
    return sorted(matches,key=lambda x:(-x["score"],x["id"]))
