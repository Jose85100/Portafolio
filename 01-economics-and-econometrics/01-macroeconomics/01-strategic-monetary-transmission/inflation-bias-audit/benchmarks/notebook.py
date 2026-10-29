"""Build and execute a small narrative notebook in clean in-process IPython."""

from pathlib import Path
import sys
import json
import nbformat as n
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
r = json.loads((root / "results/summary.json").read_text())
cells = [
    n.v4.new_markdown_cell(
        "# Sesgo inflacionario: optimizar no basta sin expectativas consistentes\n\n## Resumen\nAncla sintética: compromisoL0,75, discreciónL1,25. Una política ingenua pareceL0,5, pero supone expectativas0 y genera inflación media0,5: no es un equilibrio de expectativas racionales. 54casos con dos estados equiprobables exactos; sin Monte Carlo ni datos reales. S2 local."
    ),
    n.v4.new_markdown_cell(
        "## Tres ideas y selección\nSe compararon HAC para IV, extensión dinámica de bienes públicos e inconsistencia temporal monetaria. Se eligió la tercera para rotar de modelos recientes y auditar factibilidad de expectativas antes de ordenar objetivos. Teoría clásica; contribución incremental al repositorio, no prioridad científica."
    ),
    n.v4.new_markdown_cell(r"""## Modelo y secuencia

$y=\alpha(\pi-\pi^e)+\epsilon$, pérdida $L=\frac12[\pi^2+\lambda(y-k)^2]$. El privado fija $\pi^e$ antes del shock; el banco observa ε y elige π. Bajo discreción el privado anticipa esa mejor respuesta. Bajo compromiso se asume capacidad **costless y creíble** de fijar una regla contingente antes de expectativas; no se implementa un mecanismo institucional que la garantice.

Shock ε∈{−σ,+σ}, probabilidad0,5. Cuando σ0 son dos registros idénticos con peso0,5, no dos observaciones independientes. Variables normalizadas, no tasas calibradas o previsiones macro reales."""),
    n.v4.new_code_cell(
        'import json,csv\nfrom pathlib import Path\nimport numpy as np\nfrom IPython.display import display,Image\nfrom src.monetary import policies,loss,best_response,oracle\nroot=Path.cwd()\nr=json.loads((root/"results/summary.json").read_text())\nprint(json.dumps(r["config"],indent=2))'
    ),
    n.v4.new_markdown_cell(r"""## Derivación y expectativas racionales

Mejor respuesta condicional: $\pi^{BR}=\lambda\alpha(\alpha\pi^e+k-\epsilon)/(1+\lambda\alpha^2)$. Bajo RE $\pi^e=E\pi=\lambda\alpha k=b$. Por tanto $\pi_D=b-\lambda\alpha\epsilon/(1+\lambda\alpha^2)$.

Compromiso óptimo dentro de reglas afines: $\pi_C=-\lambda\alpha\epsilon/(1+\lambda\alpha^2)$ y esperanza0. Ambas generan $y=\epsilon/(1+\lambda\alpha^2)$; la diferencia exacta de pérdida esperada es $\frac12b^2$. Bajo compromiso se impide reoptimizar ex post: no se verifica la misma mejor respuesta que discreción. La ventaja depende de esa capacidad asumida."""),
    n.v4.new_code_cell(
        'for shock in [-1,1]:\n for name,(pi,e) in policies(shock,1,1,1).items():\n  print("Shock",shock,name,"π",pi,"πe",e,"y",pi-e+shock,"L",loss(pi,e,shock,1,1,1))\n print("Oráculo BR discreción",oracle(1,shock,1,1,1))'
    ),
    n.v4.new_markdown_cell(
        "## Datos, baseline y control de admisibilidad\n54escenarios de parámetros,3regímenes y2estados producen324registros. Discreción es baselineREfactible. La política ingenua congelaπe0 y usaBR: no debe contarse como régimen factible cuandoEπ≠πe. El oráculo escalar verifica la BRcondicional, no prueba compromiso institucional o causalidad."
    ),
    n.v4.new_code_cell(
        'rows=list(csv.DictReader((root/"results/cases.csv").open()))\nassert len(rows)==54\nprint("Ancla",r["anchor"])\nprint("Error identidad de pérdida",r["max_loss_gap_identity_error"])\nprint("Error máximo BR versus oráculo",r["max_best_response_oracle_error"])\nassert r["max_loss_gap_identity_error"]<1e-10\nassert r["max_best_response_oracle_error"]<1e-6\nfor row in rows:\n assert float(row["commitment_re_residual"])<1e-12\n assert float(row["discretion_re_residual"])<1e-12'
    ),
    n.v4.new_markdown_cell(
        "## Falsación: menor pérdida aparente con equilibrio incumplido\nAncla: naiveL0,5 es menor que compromiso0,75, pero su inflación media0,5 contradiceexpectativa0. Su ganancia media de producto0,5 es sorpresa no anticipada, no un efecto sistemáticoRE. En los dos regímenes consistentes producto medio0. No recomendar una política por su objetivo si incumple restricciones."
    ),
    n.v4.new_code_cell(
        'a=r["anchor"]\nassert a["naive_loss_inconsistent"]<a["commitment_loss"]\nassert a["naive_re_residual"]>.4\nassert abs(a["commitment_mean_output"])<1e-12\nassert abs(a["discretion_mean_output"])<1e-12\nprint("Naive rechazada como equilibrio; no se cuenta su pérdida como mejora factible.")'
    ),
    n.v4.new_markdown_cell(
        "## Sensibilidad y control negativo\nCuando k0 desaparece la razón de sesgo: compromiso y discreción coinciden. Las diferencias aquí son exactas bajo el modelo, no errores estadísticos o evidencia de dominancia de reglas rígidas en modelos más amplios."
    ),
    n.v4.new_code_cell(
        'display(Image(filename=str(root/"results/comparison.png")))\nfor shock in [-1,1]:\n p=policies(shock,1,1,0)\n assert p["commitment"]==p["discretion"]\nprint("Control k0 confirmado.")'
    ),
    n.v4.new_markdown_cell(
        "## Coste, trazabilidad y límites\nEvaluación de54casos y oráculos escalares medida en tiempo/picoPython, noRSS ni latencia operacional. Sin benchmark de alta dimensión. No agentes heterogéneos, tipo de cambio, dinero, tasa de interés, credibilidad endógena, reputación repetida o estimación de parámetros."
    ),
    n.v4.new_code_cell(
        'print("Versiones",r["versions"])\nprint("Segundos instrumentados",r["seconds"],"PicoPython",r["python_peak_bytes"])\nprint("SHA256 datos",r["data_sha256"])\nprint("SHA256 núcleo",r["source_sha256"])'
    ),
    n.v4.new_markdown_cell(
        "## Preguntas y siguientes pasos\n¿Quién garantiza la regla comprometida? ¿Cómo cambian resultados si k depende de distorsiones o expectativas se aprenden? ¿Qué datos identifican α? No se responde con una recomendación para un banco real. Cinco referencias verificadas y un informe14p delimitan alcance.\n\nEjecución secuencial IPython limpio en proceso sin kernel/socket; errores abortan, outputs persisten; figura inspeccionada sin probar todos los frontends."
    ),
]
nb = n.v4.new_notebook(
    cells=cells,
    metadata={
        "kernelspec": {
            "name": "python3",
            "display_name": "Python3",
            "language": "python",
        },
        "language_info": {"name": "python"},
        "execution_method": "Clean in-process IPython; sequential cells; no Jupyter kernel/socket.",
    },
)
shell = InteractiveShell.instance(user_ns={})
count = 0
for cell in nb.cells:
    if cell.cell_type != "code":
        continue
    count += 1
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=False)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError(f"Notebook cell{count} failed") from (
            result.error_before_exec or result.error_in_exec
        )
    outputs = []
    if captured.stdout:
        outputs.append(n.v4.new_output("stream", name="stdout", text=captured.stdout))
    if captured.stderr:
        outputs.append(n.v4.new_output("stream", name="stderr", text=captured.stderr))
    for output in captured.outputs:
        outputs.append(
            n.v4.new_output("display_data", data=output.data, metadata=output.metadata)
        )
    cell.outputs = outputs
    cell.execution_count = count
n.validate(nb)
n.write(nb, root / "notebook.ipynb")
print(f"Executed{count}code cells in process.")
