"""Export selected official-data figures already embedded in the executed notebook."""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebook.ipynb"
DEST = ROOT / "reports" / "figures"
FIGURES = {
    5: "world-bank-coverage.png",
    19: "mfa-inertia-selection.png",
    25: "mfa-multiple-group-correlations.png",
    28: "country-map-income-groups.png",
    35: "cluster-stability.png",
}


def main():
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    DEST.mkdir(parents=True, exist_ok=True)
    for cell_index, name in FIGURES.items():
        outputs = notebook["cells"][cell_index].get("outputs", [])
        image_data = next((output.get("data", {}).get("image/png") for output in outputs
                           if output.get("data", {}).get("image/png")), None)
        if not image_data:
            raise ValueError(f"Notebook cell {cell_index} has no embedded PNG output")
        if isinstance(image_data, list):
            image_data = "".join(image_data)
        (DEST / name).write_bytes(base64.b64decode(image_data))
        print(f"exported cell {cell_index}: {name}")


if __name__ == "__main__":
    main()
