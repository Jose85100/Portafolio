"""Static maturity inventory; evidence presence only, never inferred model quality."""
from collections import Counter
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
DOMAINS=("01-economics-and-econometrics","02-mathematics-statistics-and-quant",
         "03-financial-risk","04-quant-strategy-and-products",
         "05-artificial-intelligence-and-computational-systems",
         "06-strategy-innovation-and-leadership")

def inspect(root=ROOT):
    rows=[]
    for domain in DOMAINS:
        folder=root/domain
        files=[p for p in folder.rglob("*") if p.is_file()]
        counts=Counter(p.suffix.lower() for p in files)
        rows.append({"domain":domain,"files":len(files),"readmes":sum(p.name.lower()=="readme.md" for p in files),
                     "python":counts[".py"],"notebooks":counts[".ipynb"],
                     "cpp":sum(counts[x] for x in (".cpp",".hpp",".h",".cc")),
                     "test_files":sum(p.name.startswith("test_") and p.suffix==".py" for p in files)})
    return rows

if __name__=="__main__":json.dump({"scope":"static file evidence; not model validation","domains":inspect()},sys.stdout,indent=2)
