"""Validate design inventory, references and maturity claims; not model/security tests."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]


def validate():
    projects = json.loads((ROOT / "projects/projects.json").read_text())["projects"]
    layers = json.loads((ROOT / "defense-layers/layers.json").read_text())["layers"]
    assert len(projects) == 10 and len(layers) == 8
    slugs = {p["slug"] for p in projects}
    assert len(slugs) == 10 and len({p["id"] for p in layers}) == 8
    sources = {
        s["id"] for s in json.loads((ROOT / "sources.json").read_text())["sources"]
    }
    idea_ids, scenario_ids, study_ids = [], [], []
    for p in projects:
        assert p["status"] == "S1" and p["implemented"] is False
        assert len(p["ideas"]) == 3 and len(p["security_cases"]) == 4
        folder = ROOT / "projects" / p["slug"]
        for name in [
            "README.md",
            "EXPERIMENTS.md",
            "SECURITY_REVIEW.md",
            "contracts/example.json",
        ]:
            assert (folder / name).is_file(), (p["slug"], name)
        assert (
            json.loads((folder / "contracts/example.json").read_text()) == p["example"]
        )
        for path in p["reuse"]:
            assert (REPO / path).exists(), path
        assert set(p["sources"]) <= sources
        assert set(p["dependencies"]) <= slugs and p["slug"] not in p["dependencies"]
        local_cases = {c["id"] for c in p["security_cases"]}
        scenario_ids.extend(local_cases)
        for idea in p["ideas"]:
            assert idea["status"] == "proposed" and idea["executed"] is False
            assert set(idea["adversarial_case_ids"]) <= local_cases
            assert all(
                idea[key]
                for key in [
                    "hypothesis",
                    "formula",
                    "design",
                    "metrics",
                    "falsification",
                    "deliverable",
                ]
            )
            idea_ids.append(idea["id"])
    graph = {p["slug"]: p["dependencies"] for p in projects}

    def visit(node, trail):
        assert node not in trail, ("dependency cycle", trail, node)
        for dep in graph[node]:
            visit(dep, trail + [node])

    for node in graph:
        visit(node, [])
    for layer in layers:
        assert layer["status"] == "S1" and layer["implemented"] is False
        assert set(layer["projects"]) <= slugs
        assert (ROOT / "defense-layers" / layer["id"] / "README.md").is_file()
        assert len(layer["studies"]) == 2
        for study in layer["studies"]:
            assert study["status"] == "proposed" and study["executed"] is False
            study_ids.append(study["id"])
    for ids, count in [(idea_ids, 30), (scenario_ids, 40), (study_ids, 16)]:
        assert len(ids) == len(set(ids)) == count
    links = 0
    for path in ROOT.rglob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            assert (path.parent / target.split("#")[0]).exists(), (str(path), target)
            links += 1
    return {
        "scope": "Structural design validation only; no research experiment or pentest.",
        "projects": 10,
        "project_ideas": 30,
        "adversarial_scenarios": 40,
        "additional_layers": 8,
        "layer_studies": 16,
        "local_markdown_links": links,
        "maturity": "all new designs S1; proposed/executed flags checked",
    }


if __name__ == "__main__":
    print(json.dumps(validate(), ensure_ascii=False))
