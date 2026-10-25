"""Ejecutar y guardar los ocho notebooks; un kernel limpio por archivo."""
from pathlib import Path
import nbformat
from nbclient import NotebookClient

def main():
    paths = sorted((Path(__file__).resolve().parent / "notebooks").glob("*.ipynb"))
    for path in paths:
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        NotebookClient(notebook, timeout=180, kernel_name="python3",
                       resources={"metadata": {"path": str(path.parent)}}).execute()
        nbformat.write(notebook, path)
        print(f"OK: {path.name}")

if __name__ == "__main__":
    main()

