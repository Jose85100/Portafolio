"""Build and execute the companion notebook in-process with IPython (kernel sockets unavailable)."""

from pathlib import Path
import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parent
nb = nbf.v4.new_notebook()
nb.metadata.kernelspec = {
    "name": "python3",
    "display_name": "Python 3",
    "language": "python",
}
md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
nb.cells = [
    md(r"""# Firmas nivel 2: orden, geometría y aliasing
## Resumen
En simulación el nivel 2 separa orientación sin ruido; endpoints y momentos no distinguen pares reversos. Con ruido alto falla. Auditoría S2 de un componente del programa 13, sin evidencia operativa.
## Contexto y métodos
Trayectorias poligonales finitas en $\mathbb R^d$.
$S_1=\sum_i\Delta x_i$, $S_2=\sum_{i<j}\Delta x_i\otimes\Delta x_j+\frac12\sum_i\Delta x_i\otimes\Delta x_i$.
Composición de Chen: $(a,b)*(c,d)=(a+c,b+d+a\otimes c)$. Al añadir segmento $v$ se multiplica por $(v,v\otimes v/2)$.
Área: $A=(S_2^{12}-S_2^{21})/2$, oráculo independiente shoelace cerrando por cuerda.
### Supuestos
Etiqueta sintética de orientación latente antes del ruido. Los pares reversos tienen los mismos puntos y resúmenes marginales: cualquier clasificador determinista sobre dichos resúmenes predice igual para ambos, por lo que acierta exactamente uno. No se afirma reconstrucción ni innovación algorítmica mundial.
## Datos
Semilla 422; 100 pares por nivel de ruido. Los miembros del par no son independientes."""),
    code(
        "import json, csv\nfrom pathlib import Path\nfrom IPython.display import display, Image\nresults=Path('results')\nconfig=json.loads(Path('config.json').read_text())\nconfig"
    ),
    md(
        "## Resultados\nLos CSV preservan réplicas y medidas. Shoelace es más específico y eficiente para área planar: no se pretende superarlo."
    ),
    code("summary=json.loads((results/'summary.json').read_text())\nsummary"),
    code("display(Image(filename=str(results/'audit.png')))"),
    md(
        "### Convergencia y recursos\nEl error frente a π es geométrico por observación poligonal. No es error de discretización de la recurrencia. La API conserva entrada batch; el estado recurrente requiere O(d²)."
    ),
    code("list(csv.DictReader((results/'convergence.csv').open()))"),
    code("list(csv.DictReader((results/'scalability.csv').open()))"),
    md(
        "## Comprobaciones\nTests de Chen, shuffle, traslación, reversión, entradas inválidas y degeneración. Dos vueltas vistas con cuatro segmentos pierden el área: la exactitud numérica no corrige aliasing."
    ),
    code(
        "from src.signatures import signature, circle, signed_area\nimport numpy as np\na,b=signature(np.array([[0.,0.],[1.,2.],[0.,0.]]))\nassert np.allclose(b,0)\nassert summary['max_oracle_error'] < config['area_tolerance']\nassert summary['accuracy_by_noise']['0'] >= config['orientation_accuracy_threshold']\nprint('Tree-like:', b.tolist())\nprint('Área densa:', signed_area(circle(256,turns=2)))\nprint('Área submuestreada:', signed_area(circle(4,turns=2)))"
    ),
    md(
        "## Conclusiones\nEl nivel 2 añade orden frente a endpoints y momentos; no identifica caminos arbitrarios. Con ruido 1.0, 70% de exactitud refuta robustez universal. Falta validación externa. Bibliografía y verificación en referencias.bib y fuentes.md."
    ),
]
shell = InteractiveShell.instance()
nb.metadata.execution = {
    "executor": "IPython in-process",
    "limitation": "Kernel sockets unavailable in sandbox; fresh script namespace, cells executed sequentially",
}
count = 0
for cell in nb.cells:
    if cell.cell_type != "code":
        continue
    count += 1
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=False)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError(str(result.error_before_exec or result.error_in_exec))
    cell.execution_count = count
    cell.outputs = []
    if captured.stdout:
        cell.outputs.append(
            nbf.v4.new_output("stream", name="stdout", text=captured.stdout)
        )
    if captured.stderr:
        cell.outputs.append(
            nbf.v4.new_output("stream", name="stderr", text=captured.stderr)
        )
    for output in captured.outputs:
        cell.outputs.append(
            nbf.v4.new_output(
                "display_data", data=output.data, metadata=output.metadata
            )
        )
nbf.validate(nb)
nbf.write(nb, root / "notebook.ipynb")
