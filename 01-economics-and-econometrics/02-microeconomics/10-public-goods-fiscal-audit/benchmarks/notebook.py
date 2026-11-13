"""Build and execute a compact notebook in a clean in-process IPython shell."""

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
        "# Bien público: financiar un subsidio no es gratis\n\n## Resumen\nEn el modelo sintético de dos agentes, un matching que ignora la distorsión fiscal puede reducir bienestar frente a no intervenir. Se deriva una corrección analítica y se contrasta con optimización escalar en30casos. S2 local; no recomendación fiscal real."
    ),
    n.v4.new_markdown_cell(
        "## Tres ideas y selección\nSe compararon HAC para IV, inferencia robusta al sesgo RD y provisión de bien público con coste fiscal. Se eligió el tercero por ser nuevo y pequeño, con identidad presupuestaria y oráculo independientes. No se afirma algoritmo mundial nuevo."
    ),
    n.v4.new_markdown_cell(r"""## Modelo económico

Dos agentes con $0<\theta_L<\theta_H$, $\theta_H>1$. Utilidad $\theta_i\log(1+G)-(1-s)g_i-T_i$, $G=g_L+g_H$. Transferencias fijas $T_i$ se anuncian antes de elegir; suman $sG$ **en el equilibrio previsto**, no ante toda desviación. Ningún agente internaliza cambios marginales del impuesto. Preferencias conocidas y sin restricciones presupuestarias.

Nash: solo el tipo alto contribuye, $G(s)=\theta_H/(1-s)-1$. Sin política $G_0=\theta_H-1$. El objetivo sin coste fiscal tiene $G_{FB}=\theta_L+\theta_H-1$. No modelamos altruismo cálido, incertidumbre, competencia fiscal o comportamiento empírico."""),
    n.v4.new_code_cell(
        'import json,csv\nfrom pathlib import Path\nimport numpy as np\nfrom IPython.display import display,Image\nfrom src.public_good import optimal,naive,no_policy,policy_welfare,oracle\nroot=Path.cwd()\nr=json.loads((root/"results/summary.json").read_text())\nprint(json.dumps(r["config"],indent=2))'
    ),
    n.v4.new_markdown_cell(r"""## Contabilidad y solución

Matching $s(G)=1-\theta_H/(1+G)$, presupuesto $B=sG$. Transferencias no son ganancia de recursos: bienestar $W=(\theta_L+\theta_H)\log(1+G)-G-\lambda B$. λ es una pérdida real adicional **supuesta**, no una estimación fiscal.

Con $z=1+G$, condición interior $(1+\lambda)z^2-(\theta_L+\theta_H)z-\lambda\theta_H=0$. La segunda derivada de W es negativa; la raíz positiva y la cota $G\ge G_0$ producen óptimo global del modelo restringido. Si λ≥θL/(θH−1), se elige no subsidiar. El solver escalar es un contraste de implementación, no evidencia empírica."""),
    n.v4.new_code_cell(
        'low,high,tax=1,2,.5\nfor label,G in [("Sin política",no_policy(high)),("Ignora coste fiscal",naive(low,high)),("Corrige coste fiscal",optimal(low,high,tax))]:\n W,s,B=policy_welfare(G,low,high,tax)\n print(label,"G",G,"W",W,"s",s,"B",B)\n assert abs(high/(1-s)-1-G)<1e-10\nprint("Oráculo numérico",oracle(low,high,tax))'
    ),
    n.v4.new_markdown_cell(
        "## Datos y validación\n30casos determinísticos:3valores bajos×2altos×5costes fiscales. No son muestras de una población; no inventamos errores Monte Carlo o validación causal. CSV guarda G, bienestar, presupuesto y error del oráculo; hashes/versiones enJSON."
    ),
    n.v4.new_code_cell(
        'rows=list(csv.DictReader((root/"results/cases.csv").open()))\nassert len(rows)==30\nprint("Error máximo de bienestar frente a oráculo",r["max_oracle_welfare_gap"])\nprint("Mínima ganancia vs no política",r["min_gain_vs_no_policy"])\nprint("Mínima ganancia vs naive",r["min_gain_vs_naive"])\nassert r["max_oracle_welfare_gap"]<1e-8\nassert r["min_gain_vs_no_policy"]>-1e-10'
    ),
    n.v4.new_markdown_cell(
        "## Sensibilidad y control negativo\nCuando λ=0, corregir coincide con la política sin distorsión. Para λ alto, el óptimo elimina subsidio; no hay mejora universal estricta. Gráfico en unidades normalizadas, no dinero ni bienestar medido de hogares."
    ),
    n.v4.new_code_cell(
        'display(Image(filename=str(root/"results/comparison.png")))\nprint("Ancla",r["anchor"])'
    ),
    n.v4.new_markdown_cell(
        "## Falsación de contabilidad\nOmitir los impuestos fijos y sumar solo la utilidad antes de financiar el matching eleva artificialmente bienestar por B. La corrección no resta dos veces una transferencia: resta recursos G y la pérdida adicionalλB, según el modelo supuesto."
    ),
    n.v4.new_code_cell(
        'G=2\nW,s,B=policy_welfare(G,1,2,0)\nbefore_tax=3*np.log1p(G)-(1-s)*G\nprint("Bienestar antes de financiar",before_tax,"real",W,"diferencia",before_tax-W,"presupuesto",B)\nassert abs(before_tax-W-B)<1e-12\nassert optimal(1,2,0)==naive(1,2)\nassert optimal(1,2,2)==no_policy(2)'
    ),
    n.v4.new_markdown_cell(
        "## Costes y trazabilidad\nEscenario escalar fijo; costes de30casos agregados por prefijos, no benchmark de alta dimensión. Pico de asignacionesPython del experimento entero no esRSS ni memoria por brazo. Cinco referencias reales delimitan lo que no modelamos."
    ),
    n.v4.new_code_cell(
        'print((root/"results/costs.csv").read_text())\nprint("Versiones",r["versions"])\nprint("SHA256 datos",r["data_sha256"])\nprint("SHA256 núcleo",r["source_sha256"])'
    ),
    n.v4.new_markdown_cell(
        "## Límites y siguientes pasos\nEl presupuesto solo equilibra en el Nash previsto. Si los impuestos dependen de desviaciones, cambian los incentivos; si hay ingreso limitado, warm glow o λ endógeno, hay otro juego. No se concluye una tasa óptima real. Siguiente: restricciones presupuestarias, financiación fuera de equilibrio y preferencias/λ identificados.\n\nEjecución secuencial IPython limpio en proceso sin kernel/socket; errores abortan y outputs persisten. FiguraPNG inspeccionada, sin prueba de todos los frontends."
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
        "execution_method": "Clean in-process IPython, sequential cells, no Jupyter kernel/socket.",
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
print(f"Executed {count} code cells in process.")
