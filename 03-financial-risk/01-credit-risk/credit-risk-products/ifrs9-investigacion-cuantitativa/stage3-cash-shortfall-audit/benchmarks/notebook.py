"""Author and actually execute a narrative notebook with captured real outputs."""

import contextlib
import io
from pathlib import Path
from typing import Any

import nbformat
from IPython.core.interactiveshell import InteractiveShell

project = Path(__file__).resolve().parents[1]
nb = nbformat.v4.new_notebook()
nb.metadata.kernelspec = {"name": "python3", "display_name": "Python 3", "language": "python"}
nb.metadata.execution_method = "IPython in-process; real outputs"
nb.cells = [
    nbformat.v4.new_markdown_cell(
        "# Stage 3: default ya ocurrido y recuperaciones\n\n"
        "## tl;dr\nEl motor padre no distingue pérdida dado incumplimiento actual "
        "de nuevo default futuro. Esta auditoría separa PD y descuento. "
        "No es una calibración de cartera ni un cálculo contable aprobado.\n\n"
        "## Context & Methods\n### Key Assumptions\n"
        "No POCI, gross=100 al cierre, sin undrawn/costos/curas, EIR original conocida, "
        "recuperaciones esperadas netas no negativas. Se compara el mismo LGD ya descontado. "
        "Referencia B5.5.33 en copia pública oficial adoptada2016; no afirmación de revisión normativa2026."
    ),
    nbformat.v4.new_code_cell(
        "import json\nfrom pathlib import Path\nfrom src.model import shortfall, scenario_shortfall\n"
        "example=json.loads(Path('results/example.json').read_text())\nprint(example)\n"
        "assert abs(example['cash_shortfall']-(100-60/1.1**2))<1e-12\n"
        "assert example['tiny_rate_stable']>0 and example['tiny_rate_subtractive']==0"
    ),
    nbformat.v4.new_markdown_cell(
        "## Data\n432 casos del producto cartesiano en results/config.json, sin muestreo selectivo. "
        "Se mantiene constante el estado incumplido y se varía la PD ajena a ese estado. "
        "Las columnas de ablación eliminan sólo uno de los dos factores espurios."
    ),
    nbformat.v4.new_code_cell(
        "import pandas as pd\nfrom IPython.display import display\n"
        "rows=pd.read_csv('results/accuracy.csv')\nsummary=json.loads(Path('results/summary.json').read_text())\n"
        "print({k:summary[k] for k in ['cases','nonzero_reference_cases','baseline_underestimates',"
        "'oracle_max_relative_error']})\n"
        "assert summary['oracle_max_relative_error']<=1e-12\n"
        "display(rows[['pd12','eir','horizon','baseline_ecl','cash_shortfall']].head(6))"
    ),
    nbformat.v4.new_markdown_cell("## Results\nFigura sobre casos fijados, no intervalo de confianza."),
    nbformat.v4.new_code_cell(
        "from IPython.display import SVG\ndisplay(SVG(filename='results/comparison.svg'))"
    ),
    nbformat.v4.new_markdown_cell(
        "## Takeaways\nNo se debe reutilizar sin adaptación una curva de nuevo default para un "
        "activo ya incumplido. Una LGD a valor presente tampoco se vuelve a descontar por defecto. "
        "El motor padre queda intacto: se entrega un módulo opt-in y evidencia para migración revisada. "
        "No todos los Stage3 son reducibles a este caso; no se modela POCI, cura, write-off, intereses "
        "ni error de estimación de recuperaciones. Referencias y crítica en informe.md."
    ),
]
shell = InteractiveShell.instance()
for cell in nb.cells:
    if cell.cell_type != "code":
        continue
    outputs: list[Any] = []
    stdout = io.StringIO()
    stderr = io.StringIO()

    def capture(data: dict[str, Any], metadata: dict[str, Any] | None = None, **kwargs: Any) -> None:
        outputs.append(nbformat.v4.new_output("display_data", data=data, metadata=metadata or {}))

    original = shell.display_pub.publish
    setattr(shell.display_pub, "publish", capture)
    try:
        cell.execution_count = shell.execution_count
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = shell.run_cell(cell.source, store_history=True)
        if result.error_before_exec or result.error_in_exec:
            raise RuntimeError(stdout.getvalue() + stderr.getvalue())
    finally:
        setattr(shell.display_pub, "publish", original)
    if stdout.getvalue():
        outputs.insert(0, nbformat.v4.new_output("stream", name="stdout", text=stdout.getvalue()))
    if stderr.getvalue():
        outputs.append(nbformat.v4.new_output("stream", name="stderr", text=stderr.getvalue()))
    cell.outputs = outputs
nbformat.validate(nb)
assert all(c.outputs for c in nb.cells if c.cell_type == "code")
nbformat.write(nb, project / "notebook.ipynb")
print("Three code cells executed with real output; notebook validated")
