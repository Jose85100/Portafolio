"""Build four defensive overlays using the existing shared geometry renderer."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHARED = (
    ROOT.parents[2]
    / "fraud-and-anomaly-research/ai-enabled-fraud-defense/build_architectures.py"
)


def generate():
    spec = importlib.util.spec_from_file_location("shared_defense_renderer", SHARED)
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    pages = json.loads((ROOT / "diagram_specs.json").read_text())["pages"]
    assert len(pages) == 4 and len({p[0] for p in pages}) == 4
    for slug, title, subtitle, rows, edges in pages:
        assert len(rows) == 5 and all(len(nodes) == 3 for _, nodes in rows)
        assert len(title) < 85 and len(subtitle) < 130
        for _, nodes in rows:
            for title, detail, kind in nodes:
                assert len(title) <= 34 and len(detail) <= 65
                assert kind in renderer.COLORS
        assert all(
            0 <= a < 15 and 0 <= b < 15 and a != b and b // 3 >= a // 3
            for a, b in edges
        )
        assert {n for edge in edges for n in edge} == set(range(15)), slug
    renderer.ROOT, renderer.PAGES = ROOT, pages
    renderer.generate()
    (ROOT / "diagrams/fraud-defense.drawio").replace(
        ROOT / "diagrams/defense-layers.drawio"
    )
    path = ROOT / "diagrams/manifest.json"
    manifest = json.loads(path.read_text())
    manifest["drawio_file"] = "defense-layers.drawio"
    manifest["scope"] = (
        "4 defensive S1 overlays; custom SVG, no draw.io GUI round-trip."
    )
    path.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    generate()
