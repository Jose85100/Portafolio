"""Render lifecycle views with the existing shared fraud-architecture renderer.

This reuses the renderer without duplicating geometry or modifying its original pages.
No external packages, APIs or draw.io installation are required.
"""

import importlib.util
import json
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
RENDERER = (
    ROOT.parents[1]
    / "fraud-and-anomaly-research/ai-enabled-fraud-defense/build_architectures.py"
)


def generate():
    spec = importlib.util.spec_from_file_location(
        "shared_credit_diagram_renderer", RENDERER
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pages = json.loads((ROOT / "diagram_specs.json").read_text())["pages"]
    assert len(pages) == 9
    assert len({page[0] for page in pages}) == len(pages)
    for slug, title, subtitle, rows, edges in pages:
        assert len(rows) == 5 and all(len(nodes) == 3 for _, nodes in rows)
        assert len(title) < 85 and len(subtitle) < 130
        for _, nodes in rows:
            for name, detail, kind in nodes:
                assert len(name) <= 34 and len(detail) <= 65
                assert kind in module.COLORS
        assert all(
            0 <= a < 15 and 0 <= b < 15 and a != b and b // 3 >= a // 3
            for a, b in edges
        ), slug
        assert {v for edge in edges for v in edge} == set(range(15)), slug
    module.ROOT = ROOT
    module.PAGES = pages
    module.generate()
    source = ROOT / "diagrams/fraud-defense.drawio"
    target = ROOT / "diagrams/credit-lifecycle.drawio"
    source.replace(target)
    assert len(ET.parse(target).getroot().findall("diagram")) == 9
    manifest_path = ROOT / "diagrams/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["drawio_file"] = target.name
    manifest["renderer_source"] = str(RENDERER.relative_to(ROOT.parents[3]))
    manifest["scope"] = (
        "Design only; 9 pages; custom SVG renderer, not draw.io GUI exports."
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    generate()
