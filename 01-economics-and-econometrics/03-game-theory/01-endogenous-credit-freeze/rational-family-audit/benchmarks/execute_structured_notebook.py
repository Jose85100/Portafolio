"""Create and execute a small self-contained narrative notebook in process."""

import contextlib
import base64
import io
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
def md(s: str) -> dict[str, object]:
    return {"cell_type": "markdown", "metadata": {}, "source": s}
codes = [
    "from src.uncertainty_structures import shared_opponent_shock_regret\nfrom src.epsilon_robustness import robust_regret\nA=[[1.,-1.],[-.4,.7]]; p=[.3,.7]; q=[.6,.4]\nfor d in (0,.05,.1,.2):\n    print(d, shared_opponent_shock_regret(A,p,q,d), robust_regret(A,p,q,d).robust_regret)\nassert shared_opponent_shock_regret(A,p,q,.2)==shared_opponent_shock_regret(A,p,q,0)",
    "import csv\nfrom pathlib import Path\nrows=list(csv.DictReader(Path('results/structured_uncertainty/comparison.csv').open()))\nprint('rows=',len(rows),'last=',rows[-1])\nassert len(rows)==4",
]
cells = [
    md(
        "# ¿Cuándo importa la estructura del error de pagos?\nJuego bimatriz sintético; no datos observados. Pregunta: ¿qué cambia al compartir el shock por estado rival?"
    ),
    md(
        "## Derivación\nSea $p$ la mezcla propia y $q$ la rival, ambas en el simplex. Para $u_{ij}=A_{ij}+\\theta_j$, el gain de desviar a $a$ es $g_a=\\sum_j q_j[(A_{aj}+\\theta_j)-\\sum_i p_i(A_{ij}+\\theta_j)]$. El coeficiente de $\\theta_j$ es $q_j(1-\\sum_i p_i)=0$. La cancelación vale para toda caja acotada de shocks comunes por columna; no vale para errores independientes por celda."
    ),
    md(
        "## Baseline y experimento\nComparamos regret nominal y caja independiente del ciclo anterior con el shock común, usando exactamente el mismo juego/perfil. Los cuatro vértices dan un oráculo finito para la caja estructurada."
    ),
]
ns = {}
for source in codes:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(source, ns)
    cells.append(
        {
            "cell_type": "code",
            "metadata": {},
            "execution_count": len([c for c in cells if c["cell_type"] == "code"]) + 1,
            "source": source,
            "outputs": [
                {"output_type": "stream", "name": "stdout", "text": buf.getvalue()}
            ],
        }
    )
png = root / "results/structured_uncertainty/comparison.png"
if not png.is_file():
    raise FileNotFoundError(png)
cells.append(
    {
        "cell_type": "code",
        "metadata": {},
        "execution_count": len(codes) + 1,
        "source": "from IPython.display import Image, display\ndisplay(Image(filename='results/structured_uncertainty/comparison.png'))",
        "outputs": [
            {
                "output_type": "display_data",
                "metadata": {},
                "data": {
                    "image/png": base64.b64encode(png.read_bytes()).decode("ascii"),
                    "text/plain": "Regret under shared and independent shocks",
                },
            }
        ],
    }
)
cells.append(
    md(
        "## Figura y lectura\nLa figura `results/structured_uncertainty/comparison.png` muestra que la cota compartida permanece constante y la caja independiente crece. El resultado depende enteramente del conjunto de incertidumbre supuesto. No identifica el proceso generador de shocks ni demuestra un equilibrio nuevo."
    )
)
nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 4,
}
(root / "notebook_structured.ipynb").write_text(
    json.dumps(nb, indent=1, ensure_ascii=False) + "\n"
)
print("executed", len(codes), "cells in process; outputs saved")
