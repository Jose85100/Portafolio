"""Build the program's primary drift report and execute its companion notebook."""

import csv
import json
from pathlib import Path
import nbformat as nbf
from scripts_notebook import execute_in_process


def main():
    rows = list(csv.DictReader(Path("benchmarks/drift-summary.csv").open()))
    result = json.loads(Path("benchmarks/drift-results.json").read_text())
    lines = []
    for scenario in ["null", "mean_shift", "scale_shift", "matched_mixture", "correlated_null"]:
        values = []
        for m in ["fr", "ks", "w1"]:
            r = next(r for r in rows if r["n"] == "128" and r["scenario"] == scenario and r["method"] == m)
            values.append(
                f"{100 * float(r['rate']):.2f}% [{100 * float(r['lower95']):.2f}, {100 * float(r['upper95']):.2f}]"
            )
        lines.append("| " + scenario + " | " + " | ".join(values) + " |")
    report = f"""# Geometría de información para detección de cambios — revisión 2026-10-21

## Alineación y pregunta del programa
¿Cuándo un detector Fisher–Rao basado en proyección gaussiana distingue cambios de media/escala y
cuándo pierde cambios de forma frente a KS y Wasserstein-1?
La entrega anterior solo auditaba equivalencias categóricas. Era un componente numérico útil,
pero no cerraba esta pregunta de detección continua. Se conserva como regresión y anexo
docs/categorical-audit.md. Este informe, drift_notebook.ipynb y src/drift.py son ahora el hilo principal.

## Modelo implementado y supuestos
Se estima cada ventana con N(mu,sigma²) usando media y desviación MLE (ddof=0).
Se compara en la variedad normal, con métrica ds²=(dmu²+2 dsigma²)/sigma².
La distancia exacta es sqrt(2)*acosh(1+z), con
z=((mu1-mu2)²+2(sigma1-sigma2)²)/(4 sigma1 sigma2).
Se evalúa como 2sqrt(2)*asinh(sqrt(z/2)) para evitar cancelación cerca de igualdad.
Esta fórmula conocida coincide con Miyamoto et al., sección 4.4.1; no es un algoritmo nuevo.
El oráculo usa acosh a 80 dígitos y los tests verifican simetría, identidad e invariancia afín.

El nombre correcto es FR entre PROYECCIONES gaussianas. Si P y Q no son normales,
la distancia calculada no es la distancia Fisher–Rao entre sus leyes originales.
Por ejemplo, N(0,1) y la mezcla equiprobable N(-.95,1-.95²)/N(.95,1-.95²)
tienen ambos media cero y varianza uno: las proyecciones coinciden, aunque las leyes no.
Con muestras finitas el score puede diferir por variación de los estimadores.

## Detector y calibración implementados
API: calibrate(reference, independent_baseline_windows, alpha=.05, delta=.05);
Detector.predict(current) retorna tres scores y tres decisiones independientes.
Una ventana de referencia se fija por tamaño, separada de las 399 ventanas de calibración.
Los tres métodos usan las MISMAS ventanas: FR, KS y W1 dividido por la desviación de referencia.
Se calibra la ESTADÍSTICA KS; no se interpreta el p-valor asintótico que SciPy también calcula.

Para controlar la incertidumbre de calibración se usa un límite de tolerancia no paramétrico.
Con B scores IID del nulo y p=1-alpha, se toma
k=1+Q_Binomial(B,p)(1-delta/3); el umbral es el k-ésimo score ordenado.
Si k>B, el umbral es infinito y no se dispara una alarma.
Se rechaza solo con score > umbral; los empates son conservadores.
La razón: la probabilidad de que S_(k) quede por debajo del cuantil p es
P(Binomial(B,p)>=k)<=delta/3. Unión de los tres métodos da probabilidad de fallo <=delta.
No requiere independencia entre métodos.

**Alcance exacto:** con probabilidad al menos 1-delta sobre la calibración, cada detector tiene
probabilidad condicional de falsa alarma por nueva ventana <=alpha, bajo la misma ley de
ventanas limpias e independientes y referencia fija. No garantiza que en 300 ensayos la tasa
observada sea <=.05; tampoco controla la unión de alarmas de los tres métodos ni un horizonte
secuencial infinito. Si se desea una alarma conjunta, hay que recalibrar la regla combinada.
NIST documenta límites de tolerancia; la implementación binomial específica se deriva aquí y se testea.

## Diseño e hipótesis
experiments/drift.json fija n=32/128, 399 ventanas limpias de calibración y 300 datasets de evaluación
por escenario/tamaño (3.000 ventanas de evaluación; 9.000 decisiones).
Media desplazada .8; escala 1.6; mezcla de iguales momentos; nulo IID; nulo AR(1) estacionario phi=.8.
Referencia y calibración se generan con seed=20261021+n.
Cada evaluación usa una semilla distinta guardada en CSV; ninguna evaluación entra en el umbral.
La mezcla y AR1 son controles negativos esenciales, no se borran de las conclusiones.
El AR1 conserva marginales N(0,1) pero viola la ley IID de ventanas de calibración.

Hipótesis de potencia acotada: FR >=.60 para los desplazamientos de media y escala especificados
a n=128; error absoluto del oráculo <=1e-10. No se plantea superioridad universal.
Los tamaños de cambio son relativamente grandes: 100% observado no implica sensibilidad a drift pequeño.
Una sola referencia y calibración por n: Wilson cuantifica evaluación condicionada a esa calibración,
no variación entre múltiples referencias o conjuntos de calibración.
Es una revisión exploratoria motivada por problemas de alineación; no un estudio confirmatorio independiente.

## Resultado con n=128
Tasas sobre 300 datasets; corchetes Wilson 95% (no simultáneos).

| Escenario | FR proyectado | KS calibrado | W1 calibrado |
|---|---:|---:|---:|
{chr(10).join(lines)}

```json
{json.dumps(result["checks"], indent=2)}
```

### Resultado negativo de calibración conservado
El piloto con rango marginal ceil((B+1)(1-alpha)) dio 9% de falsas alarmas FR a n=128.
Se conservan drift-exploratory-summary.csv y drift-exploratory-results.json.
Un control marginal sobre calibraciones aleatorias no es un control condicional para cada conjunto fijo.
Se añadió el rango de tolerancia con delta y Bonferroni, manteniendo las mismas muestras para comparar
el efecto de la corrección; esto NO es una nueva validación externa independiente.
La evaluación final FR observada puede superar .05 por azar; su intervalo debe leerse completo.
No se relajan umbrales para ocultar el resultado.

## Interpretación crítica
FR aprovecha su estructura para cambios gaussianos de localización/escala; W1 también.
Para la mezcla de iguales momentos, KS/W1 detectan el cambio que la proyección descarta.
El nulo AR1 dispara demasiadas alarmas: confirma el riesgo de trasladar calibración IID a series temporales.
No se promete detector macroeconómico, regulatorio ni de drift bancario listo para producción.
El aporte es una comparación de modelos de distribución, sus pérdidas de información y calibración,
en lugar de contar tests como si demostraran impacto científico.

## Artefactos, arquitectura y reproducción
Un comando desde esta carpeta: make run.
src/ contiene API, geometría, oráculos y benchmarks; tests/ valida contrato, bordes, propiedades,
estadísticos de orden y baselines. experiments/drift.json configura el estudio continuo.
data/drift-examples.npz guarda referencias y vistas previas de calibración/evaluación; CSV guarda scores,
decisiones y semillas completas para reconstruir todo, no solo las vistas previas.
benchmarks/drift-calibration.csv conserva 798 filas; drift-raw-32/128.csv 1.500 filas cada uno.
drift-summary.csv conserva los 30 resultados, incluidos fallos y sus intervalos.
drift_notebook.ipynb se ejecuta con outputs y código gráfico editable.
notebook.ipynb mantiene la auditoría categórica como anexo ejecutable.
La figura se inspecciona por separado; la inspección visual integral de notebooks en visor no se reclama.

Los tiempos de drift-raw incluyen las tres funciones y validación; excluyen generación de datos.
Memoria tracemalloc en llamada separada, no RSS. Hardware: {json.dumps(result["hardware"])}.
Dependencias directas fijadas; environment.txt registra transitivas sin garantizar lock completo.
Ruff, formato, mypy, pytest y cobertura medida también de src/drift.py, más numerical-core.
Las pruebas de cobertura no certifican calibración económica ni equivalen a revisión científica externa.

![Detección](benchmarks/drift.png)

## Integración y trazabilidad
Se resolvieron conflictos del PR con main en ambos índices y requirements-research.in, conservando el programa 05.
Los índices contabilizan ahora 8 prototipos S2 acotados y 12 S1.
El avance del programa 02 sigue acotado a datos categóricos/continuos univariados y escenarios sintéticos.
Los módulos previos y sus resultados se mantienen como evidencia auxiliar, sin vender la equivalencia conocida
como la contribución principal. El mismo PR concentra la corrección, sin crear otro proyecto paralelo.

## Límites pendientes
Calibración por bloques para dependencia temporal; varias referencias y calibraciones independientes;
drifts pequeños/locales; Student/colas pesadas y degeneración; familias multivariantes;
datos públicos licenciados y evaluación financiera; monitoreo secuencial con presupuesto de falsas alarmas.
El validador declara qué se ejecutó y no presenta estos pendientes como resueltos.

## Referencias y rúbrica
Fórmulas gaussianas: Miyamoto et al. v3 (2024). Calibración por rangos: Shafer–Vovk (2008) como contexto;
límites de tolerancia NIST; KS y Wasserstein: documentación oficial SciPy 1.17.0.
referencias.bib conserva las cinco entradas originales y añade cuatro pertinentes a la corrección.
Novedad incremental 2/5; rigor 4/5; reproducibilidad 4/5; código 4/5; claridad 4/5;
impacto potencial 3/5; honestidad 5/5; MVP ejecutable 5/5.

Siguiente iteración recomendada:
1. advanced-research: calibración por bloques y evaluación con dependencia temporal.
2. advanced-research: replicar referencias/calibraciones e incorporar cambios pequeños y colas pesadas.
3. quantitative-methods: evaluar una regla conjunta FR/KS/W1 con control explícito de múltiples alarmas.
"""
    Path("informe.md").write_text(report)
    cells = [
        nbf.v4.new_markdown_cell(
            "# Detección de cambios con geometría de información\n## tl;dr\nEl método gaussiano debe evaluarse como proyección: detecta media/escala pero pierde cambios de forma. Comparación con KS y Wasserstein y calibración separada."
        ),
        nbf.v4.new_markdown_cell(
            "## Context & Methods\n### Key Assumptions\nReferencia fija, ventanas de calibración limpias e independientes; una decisión por batch, sin garantía secuencial. Configuración experiments/drift.json. Fórmulas y prior art en informe.md.\n### 1. Datos y controles"
        ),
        nbf.v4.new_code_cell(
            "import json,csv\nfrom pathlib import Path\nimport numpy as np\nfrom IPython.display import display,Image\nfrom src.drift import scores,calibrate\nfrom src.drift_benchmark import plot\nconfig=json.loads(Path('experiments/drift.json').read_text())\nresult=json.loads(Path('benchmarks/drift-results.json').read_text())\nprint(config['question'])\nprint(result['checks'])\nassert all(result['passed'].values())"
        ),
        nbf.v4.new_markdown_cell(
            "## Data\n### 2. Recalibración desde semilla y predicción real\nLa evaluación no participa en el ajuste del umbral."
        ),
        nbf.v4.new_code_cell(
            "data=np.load('data/drift-examples.npz')\nn=128\nrng=np.random.default_rng(config['seed']+n)\nreference=rng.normal(size=n)\nwindows=rng.normal(size=(config['calibration_windows'],n))\nnp.testing.assert_array_equal(reference,data['reference_128'])\ndetector=calibrate(reference,windows,config['alpha'],config['calibration_delta'])\nvalues,alarms=detector.predict(data['128_scale_shift_0'])\nprint('FR,KS,W1 scores:',values,'alarms:',alarms,'thresholds:',detector.thresholds)\n# Igualdad de momentos no preserva la ley.\na=np.linspace(-1,1,128);a=(a-a.mean())/a.std()\nb=np.tile([-1.,1.],64)\nprint('Same sample moments, distinct shapes:',scores(a,b))\nassert scores(a,b)[0]<1e-12 and scores(a,b)[1]>.1"
        ),
        nbf.v4.new_markdown_cell(
            "## Results\n### 3. Todas las tasas a n=128\nWilson 95%, condicionado a una referencia/calibración; AR1 viola el supuesto IID."
        ),
        nbf.v4.new_code_cell(
            "rows=list(csv.DictReader(Path('benchmarks/drift-summary.csv').open()))\nfor row in rows:\n    if row['n']=='128':\n        print(row['scenario'],row['method'],round(float(row['rate']),3),[round(float(row[c]),3) for c in ['lower95','upper95']])"
        ),
        nbf.v4.new_markdown_cell(
            "### 4. Figura regenerada desde CSV\nEl código de dibujo editable vive en src/drift_benchmark.py."
        ),
        nbf.v4.new_code_cell(
            "typed=[{**r,'n':int(r['n']),'rate':float(r['rate']),'lower95':float(r['lower95']),'upper95':float(r['upper95'])} for r in rows]\nplot(typed)\ndisplay(Image(filename='benchmarks/drift.png'))"
        ),
        nbf.v4.new_markdown_cell(
            "## Takeaways\nNo existe superioridad universal. La proyección gaussiana descarta cambios de forma; KS/W1 conservan información distinta. La calibración de rangos incorpora incertidumbre del umbral y se limita al supuesto de ventanas limpias de igual ley. AR1 muestra un fallo importante. El piloto marginal con 9% de falsas alarmas se conserva; esta corrección es exploratoria, no validación externa. Abrir en Jupyter para revisión visual integral; figura revisada por separado."
        ),
    ]
    nb = nbf.v4.new_notebook(
        cells=cells,
        metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}},
    )
    nb = execute_in_process(nb)
    nbf.validate(nb)
    nbf.write(nb, "drift_notebook.ipynb")
    print("Primary drift report and four executed notebook cells saved.")


if __name__ == "__main__":
    main()
