"""Content-addressed evidence ledger with chain verification."""
import hashlib,json

def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def append(ledger,payload):
    previous=ledger[-1]["hash"] if ledger else "GENESIS"
    record={"index":len(ledger),"previous":previous,"payload":payload}
    record["hash"]=hashlib.sha256(canonical(record).encode()).hexdigest()
    return [*ledger,record]
def verify(ledger):
    previous="GENESIS"
    for i,record in enumerate(ledger):
        if record.get("index")!=i or record.get("previous")!=previous:return False
        candidate={k:v for k,v in record.items() if k!="hash"}
        if hashlib.sha256(canonical(candidate).encode()).hexdigest()!=record.get("hash"):return False
        previous=record["hash"]
    return True
