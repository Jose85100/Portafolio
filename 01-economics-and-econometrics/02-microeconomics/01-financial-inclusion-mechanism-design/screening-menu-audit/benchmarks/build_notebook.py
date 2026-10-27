"""Narrative experiment notebook with exact IC/IR algebra and negative controls."""

from pathlib import Path
import json
import nbformat as n

root = Path(__file__).resolve().parents[1]
r = json.loads((root / "results/summary.json").read_text())
a = r["anchor"]
cells = [
    n.v4.new_markdown_cell(f"""# Menús de screening: IC, participación y ejecución

## Resumen
En el ejemplo sintético de dos tipos, el menú estrictamente implementable produce beneficio esperado {a["strict_profit"]:.7f}, frente al mejor contrato único de {a["uniform_profit"]:.7f}. La mejora no es universal: desaparece cuando es óptimo excluir al tipo bajo. Un menú débilmente IC puede fallar con desempates adversos; la participación falla si el tipo bajo está mal especificado. No es evidencia de originación real, default o contratos contingentes al flujo. S2 del componente estático, no del programa completo."""),
    n.v4.new_markdown_cell(
        "## Tres ideas y decisión\nSe compararon extender AR con HAC, invertir inferencia RD y abrir un componente estático de screening en el programa microeconómico S1. Se eligió el tercero para rotar de econometría a diseño de mecanismos y hacer explícitas restricciones IC/IR. Método clásico; contribución incremental auditada, no algoritmo nuevo."
    ),
    n.v4.new_markdown_cell(r"""## Modelo económico y alcance

Dos tipos privados $0<\theta_L<\theta_H$, probabilidad p del alto, utilidad cuasilineal $u_\theta(q,t)=\theta q-t$, opción externa0. Principal ofrece $(q_L,t_L),(q_H,t_H)$, coste real $cq^2/2$, sin competencia o presupuestos. q es cantidad/capacidad normalizada de servicio, t transferencia normalizada; no son tasas de interés o PD.

IR: $\theta_iq_i-t_i\ge0$. IC: $\theta_iq_i-t_i\ge\theta_iq_j-t_j$. Beneficio $\Pi=(1-p)(t_L-cq_L^2/2)+p(t_H-cq_H^2/2)$. No se modelan ventas inciertas, impago, moral hazard o flujo contingente. El programa original sigue teniendo esas brechas."""),
    n.v4.new_code_cell(
        'import json,csv\nfrom pathlib import Path\nimport numpy as np\nfrom IPython.display import display,Image\nfrom src.screening import Economy,analytic,uniform,profit,slacks,strictify,qp,realized\nroot=Path.cwd()\nr=json.loads((root/"results/summary.json").read_text())\nprint(json.dumps(r["config"],ensure_ascii=False,indent=2))'
    ),
    n.v4.new_markdown_cell(r"""## Derivación de la solución

Sumar IC implica $q_H\ge q_L$. Para cantidades monótonas, transferencias máximas con IR baja e IC alta vinculantes: $t_L=\theta_Lq_L$, $t_H=\theta_Hq_H-(\theta_H-\theta_L)q_L$. Sustituir reduce el objetivo a una cuadrática cóncava separable. Por ello

$$q_H=\theta_H/c,\quad q_L=\max\{0,[\theta_L-p(\theta_H-\theta_L)/(1-p)]/c\}.$$

La monotonía se cumple automáticamente y la concavidad garantiza optimalidad global en **este modelo**. La renta del alto es $(\theta_H-\theta_L)q_L$; el bajo recibe cero. Es un mecanismo débilmente IC con equilibrio veraz, no elección única."""),
    n.v4.new_code_cell(
        'e=Economy(**r["config"]["anchor"])\na=analytic(e)\nnum,iterations=qp(e)\nprint("qL,qH,tL,tH:",a)\nprint("IC/IR:",slacks(a,e))\nprint("Beneficio",profit(a,e),"Oráculo QP",profit(num,e),"Iteraciones",iterations)\nassert abs(profit(a,e)-profit(num,e))<1e-7'
    ),
    n.v4.new_markdown_cell(
        "## Baseline optimizado\nUn solo contrato puede servir a ambos tipos o solo al alto. Dentro de cada región se optimizan cantidad y transferencia, luego se escoge el mejor; no usar un precio arbitrario para inflar la mejora. El valor débilmente implementable es el máximo entre θL²/(2c) y pθH²/(2c). Un descuento ε permite participación estricta sin alterar materialmente la comparación."
    ),
    n.v4.new_code_cell(
        'kind,b,bp=uniform(e)\ns=strictify(a,e,r["config"]["epsilon"])\nprint("Mejor contrato único",kind,b,"beneficio",bp)\nprint("Baseline con descuento",r["anchor"]["uniform_strict_profit"])\nprint("Menú estricto",s,"beneficio",profit(s,e))\nprint("Mejora respecto a baseline ideal",profit(s,e)/bp-1)\nprint("Slacks estrictos",slacks(s,e))'
    ),
    n.v4.new_markdown_cell(
        "## Auditoría sobre parámetros\n81 economías determinísticas de grilla: 9 probabilidades×3 costes×3 pares de tipos. Cada una conserva asignaciones, transferencias, restricciones y comparación numérica independiente con QP(SLSQP, inicial cero). Es estática comparativa sintética, no muestreo de una población: no inventar errores Monte Carlo o confianza estadística."
    ),
    n.v4.new_code_cell(
        'rows=list(csv.DictReader((root/"results/grid.csv").open()))\nassert len(rows)==81\nprint("Casos",len(rows),"Máximo error beneficio QP",r["max_qp_profit_gap"],"Error cantidades",r["max_quantity_error"])\nassert r["max_qp_profit_gap"]<=r["config"]["solver_tolerance"]\nfor row in rows:\n if float(row["low"])==1 and float(row["high"])==2 and float(row["cost"])==1:\n  print("p",row["p"],"qL",row["qL"],"menú",row["menu_profit"],"baseline",row["baseline_profit"])'
    ),
    n.v4.new_markdown_cell(
        "## Resultados y fallos de implementación\nIzquierda: la ventaja de menú desaparece al aumentar p y excluir al bajo. Derecha: elegir contratos y optar por no participar cambia resultados cuando IC/IR son débiles o el tipo real difiere del supuesto."
    ),
    n.v4.new_code_cell('display(Image(filename=str(root/"results/comparison.png")))'),
    n.v4.new_markdown_cell(
        "## Falsación1: empates de incentivos\nCon IC débil el tipo alto puede imitar al bajo sin perder utilidad, y el bajo puede elegir la opción externa. El equilibrio veraz no garantiza selección veraz única. Descuentos ε al contrato bajo y2ε al alto crean márgenes estrictos en el ejemplo sin asignaciones distintas."
    ),
    n.v4.new_code_cell(
        'for label,menu in [("Débil",a),("Estricto",s)]:\n print(label,"beneficio contable veraz",profit(menu,e),"elección desempate adverso",realized(menu,e,tie="smallest"))\nassert abs(realized(s,e,tie="smallest")-profit(s,e))<1e-9'
    ),
    n.v4.new_markdown_cell(
        "## Falsación2: preferencias mal especificadas\nSi el tipo bajo real es0,8 en lugar de1, rechaza el contrato de baja cantidad. La ventaja de beneficio puede desaparecer; comparador con información de tipo real se declara oráculo informado, no un baseline con mismo conjunto informativo."
    ),
    n.v4.new_code_cell(
        'print("Menú diseñado para θL1, realθL0.8:",realized(s,e,true_low=.8))\ntrue_e=Economy(.8,2,.2,1)\nprint("Contrato único informado sobre tipo real:",uniform(true_e)[2])\nfirst_best=np.array([1.,2.,1.,4.])\nprint("Ablation sin IC: beneficio aparente",profit(first_best,e),"slacks",slacks(first_best,e))\nprint("El first-best sin renta informativa no es implementable: IC alta negativa.")'
    ),
    n.v4.new_markdown_cell(
        "## Costes y trazabilidad\nComparación de forma cerrada y QP sobre mismas economías, generación excluida. Memoria Python instrumentada no RSS; no extrapolar servicio real. Seeds solo generan casos de tests/microbenchmark; grilla principal determinística."
    ),
    n.v4.new_code_cell(
        'print((root/"results/costs.csv").read_text())\nprint("Versiones",r["versions"])\nprint("SHA256 datos",r["data_sha256"])\nprint("SHA256 fuente",r["source_sha256"])'
    ),
    n.v4.new_markdown_cell(
        "## Lectura crítica y siguientes pasos\n¿Es la utilidad cuasilineal razonable para crédito con liquidez limitada? ¿Cómo cambia IC si se observa flujo con error? ¿Qué restricciones de equidad se necesitan? Este MVP no responde con datos reales: solo aporta un núcleo estático verificado para explorar esas preguntas. Beneficio del principal no equivale a bienestar ni inclusión; qL puede disminuir y el tipo bajo puede quedar excluido.\n\nCinco referencias reales en referencias.bib, informe de14p y límites del componente. Próximos: presupuesto, más tipos y contingencia de flujo con revelación verificable. Notebook ejecutado en IPython limpio en proceso sin kernel/socket; errores abortan y outputs permanecen guardados."
    ),
]
n.write(
    n.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "name": "python3",
                "display_name": "Python3",
                "language": "python",
            },
            "language_info": {"name": "python"},
        },
    ),
    root / "notebook.ipynb",
)
