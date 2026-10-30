"""Execute30October scale-aware moments notebook in a fresh IPython namespace."""

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
nb.metadata.execution = {
    "executor": "IPython in-process",
    "scope": "fresh shell, sequential execution, abort on error; separate kernel not tested",
}
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells = [
    md(r"""# Lección30: unidades, varianza y rango de máquina
## 1 Pregunta y continuidad
El29 verificó cancelación con offset y admitió que datos finitos pueden producir M2 infinito. Aquí no cambiamos algoritmo29: lo envolvemos con escala externa binaria y salida tipada. ¿Podemos recuperar una desviación estándar finita aun si su cuadrado no cabe?
## 2 Derivación propia de una identidad clásica
Sea $s=2^e>0$, $y_i=x_i/s$ y $\bar y=n^{-1}\sum y_i$. Entonces $\bar x=s\bar y$ y
$$M_{2,x}=\sum_i(x_i-\bar x)^2=s^2\sum_i(y_i-\bar y)^2=s^2M_{2,y}.$$
Para $d\in\{0,1\}$ con $n>d$,
$$V_{x,d}=2^{2e}\frac{M_{2,y}}{n-d},\qquad \sigma_{x,d}=2^e\sqrt{\frac{M_{2,y}}{n-d}}.$$
**Correspondencia código:** `scaled_moments` usa `ldexp(x,-exponent)`; el núcleo29 calcula M2; `ldexp(variance_scaled,2*exponent)` y `ldexp(sqrt(...),exponent)` devuelven unidades. Varianza tiene unidades U², SD U. No es fórmula inédita ni cota universal de error. Escala se declara, no se aprende de datos futuros.
## 3 Hipótesis local/configuración
Para seis fixtures con e=frexp(unit)[1], error relativo SD<=1e-12. unit1,1e200,1e-200, n128/4096. Decimal80 sobre floats recibidos. Dominio operacional: cada observación normalizada no nula tiene magnitud entre2^-400 y2^400; fuera devuelve normalization_failure, para ajustar e."""),
    code(
        "import math,json,csv\nfrom pathlib import Path\nfrom IPython.display import display,Image\nfrom src.scaled import scaled_moments\nx=[1e200,2e200,3e200,4e200]\na=scaled_moments(x,665)\nprint(a)\nassert a.status=='variance_overflow' and math.isfinite(a.std)\nprint('SD/unidad:',a.std/1e200,'vs sqrt(1.25):',math.sqrt(1.25))"
    ),
    md(r"""## 4 Experimento y sensibilidad
¿Por qué elegir potencias de dos? La operación desplaza exponente sin introducir división decimal, siempre que el resultado siga representable. La ventana2^±400 es conservadora, no óptima; evita muchas normalizaciones peligrosas pero sacrifica rango dinámico mixto. No elimina pérdida de representación anterior al ingreso. Variamos e por±400/±1000 y registramos rechazos, no los escondemos del denominador."""),
    code(
        "s=json.loads(Path('results/scale_summary.json').read_text())\nprint(json.dumps(s,indent=2))\nrows=list(csv.DictReader(Path('results/scale_raw.csv').open()))\nprint([r for r in rows if r['n']=='128' and r['method']=='scaled'])"
    ),
    code("display(Image(filename='results/scale_audit.png'))"),
    md(r"""## 5 Ablación negativa y decisión
Sin escala: kernel29 y NumPy pueden devolver inf para varianza grande y cero para pequeña, aunque SD sea representable. No es fallo de NumPy devolver varianza no representable: el contrato de nuestra extensión distingue SD disponible y varianza no representable. Baseline fuerte NumPy dos pasadas sigue siendo mejor opción por rendimiento en dominio usual; no afirmamos speedup. Escala incorrecta se rechaza; no es detector universal de pérdida de significancia.
## 6 Enseñar los límites
En x=1e16+(0,1,2,3) se conserva el negativo29: ninguna escala recupera incrementos perdidos. Mezclas de órdenes1e±200 no caben juntas en nuestra ventana. Esto es limitación de diseño, no un teorema de imposibilidad para otros métodos. Prototipo acumulativo, sin validación operacional ni equivalencia S2=M2."""),
    code(
        "assert s['chosen_max_relative_sd_error']<=1e-12\nassert scaled_moments([1e200,2e200],0).status=='normalization_failure'\nprint('Escala mala:',scaled_moments([1e200,2e200],0))\nprint('Rango mixto:',scaled_moments([1e-200,1e200],0))\nprint('Representación perdida:',scaled_moments([1e16+i for i in range(4)],54))"
    ),
]
InteractiveShell.clear_instance()
shell = InteractiveShell.instance()
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
    for name, value in [("stdout", captured.stdout), ("stderr", captured.stderr)]:
        if value:
            cell.outputs.append(nbf.v4.new_output("stream", name=name, text=value))
    for output in captured.outputs:
        cell.outputs.append(
            nbf.v4.new_output(
                "display_data", data=output.data, metadata=output.metadata
            )
        )
nbf.validate(nb)
nbf.write(nb, root / "notebook_scale.ipynb")
