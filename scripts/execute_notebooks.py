"""Execute selected portfolio notebooks and retain their rendered outputs."""
import argparse
import json
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def notebooks(arguments):
    if arguments.all:
        return sorted(ROOT.rglob("notebook.ipynb"))
    return [ROOT / value for value in arguments.notebooks]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="execute every notebook.ipynb")
    parser.add_argument("--output", default="artifacts/notebooks")
    parser.add_argument("notebooks", nargs="*", help="repository-relative notebook paths")
    args = parser.parse_args()
    selected = notebooks(args)
    if not selected:
        print("No notebooks selected.")
        return
    destination = ROOT / args.output
    results = []
    for source in selected:
        if not source.is_file() or source.name != "notebook.ipynb":
            raise ValueError(f"invalid notebook path: {source.relative_to(ROOT)}")
        relative = source.relative_to(ROOT)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        notebook = nbformat.read(source, as_version=4)
        NotebookClient(notebook, timeout=1800, kernel_name="python3",
                       resources={"metadata": {"path": str(source.parent)}}).execute()
        nbformat.write(notebook, target)
        results.append({"notebook": str(relative), "status": "passed", "artifact": str(target.relative_to(ROOT))})
    (destination / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
