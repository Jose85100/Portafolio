"""Build substantive, rerunnable teaching companion from executed experiment."""

from pathlib import Path
import json
import nbformat as n

root = Path(__file__).resolve().parents[1]
r = json.loads((root / "results/summary.json").read_text())
a = [s for s in r["summary"] if s["scenario"] == "Asymmetric curvature"]
cells = [
    n.v4.new_markdown_cell(f"""# RD: curvatura, ancho de banda e identificación

## Resumen
En DGP sintético de curvatura asimétrica, el baseline global h=1 presenta RMSE={a[0]["rmse"]:.5f}; local h=0,2 RMSE={a[2]["rmse"]:.5f}. Una ventana más estrecha h=0,08 empeora RMSE={a[3]["rmse"]:.5f} por varianza. Localizar no corrige una discontinuidad de Y(0): no confundir buen ajuste con identificación causal. S2 de este componente, no validación empírica."""),
    n.v4.new_markdown_cell(r"""## Problema económico y tres ideas candidatas

Se compararon ampliar AR con HAC, invertir AR y abrir auditoría RD. Se eligió RD por diversificación de estimandos económicos y brecha no cubierta, manteniendo MVP pequeño. Pregunta: ¿restringir extrapolación lineal reduce error de un efecto de política en umbral cuando las funciones son curvas? ¿Qué pasa si se rompe continuidad?

## Método y supuestos

Running x uniforme[-1,1], tratamiento $T=1[x\ge0]$, potencial $Y(0)=.4x+3x^2+\kappa Tx^2+\lambda T+\epsilon$, efecto constante $Y(1)-Y(0)=1$, $\epsilon\sim N(0,.3^2)$. Con λ=0, esperanza Y(0) continua aunque κ=4 produzca curvaturas distintas. Con λ=0,6 la continuidad falla. Observar discontinuidad no identifica por sí mismo el efecto del tratamiento.

Kernel uniforme $1[|x|\le h]$, regresiones lineales independientes por lado. $\hat\tau_h=\hat a_+(h)-\hat a_-(h)$, $\hat a_s=\bar y_s-\hat b_s\bar x_s$. Baseline usa h=1 y exactamente mismas pendientes separadas; solo cambia h. No implementamos CCT, RBC ni intervalos causales."""),
    n.v4.new_code_cell(
        'import json,csv\nfrom pathlib import Path\nimport numpy as np\nfrom IPython.display import display,Image\nfrom src.rd import estimate,sample\nroot=Path.cwd()\nr=json.loads((root/"results/summary.json").read_text())\nprint(json.dumps(r["config"],ensure_ascii=False,indent=2))'
    ),
    n.v4.new_markdown_cell(r"""## Sesgo poblacional calculable

Para U[0,h], la proyección lineal de $q x^2$ tiene intercepto $-qh^2/6$. Por simetría ocurre lo mismo en el lado negativo. Luego $\tau_h^{proj}=1+\lambda-\kappa h^2/6$. Es una propiedad algebraica del DGP uniforme cuadrático, no teorema general sobre todos los RD.

Compruébalo con malla densa sin ruido; no confundir esta comprobación numérica con evidencia empírica."""),
    n.v4.new_code_cell(
        'x=np.linspace(-1,1,100000)\nt=(x>=0)\ny=t+.4*x+3*x*x+4*t*x*x\nfor h in [1,.4,.2,.08]:\n expected=1-4*h*h/6\n actual=estimate(x,y,h)[0]\n print("h",h,"Proyección",expected,"Malla",actual)\n assert abs(actual-expected)<1e-4'
    ),
    n.v4.new_markdown_cell(
        "## Datos y estimador\n1.500 seeds por escenario, n1200; total18.000 estimaciones(3 escenarios×4ventanas×1500). Datos generados localmente y CSV crudo versionado con recuentos por lado. Mismas realizaciones entre h y mismo seed entre escenarios: comparar pareado. Sin población observada, sin datos sensibles."
    ),
    n.v4.new_code_cell(
        'x,y=sample(20261025,1200)\nfor h in [1,.4,.2,.08]:\n value,nl,nr=estimate(x,y,h)\n print("h",h,"salto",round(value,5),"n izquierda/derecha",nl,nr)\nprint("Este es un ejemplo, no la conclusión Monte Carlo.")'
    ),
    n.v4.new_markdown_cell(
        "## Resultados de todas las réplicas\nSesgo y RMSE usan el efecto verdadero conocido1. SD es variabilidad entre realizaciones. MC SE de la media no es un IC de efecto en una muestra. Cuantiles q025/q975 son cuantiles Monte Carlo, no intervalos inferenciales."
    ),
    n.v4.new_code_cell(
        'rows=list(csv.DictReader((root/"results/replications.csv").open()))\nassert len(rows)==18000\nfor s in r["summary"]:\n print(s["scenario"],"h",s["h"],"media",round(s["mean"],5),"sesgo",round(s["bias"],5),"RMSE",round(s["rmse"],5),"SD",round(s["sd"],5),"MCSE",round(s["mean_mc_se"],5))'
    ),
    n.v4.new_markdown_cell(
        "## Comparación visual\nPanel izquierdo: media y±1,96SE Monte Carlo. Panel derecho: RMSE respecto al efecto verdadero. Bandwidth pequeño reduce sesgo de curvatura pero puede aumentar varianza."
    ),
    n.v4.new_code_cell('display(Image(filename=str(root/"results/comparison.png")))'),
    n.v4.new_markdown_cell(
        "## Hipótesis y contrafactual negativo\nCriterio previo: RMSE local h0,2≤50% de global en curvatura asimétrica válida. La ventana h0,08 es ablation de varianza. Se reporta también dónde falla la recomendación, sin seleccionar el mejor h usando la verdad para una política real."
    ),
    n.v4.new_code_cell(
        'valid=[s for s in r["summary"] if s["scenario"]=="Asymmetric curvature"]\nratio=valid[2]["rmse"]/valid[0]["rmse"]\nprint("Ratio RMSE h.2/global",ratio,"Criterio",ratio<=.5)\nprint("h.08 peor que h.2",valid[3]["rmse"]>valid[2]["rmse"])\nprint("Diferencia MSE pareada",valid[2]["paired_mse_difference"],"SE",valid[2]["paired_mse_se"])'
    ),
    n.v4.new_markdown_cell(
        "## Falsación de identificación\nλ0,6 provoca salto latente en Y(0). Efecto causal verdadero permanece1, pero h→0 identifica salto observado1,6. El baseline puede parecer cercano a1 por cancelación de dos sesgos: esa coincidencia tampoco valida causalidad."
    ),
    n.v4.new_code_cell(
        'invalid=[s for s in r["summary"] if s["scenario"]=="Continuity violated"]\nfor s in invalid:print("h",s["h"],"media",s["mean"],"efecto verdadero1","salto límite1.6")\nprint("Acercarse a1.6 no recupera efecto1.")'
    ),
    n.v4.new_markdown_cell(
        "## Coste y reproducibilidad\nCostes instrumentados de100llamadas por brazo/tamaño; memoria Python no RSS, no extrapolar producción. Los hashes vinculan código y ledger. Versiones directas fijadas, no lock transitivo."
    ),
    n.v4.new_code_cell(
        'print((root/"results/costs.csv").read_text())\nprint("Versiones",r["versions"])\nprint("SHA256 datos",r["data_sha256"])\nprint("SHA256 núcleo",r["source_sha256"])'
    ),
    n.v4.new_markdown_cell(
        "## Límites, preguntas y siguientes pasos\n¿Por qué h pequeño empeora un DGP suave simétrico? ¿Cómo seleccionar h sin conocer efecto1? ¿Qué evidencia externa respalda continuidad? No resolvemos inferencia robusta sesgo/RBC, fuzzy RD, manipulación, running discreto, clusters o datos reales. No afirmar que local siempre domina global ni que simulación demuestra causalidad.\n\nCinco referencias verificadas en referencias.bib; informe14p analiza≥3ideas y selección. Siguiente: comparador rdrobust, selecciónbandwidth válida y falsaciones de manipulación.\n\nEjecución secuencial IPython limpio en proceso sin kernel/socket;outputs persistidos,errores abortan. Figura revisada en PNG; no certifica todos los frontends."
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
