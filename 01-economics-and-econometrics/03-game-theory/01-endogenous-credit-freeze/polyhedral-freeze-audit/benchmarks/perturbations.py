"""Exact-decimal parameter perturbations; no numerical rank tolerance."""
import csv
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.polyhedra import Game, equilibrium_cells

root = Path(__file__).resolve().parents[1]
rows = []
for q in (.5, .500000001, .500001, .51, .8):
    cells = equilibrium_cells(Game(accuracy=q))
    rows.append(dict(accuracy=q, maximal_cells=len(cells),
        dimensions=';'.join(str(c.dimension) for c in cells), max_dimension=max(c.dimension for c in cells)))
with (root/'results/perturbations.csv').open('w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)
print(rows)
