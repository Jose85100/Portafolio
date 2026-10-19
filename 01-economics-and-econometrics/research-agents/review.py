"""Deterministic research-review agents. No external LLM/API, no silent file edits.

Each reviewer emits actionable findings with evidence, not model-quality certifications.
Run from repository root. Use --strict to fail on high-severity issues.
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWERS = ("theory", "identification", "computation", "pedagogy", "reproducibility")
MIN_MARKDOWN = 850

def notebook_evidence(path):
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        cells = doc.get("cells", [])
        if not isinstance(cells, list):
            raise ValueError("cells must be a list")
        markdown = "\n".join("".join(c.get("source", [])) for c in cells if c.get("cell_type") == "markdown")
        code = "\n".join("".join(c.get("source", [])) for c in cells if c.get("cell_type") == "code")
        return {"valid":True, "cells":len(cells), "markdown_cells":sum(c.get("cell_type")=="markdown" for c in cells),
                "code_cells":sum(c.get("cell_type")=="code" for c in cells),
                "markdown_chars":len(markdown), "code_chars":len(code),
                "has_fixed_seed":bool(re.search(r"(default_rng|seed\s*\(|Random\s*\(|random_state\s*=)",code)),
                "has_assert":bool(re.search(r"\bassert\b|pytest|unittest",code)),
                "has_plot":bool(re.search(r"plt\.|\.plot\(|seaborn|sns\.",code)),
                "has_counterexample":bool(re.search(r"contraejemplo|refutaci[oó]n|falsaci[oó]n|counterexample",markdown,re.I))}
    except (OSError, ValueError, json.JSONDecodeError, TypeError) as exc:
        return {"valid":False, "error":str(exc)}

def review_project(project):
    readme=project/"README.md"
    if not readme.exists():
        return []
    doc=readme.read_text(encoding="utf-8")
    notebooks=sorted(project.rglob("*.ipynb"))
    issues=[]
    def issue(agent, severity, code, evidence, remedy):
        issues.append({"agent":agent,"severity":severity,"code":code,"evidence":evidence,"remedy":remedy})
    if len(doc)<MIN_MARKDOWN:
        issue("pedagogy","medium","short_theory",f"README length={len(doc)} characters",
              "Explain assumptions, derivations, worked example, alternative mechanisms and interpretation.")
    theory_tokens=("supuest","hipótesis","hipotesis","axioma","equilibrio","derivaci","demostraci")
    if sum(any(token in line.lower() for token in theory_tokens) for line in doc.splitlines())<2:
        issue("theory","medium","assumptions_implicit","Fewer than two assumption/theory references",
              "State mathematical hypotheses, what is proved and what remains conjectural.")
    if not re.search(r"refut|falsac|contraejempl|limitacion|limitaci[oó]n|endog|sesgo",doc,re.I):
        issue("identification","high","no_falsification","README lacks refutation or identification threats",
              "Add rival mechanisms, failure cases and empirical falsification protocol.")
    if not re.search(r"bibliograf|referenc|jorda|jordà|wooldridge|angrist|gal[ií]|keynes|nash|doi",doc,re.I):
        issue("theory","medium","no_literature","No explicit literature section detected",
              "Add verified primary sources and distinguish citations from conjectures.")
    if not notebooks and not any(project.rglob("*.py")):
        issue("computation","medium","no_executable","No notebook or Python file found",
              "Create a scoped executable baseline with an independent oracle.")
    for notebook in notebooks:
        ev=notebook_evidence(notebook)
        relative=str(notebook.relative_to(ROOT))
        if not ev["valid"]:
            issue("reproducibility","high","invalid_notebook",relative+": "+ev["error"],"Repair notebook JSON.")
            continue
        if ev["markdown_cells"]<4 or ev["markdown_chars"]<800:
            issue("pedagogy","medium","thin_notebook",f"{relative}: {ev['markdown_cells']} markdown cells, {ev['markdown_chars']} chars",
                  "Add theory, derivation, assumptions, diagnostics, interpretation and discussion.")
        if ev["code_cells"] and not ev["has_fixed_seed"]:
            issue("reproducibility","medium","no_seed",relative,"Fix and record all random seeds.")
        if ev["code_cells"] and not ev["has_assert"]:
            issue("computation","medium","no_assert",relative,"Add oracle-based invariants or tests.")
        if ev["code_cells"] and not ev["has_plot"]:
            issue("pedagogy","low","no_plot",relative,"Plot model predictions and competing scenarios.")
        if not ev["has_counterexample"]:
            issue("identification","medium","no_counterexample",relative,
                  "Construct an explicit assumption-breaking scenario; do not mislabel it a theorem refutation.")
    return issues

def discover(root=ROOT):
    projects=[]
    for area in sorted(root.iterdir()):
        if not area.is_dir() or not re.match(r"^0[1-5]-",area.name):
            continue
        projects.extend(p for p in sorted(area.iterdir()) if p.is_dir() and (p/"README.md").exists())
    return projects

def audit(root=ROOT):
    projects=discover(root)
    records=[]
    for project in projects:
        issues=review_project(project)
        records.append({"project":str(project.relative_to(root)),"notebooks":len(list(project.rglob("*.ipynb"))),
                        "findings":issues,"finding_counts":dict(Counter(i["severity"] for i in issues))})
    totals=Counter(i["severity"] for p in records for i in p["findings"])
    return {"reviewers":list(REVIEWERS),"scope":"static evidence, heuristic review, not scientific peer review",
            "projects_reviewed":len(records),"findings_by_severity":dict(totals),"projects":records}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=Path("economics-review.json"))
    parser.add_argument("--strict",action="store_true")
    args=parser.parse_args()
    result=audit()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Reviewed {result['projects_reviewed']} projects; findings: {result['findings_by_severity']}")
    if args.strict and result["findings_by_severity"].get("high",0):
        raise SystemExit(1)

if __name__=="__main__":main()
