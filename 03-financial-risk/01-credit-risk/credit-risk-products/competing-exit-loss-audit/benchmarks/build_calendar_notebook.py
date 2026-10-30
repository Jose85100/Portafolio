"""Build executed teaching notebook for cumulative calendar extension."""

import sys
from pathlib import Path

import nbformat as nbf
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
nb = nbf.v4.new_notebook()
nb.cells = []
nb.cells.append(
    nbf.v4.new_markdown_cell(
        "# Calendario e intensidades: de buckets a integración del tiempo de default\nContinuidad de CICLO29: antes se suministraban probabilidades exclusivas por período genérico; no se podía cambiar de calendario sin volver a especificarlas. Ahora usamos intensidades anuales por tramos y conservamos la API original sin reinterpretar sus argumentos. Novedad: adaptación local y verificación; las identidades de riesgos competidores son conocidas.\n\nPregunta: ¿cuánto sesgo introduce descontar todos los defaults al cierre de cada bucket? H preespecificada: >2% a un año, λd=.24, λp=1.2 y fuerza de descuento ρ=.06. Datos enteramente sintéticos."
    )
)
nb.cells.append(
    nbf.v4.new_markdown_cell(
        "## 1. Fórmula original y derivación\nEn el modelo discreto, $D_i=S_{i-1}d_i$, $P_i=S_{i-1}p_i$, $S_i=S_{i-1}(1-d_i-p_i)$ y $EL_{end}=\\sum_i D_i E_iL e^{-\\rho t_i}$, con EAD condicional $E_i$ y LGD $L$.\n\nSuponga intensidades constantes dentro del intervalo: $\\lambda_d,\\lambda_p$ en año$^{-1}$ y $\\Delta_i$ en años. La ecuación $dS(u)/du=-k_iS(u)$, $k_i=\\lambda_d+\\lambda_p$, implica $S(u)=S_{i-1}e^{-k_i u}$. Integrar $\\lambda_d S(u)$ da $d_i=\\lambda_d(1-e^{-k_i\\Delta_i})/k_i$ y análogamente $p_i$. La supervivencia es $e^{-k_i\\Delta_i}$. Si $k_i=0$ ambas salidas son cero. No dividir una probabilidad anual por doce. Tampoco convertir cada salida con $1-e^{-\\lambda\\Delta}$ por separado: suma mal las masas conjuntas.\n\nEsta conversión obtiene probabilidades de **salidas competidoras**, no asume que ambos eventos puedan ocurrir."
    )
)
nb.cells.append(
    nbf.v4.new_markdown_cell(
        "## 2. Propuesta: descuento dentro del intervalo\nSi el default ocurre a tiempo $u$ del intervalo, descontar a $t_{i-1}+u$ en lugar del cierre:\n$$EL_i=S_{i-1}E_iL e^{-\\rho t_{i-1}}\\int_0^{\\Delta_i}\\lambda_d e^{-(k_i+\\rho)u}du\n=S_{i-1}E_iL e^{-\\rho t_{i-1}}\\frac{\\lambda_d}{k_i+\\rho}(1-e^{-(k_i+\\rho)\\Delta_i}).$$\nUnidades: integral y masas adimensionales, EAD en dinero y LGD fracción. `src/calendar.py` usa `expm1` para evitar cancelación cerca de cero; `integrated` corresponde al cociente/integral, `exact` a cada ELi y `endpoint` al baseline. Para $k+\\rho=0$, λd=0 y pérdida cero. Ambos modelos comparten probabilidades, horizonte, EAD y tasa: solo cambia tiempo de descuento. No se modifica ni descalifica el baseline discreto29.\n\nρ≥0 implica $EL_{end}\\le EL_{exact}$ pues $e^{-\\rho\\Delta}\\le e^{-\\rho u}$. Para coeficientes constantes, partir un intervalo no cambia la integral exacta por aditividad; sí reduce el sesgo del cierre. No es prueba de calibración ni teorema sobre datos reales."
    )
)
nb.cells.append(
    nbf.v4.new_code_cell(
        "from pathlib import Path\nroot=Path.cwd()\nfrom src.calendar import project_calendar\nimport csv,json,math\nfrom IPython.display import display,Image\nprint(json.dumps(json.loads((root/'results/calendar_metrics.json').read_text()),indent=2))\nrows=list(csv.DictReader((root/'results/calendar.csv').open()))\nfor r in rows: print(r)"
    )
)
nb.cells.append(
    nbf.v4.new_markdown_cell(
        "## 3. Ejecución y sensibilidad\nUn año, EAD100, LGD.45, intensidades .24/1.2. Tasas0,.06,.20 y 1,2,4,12,52,360 intervalos. Mismos parámetros anuales; no se cambia el DGP entre calendarios. Tabla cruda muestra ambas pérdidas y masa total."
    )
)
nb.cells.append(
    nbf.v4.new_code_cell(
        "display(Image(filename=str(root/'results/calendar.png')))\none=project_calendar([1.],[.24],[1.2],[100.])\nmonthly=project_calendar([1/12]*12,[.24]*12,[1.2]*12,[100.]*12)\nprint('Invariancia exacta:',abs(one.exact_loss-monthly.exact_loss))\nassert abs(one.exact_loss-monthly.exact_loss)<1e-12\nassert one.endpoint_loss<one.exact_loss"
    )
)
nb.cells.append(
    nbf.v4.new_markdown_cell(
        "## 4. Casos negativos y límite de la mejora\nCon descuento cero ambos coinciden: no se fabrica mejora. Con default cero, pérdida cero. La invariancia de partición exige EAD/intensidades constantes dentro del tramo; al refinar una trayectoria amortizable no debe cambiarse silenciosamente esa función. La mejora es exactitud bajo supuestos, no mayor capacidad predictiva. H1 ya no implica misma pérdida al variar intensidad prepago: esta API continua tiene eventos en tiempos distintos y no reinterpreta el negativo de la API discreta29.\n\nNo se estima dependencia de covariables, censura, errores de calibración ni probabilidad de prepago a datos. No usar cifras para provisiones regulatorias. Fórmula conocida adaptada a calendario explícito; `benchmarks/prior-art.md` clasifica cinco trabajos y `research-log.md` conserva elección y siguiente prueba."
    )
)
nb.cells.append(
    nbf.v4.new_code_cell(
        "zero=project_calendar([1.],[.24],[1.2],[100.],discount_force=0.)\nassert abs(zero.exact_loss-zero.endpoint_loss)<1e-12\nprint('Sin descuento:',zero)\nprint((root/'results/tests.txt').read_text())"
    )
)
nb.metadata["kernelspec"] = {
    "display_name": "Python3",
    "language": "python",
    "name": "python3",
}
nb.metadata["execution"] = {
    "mode": "IPython sequential in-process",
    "outputs": "captured from real execution",
}
shell = InteractiveShell.instance()
for count, cell in enumerate((c for c in nb.cells if c.cell_type == "code"), 1):
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
    for rich in captured.outputs:
        cell.outputs.append(
            nbf.v4.new_output("display_data", data=rich.data, metadata=rich.metadata)
        )
nbf.validate(nb)
nbf.write(nb, root / "calendar_notebook.ipynb")
