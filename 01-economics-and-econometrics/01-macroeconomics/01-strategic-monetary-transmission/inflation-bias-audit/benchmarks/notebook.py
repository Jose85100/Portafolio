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
        "# Auditoría monetaria acumulativa: expectativas y delegación\n\n## Resumen ciclo30\nExtensión ejecutada: q*=0,308571 reduce pérdida social de1,25 a0,867406; 144casos exactos y control negativo k0. Fórmulas, derivación, unidades y tradeoff en secciónCiclo30 al final. Se conserva la lección29.\n\nAncla sintética: compromisoL0,75, discreciónL1,25. Una política ingenua pareceL0,5, pero supone expectativas0 y genera inflación media0,5: no es un equilibrio de expectativas racionales. 54casos con dos estados equiprobables exactos; sin Monte Carlo ni datos reales. S2 local."
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
cells.extend(
    [
        n.v4.new_markdown_cell(r"""# Ciclo30: delegación conservadora como extensión acumulativa

El ciclo29 identifica la ventaja de compromiso **asumido**. Ahora mantenemos discreción y expectativas racionales y preguntamos qué peso delegado reduce la pérdida **social**. No mezclamos objetivos: λ pertenece a la sociedad, q al banquero. Es una ilustración clásica de Rogoff, no una teoría nueva. Tres candidatos: aprendizaje adaptativo (cambia RE), reputación repetida (demasiado alcance), delegación estática (seleccionada: reutiliza política y pérdida previas y aísla tradeoff).

## Fórmula original y modificación

Antes, banco y sociedad compartían $L_\lambda=\frac12[\pi^2+\lambda(y-k)^2]$. Propuesta implementada: banco minimiza $L_q$ mientras todas las comparaciones conservan $L_\lambda$. Con el mismo orden temporal y $E\epsilon=0$, $\pi^e=q\alpha k$, $\pi=q\alpha k-q\alpha\epsilon/(1+q\alpha^2)$, $y=\epsilon/(1+q\alpha^2)$.

Por expansión de cuadrados, $J(q)=E L_\lambda=\frac12[(q\alpha k)^2+\lambda k^2+\sigma^2((q\alpha)^2+\lambda)/(1+q\alpha^2)^2]$. Las variables son normalizadas: π,y,k,ε en unidades del modelo; α convierte sorpresa de inflación en producto; λ y q convierten cuadrados de producto en pérdida de inflación. No son puntos porcentuales calibrados.

## Derivación de la regla y unicidad

$J'(q)=\alpha^2[q k^2+\sigma^2(q-\lambda)/(1+\alpha^2q)^3]$. Multiplicar por el factor positivo da $F(q)=q k^2(1+\alpha^2q)^3+\sigma^2(q-\lambda)$. En $[0,\lambda]$, $F'(q)=k^2(1+\alpha^2q)^2(1+4\alpha^2q)+\sigma^2>0$ salvo degeneración k=σ=0; F(0)≤0 y F(λ)≥0. Existe raíz única y minimiza J globalmente para q≥0: fuera de λ la derivada es positiva. En degeneración toda q es equivalente y elegimos baselineλ. No se requiere convexidad global de J. Supuesto indispensable: nombramiento creíble y sin coste; su implementación política no se modela."""),
        n.v4.new_code_cell(
            'from src.delegation import optimal_weight,social_loss,state_average\nd=json.loads((root/"results/delegation-summary.json").read_text())\nprint("Casos",d["cases"],"Ancla",d["anchor"])\nq=optimal_weight(1,1,1,1)\nprint("q óptimo",q,"J social",social_loss(q,1,1,1,1))\nassert abs(social_loss(q,1,1,1,1)-state_average(q,1,1,1,1))<1e-12'
        ),
        n.v4.new_markdown_cell(
            "## Mecanismo, controles negativos y sensibilidad\nReducir q reduce sesgo, pero debilita estabilización. El criterio de éxito es J(q*)≤J(λ)+1e−10 en toda la malla, fórmula/estados y oráculo independientes coinciden a1e−10. La política extrema q0 falla cuando k0 y σ>0: elimina un sesgo que no existe y pierde estabilización. Si σ0,k>0 sí conviene q0. Nunca evaluamos al delegado con su propio objetivo para afirmar una ganancia social."
        ),
        n.v4.new_code_cell(
            'print("Error oráculo",d["max_oracle_loss_error"],"Error estados",d["max_state_error"])\nassert optimal_weight(1,1,0,1)==1\nassert social_loss(0,1,1,0,1)>social_loss(1,1,1,0,1)\nassert optimal_weight(1,1,1,0)==0\nprint("Negativo k0: q0",social_loss(0,1,1,0,1),"baseline",social_loss(1,1,1,0,1))\ndisplay(Image(filename=str(root/"results/delegation.png")))'
        ),
        n.v4.new_markdown_cell(
            "## Evidencia y clasificación honesta\n144 casos exactos, sin muestreo ni inferencia empírica. Aporte: extensión computacional acumulativa y educativa del repositorio; fórmula deriva una especialización lineal-cuadrática de mecanismo clásico. No innovación teórica ni garantía de política real. No multilenguaje añadido: duplicar solver escalar no aporta al objetivo. Tiempo y memoria Python instrumentados son coste del barrido, no RSS ni escalabilidad operacional. Ver informe.md14p, matriz de cinco referencias, research-log.md y roadmap del programa."
        ),
    ]
)
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
