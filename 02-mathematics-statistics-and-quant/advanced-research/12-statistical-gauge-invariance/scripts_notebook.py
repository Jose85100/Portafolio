"""Build and execute the evidence notebook top to bottom."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent
results = json.loads((ROOT / "benchmarks/results.json").read_text(encoding="utf-8"))
global_result = results["global"]

cells = [
    nbformat.v4.new_markdown_cell(
        f"""# Certificado gauge para factorización rango uno

## tl;dr

En 120 réplicas, el residual gauge máximo fue **{global_result["max_gauge_residual"]:.3e}**, la predicción cambió como máximo **{global_result["max_prediction_change"]:.3e}** y la fijación de gauge redujo la inestabilidad paramétrica al menos **{100 * global_result["min_instability_reduction"]:.6f}%**. El punto regular tuvo nulidad 1; el caso degenerado no fue confundido con una única simetría de escala."""
    ),
    nbformat.v4.new_markdown_cell(
        """## Contexto y métodos

Modelo: `Y = u vᵀ + epsilon`, con ruido gaussiano iid y matriz completamente observada. La órbita `(u,v) ~ (c u,v/c)` conserva la distribución. Comparamos Jacobiano analítico contra diferencias centrales y factores sin fijar contra una sección SVD balanceada.

### Supuestos clave

Factores no nulos para el resultado regular; rango uno; varianza conocida; umbral espectral de precisión de máquina. La nulidad es un diagnóstico local, no prueba automática de simetría global."""
    ),
    nbformat.v4.new_markdown_cell(
        "## Datos\n\nResultados sintéticos generados desde `config.json`; cada fila cruda conserva su semilla."
    ),
    nbformat.v4.new_code_cell(
        """import csv, json
from pathlib import Path
import numpy as np
from src.gauge import analytic_jacobian, fisher_information, gauge_tangent, spectral_certificate

root = Path.cwd()
config = json.loads((root / 'config.json').read_text())
results = json.loads((root / 'benchmarks/results.json').read_text())
with (root / 'benchmarks/summary.csv').open() as stream:
    summary = list(csv.DictReader(stream))
assert len(summary) == 6 and all(results['gates'].values())
{'configurations': len(summary), 'raw_rows': results['design']['rows'], 'gates': results['gates']}"""
    ),
    nbformat.v4.new_markdown_cell("## Resultados\n\n### 1. Verificación local independiente"),
    nbformat.v4.new_code_cell(
        """u = np.array([1.0, -0.5, 0.25])
v = np.array([0.8, -0.3])
jacobian = analytic_jacobian(u, v)
certificate = spectral_certificate(fisher_information(jacobian, 0.05))
residual = np.linalg.norm(jacobian @ gauge_tangent(u, v)) / np.linalg.norm(gauge_tangent(u, v))
assert certificate.nullity == 1 and residual < 1e-12
{'nullity': certificate.nullity, 'rank': certificate.rank, 'gauge_residual': residual}"""
    ),
    nbformat.v4.new_markdown_cell("### 2. Tabla exacta por configuración"),
    nbformat.v4.new_code_cell(
        """selected = [{
    'shape': f\"{row['m']}x{row['n']}\",
    'sigma': float(row['noise_std']),
    'analytic_ms': round(float(row['median_analytic_ms']), 4),
    'finite_difference_ms': round(float(row['median_finite_difference_ms']), 4),
    'speedup': round(float(row['median_speedup']), 2),
    'nullity': int(row['nullity_mode'])
} for row in summary]
selected"""
    ),
    nbformat.v4.new_markdown_cell("### 3. Figura reproducida por el benchmark"),
    nbformat.v4.new_code_cell(
        """from base64 import b64encode
from IPython.display import HTML, display
figure = root / 'benchmarks/gauge-certificate.png'
assert figure.stat().st_size > 10_000
encoded = b64encode(figure.read_bytes()).decode('ascii')
display(HTML(f'<img src="data:image/png;base64,{encoded}" alt="Tres paneles: costo del Jacobiano, inestabilidad de escala y nulidad regular frente a degenerada">'))"""
    ),
    nbformat.v4.new_markdown_cell(
        """## Conclusiones

El certificado responde afirmativamente solo en el caso acotado: reconoce la dirección de escala conocida y la sección balanceada elimina la arbitrariedad sin alterar la predicción. La nulidad mayor del caso `u=0` es la ablation negativa esencial: una Fisher singular por sí sola no identifica qué simetría o degeneración la produjo. Siguiente prueba: acción `GL(r)` para rango mayor."""
    ),
]
notebook = nbformat.v4.new_notebook(cells=cells)
notebook.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
parser = argparse.ArgumentParser()
parser.add_argument("--kernel", action="store_true")
arguments = parser.parse_args()
if arguments.kernel:
    client = NotebookClient(
        notebook,
        timeout=180,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
    )
    client.execute()
    notebook.metadata["execution"] = {"executor": "nbclient conventional kernel"}
else:
    shell = InteractiveShell.instance()
    for execution_count, cell in enumerate((item for item in notebook.cells if item.cell_type == "code"), 1):
        with capture_output() as captured:
            result = shell.run_cell(cell.source, store_history=False)
        if result.error_before_exec or result.error_in_exec:
            raise RuntimeError("Notebook cell failed") from (result.error_before_exec or result.error_in_exec)
        cell.execution_count = execution_count
        cell.outputs = []
        for name, value in (("stdout", captured.stdout), ("stderr", captured.stderr)):
            if value:
                cell.outputs.append(nbformat.v4.new_output("stream", name=name, text=value))
        for output in captured.outputs:
            cell.outputs.append(
                nbformat.v4.new_output("display_data", data=output.data, metadata=output.metadata)
            )
    notebook.metadata["execution"] = {
        "executor": "IPython in-process; actual cells and rich outputs (local sockets unavailable)"
    }
nbformat.validate(notebook)
nbformat.write(notebook, ROOT / "notebook.ipynb")
