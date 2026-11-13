"""Generate a narrative notebook from executed experiment data; no fabricated outputs."""

from pathlib import Path
import json
import nbformat as n

root = Path(__file__).resolve().parents[1]
r = json.loads((root / "results/summary.json").read_text())
s = r["summary"][3]
cells = [
    n.v4.new_markdown_cell(f"""# AR bajo heterocedasticidad: robustez y límites

## Resumen de evidencia sintética
Con n=1000 y exclusión válida, F homocedástico rechaza {s["rates"][0]:.2%}, HC1 {s["rates"][1]:.2%}, HC3 {s["rates"][2]:.2%}, frente a nivel nominal5%. La corrección de heterocedasticidad cambia garantía finita exacta por calibración asintótica. No corrige exclusión inválida ni demuestra causalidad real."""),
    n.v4.new_markdown_cell(r"""## Contexto y método

La auditoría previa estudió relevancia débil bajo errores homocedásticos. Aquí preguntamos qué ocurre si la varianza depende de z. DGP $x=cz/\sqrt n+v$, $u=\sqrt{(0.1+z^2)/1.1}(0.8v+0.6e)$, $y=x+u+\gamma z$, normales independientes z,v,e. En control homocedástico la escala es1. **Supuestos:** independencia entre observaciones, momentos finitos y exclusión γ=0. No hay clusters/series.

Para $r=y-\beta_0x$, regresamos r en [1,z]. Sea $S=\sum z_c^2$, $\hat b=\sum z_cr_c/S$, $h_i=1/n+z_{ci}^2/S$ y $\hat e_i=r_{ci}-\hat b z_{ci}$. $V_{HC1}=\frac{n}{n-2}\sum z_c^2\hat e^2/S^2$; $V_{HC3}=\sum z_c^2\hat e^2/(1-h)^2/S^2$. El estadístico $\hat b^2/V$ se calibra con $\chi^2_1$ **asintótico**, no F exacto. No divide por la primera etapa.

Hipótesis predefinida: HC3 en [3%,7%] para n1000 heterocedástico válido y exceso de F sobre HC3 ≥5pp. HC1 es ablation. γ=0,2 es falsación de exclusión, no potencia bajo β alternativo."""),
    n.v4.new_code_cell(
        'import json, csv\nfrom pathlib import Path\nfrom IPython.display import display, Image\nfrom src.robust import sample, robust_ar\nroot=Path.cwd()\nr=json.loads((root/"results/summary.json").read_text())\nprint(json.dumps(r["config"],ensure_ascii=False,indent=2))'
    ),
    n.v4.new_markdown_cell(
        "## Datos y trazabilidad\n10.000 réplicas sintéticas guardadas en CSV con seeds, tres p-valores y decisiones. Los métodos comparten muestras, y los escenarios comparten semillas; no tratar resultados como muestras independientes. Versiones, hardware, fuente SHA256 y datos SHA256 en JSON. Sin datos personales ni fuentes operativas."
    ),
    n.v4.new_code_cell(
        'rows=list(csv.DictReader((root/"results/replications.csv").open()))\nassert len(rows)==10000\nfor s in r["summary"]:\n print(s["scenario"], "F/HC1/HC3", [round(p*100,2) for p in s["rates"]],"SE MC",[round(p*100,3) for p in s["mc_se"]])\nprint("Datos SHA256",r["data_sha256"])'
    ),
    n.v4.new_markdown_cell(
        "## Resultados\nBarras de error ±1,96SE Monte Carlo: incertidumbre entre simulaciones, no IC de efecto causal empírico. Heterocedasticidad rompe garantía exacta de F; HC3 es asintótico. Con exclusión inválida también falla HC3."
    ),
    n.v4.new_code_cell('display(Image(filename=str(root/"results/comparison.png")))'),
    n.v4.new_markdown_cell(
        "## Checks y sensibilidad\nValidar invariancia de AR al cambiar relevancia manteniendo misma nula y shocks, y evaluar umbrales registrados sin forzar resultado."
    ),
    n.v4.new_code_cell(
        'a=sample(23,500,True,c=0)\nb=sample(23,500,True,c=10)\nassert abs(robust_ar(*a,1)-robust_ar(*b,1))<1e-12\ns=r["summary"][3]\nprint("HC3 dentro umbral:", .03<=s["rates"][2]<=.07)\nprint("Exceso F >=5pp:",s["rates"][0]-s["rates"][2]>=.05)\nprint((root/"results/costs.csv").read_text())'
    ),
    n.v4.new_markdown_cell(
        "## Lectura crítica y límites\nLa inferencia robusta a relevancia débil y heterocedasticidad requiere instrumentos válidos. No prueba exclusión. HC3 puede ser conservador o distorsionado en muestras pequeñas; no se obtiene garantía uniforme de este Monte Carlo. No intervalos invertidos, clustering, HAC, instrumentos múltiples, poder ni datos reales. S2 local; garantía asintótica frente a F exacto solo en su DGP válido.\n\nSiguiente: errores dependientes; inversión que preserve conjuntos no acotados; potencia bajo alternativas. Ver siete referencias en referencias.bib y análisis de 14 puntos en informe.md.\n\nNotebook ejecutado secuencialmente con IPython limpio en proceso sin kernel/socket; errores abortan y outputs quedan persistidos."
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
