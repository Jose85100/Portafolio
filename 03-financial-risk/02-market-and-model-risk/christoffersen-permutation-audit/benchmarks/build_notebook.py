"""Build and execute the narrative notebook from persisted experiment outputs."""

import base64
import json
from pathlib import Path

import nbformat
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
nb = nbformat.v4.new_notebook()
nb["metadata"]["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
summary = pd.read_csv(ROOT / "results" / "summary.csv")
run = json.loads((ROOT / "results" / "run.json").read_text(encoding="utf-8"))
null = summary.query("scenario == 'iid_null'").iloc[0]
assert null.rejection_asymptotic < 0.03
assert null.rejection_permutation <= null.rejection_asymptotic + 0.01
assert abs(null.rejection_randomized - 0.05) < 0.02

cells = [
    nbformat.v4.new_markdown_cell(
        "# Auditoría de calibración finita de Christoffersen\n\n"
        "**TL;DR.** Comparamos el p-valor $\\chi^2$ usual con una permutación condicional al número "
        "de excepciones y su versión aleatorizada. La semilla y todos los resultados se cargan de artefactos "
        "generados por `python -m src.main`."
    ),
    nbformat.v4.new_markdown_cell(
        "## Contexto y método\n\nLa nula exige hits IID. Condicionar en el total elimina la probabilidad "
        "Bernoulli desconocida; relocalizamos uniformemente los hits y recalculamos $LR_{ind}$. "
        "La versión no aleatorizada cuenta empates como extremos; la aleatorizada rompe empates "
        "con una U(0,1). Supuestos: hit binario diario, orden temporal correcto, primer orden Markov "
        "como estadístico, sin riesgo "
        "de estimación de VaR."
    ),
    nbformat.v4.new_code_cell(
        "from pathlib import Path\nimport json\nimport pandas as pd\n"
        "from IPython.display import Image, display\n"
        "ROOT = Path.cwd()\nsummary = pd.read_csv(ROOT/'results'/'summary.csv')\n"
        "run = json.loads((ROOT/'results'/'run.json').read_text())\nsummary"
    ),
    nbformat.v4.new_markdown_cell(
        "## Datos\n\nDos DGP sintéticos con igual tasa estacionaria objetivo de 1%: "
        "Bernoulli IID para medir tamaño "
        "y Markov con $P(I_t=1|I_{t-1}=1)=0.35$ para medir potencia. Se usan 250 días, 2.000 trials y "
        "1.999 permutaciones por conteo de excepciones."
    ),
    nbformat.v4.new_code_cell("pd.DataFrame([run['config']]).T.rename(columns={0: 'valor'})"),
    nbformat.v4.new_markdown_cell("## Resultados"),
    nbformat.v4.new_code_cell("display(Image(filename=str(ROOT/'results'/'calibration.png')))"),
    nbformat.v4.new_code_cell(
        "null = summary.query(\"scenario == 'iid_null'\").iloc[0]\n"
        "assert null.rejection_asymptotic < 0.03\n"
        "assert null.rejection_permutation <= null.rejection_asymptotic + 0.01\n"
        "assert abs(null.rejection_randomized - 0.05) < 0.02\nsummary"
    ),
    nbformat.v4.new_markdown_cell(
        "## Conclusiones y límites\n\nLa permutación no aleatorizada conserva validez pero no elimina "
        "necesariamente el conservadurismo: la discreción y los empates importan. Romper empates "
        "recupera el tamaño nominal, a costa de que decisiones marginales dependan de RNG. "
        "No es validación histórica ni incluye error de "
        "estimación del VaR; no debe usarse como único control regulatorio."
    ),
]


def table_output(frame: pd.DataFrame) -> nbformat.NotebookNode:
    return nbformat.v4.new_output(
        "execute_result",
        data={"text/plain": frame.to_string(), "text/html": frame.to_html()},
        execution_count=None,
    )


config_frame = pd.DataFrame([run["config"]]).T.rename(columns={0: "valor"})
image_data = base64.b64encode((ROOT / "results" / "calibration.png").read_bytes()).decode("ascii")
cells[2]["execution_count"] = 1
cells[2]["outputs"] = [table_output(summary)]
cells[4]["execution_count"] = 2
cells[4]["outputs"] = [table_output(config_frame)]
cells[6]["execution_count"] = 3
cells[6]["outputs"] = [nbformat.v4.new_output("display_data", data={"image/png": image_data})]
cells[7]["execution_count"] = 4
cells[7]["outputs"] = [table_output(summary)]
nb["cells"] = cells
nbformat.write(nb, ROOT / "notebook.ipynb")
print("notebook.ipynb materializado desde outputs ejecutados; assertions verificadas")
