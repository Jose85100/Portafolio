# Sesgo inflacionario: objetivo y consistencia de expectativas

29 de octubre de 2026. `main` inspeccionado en `022f6bd`, sin PR abiertos al inicio. Los trabajos del 28 están integrados; en particular el bien público se conservó mediante PR #97. Este componente es nuevo, en rama/worktree propios.

## 1. Título

Auditoría de compromiso, discreción y alternativas incompatibles con expectativas racionales.

## 2. Tres ideas y novedad incremental

| Idea | Brecha | Decisión |
|---|---|---|
| IV con errores HAC | Independencia en contrastes anteriores | Diferir: calibración temporal adicional |
| Bien público dinámico | Financiación solo en equilibrio previsto | Diferir: requiere nuevo juego fiscal |
| Sesgo monetario y admisibilidad RE | Separar valor del objetivo de consistencia del régimen | **Elegida:** nuevo benchmark macro pequeño con identidad exacta |

La teoría es clásica; la contribución al repositorio es un control explícito de expectativas antes de comparar pérdidas, junto con oráculo numérico y falsación. No prioridad mundial. Hipótesis previa: residuos RE de los dos regímenes factibles ≤1e−12, identidad de pérdida, error de mejor respuesta ≤1e−6 y caso ingenuo aparentemente mejor pero inconsistente.

## 3. Literatura real

Kydland–Prescott (1977) plantea inconsistencia temporal; Barro–Gordon (1983, teoría positiva) analiza sesgo monetario en modelo de tasa natural. Su trabajo de reglas y reputación (1983) introduce mecanismos repetidos, no implementados aquí. Rogoff (1985) estudia delegación y compromiso, también distintos del supuesto simple usado. Walsh (1995) modela contratos para banqueros centrales; aquí no se implementan esos contratos.

Cinco referencias reales verificadas el 29 de octubre mediante Chicago, ScienceDirect, Oxford y página académica del autor en UCSC. DOI/URL y metadatos en `referencias.bib`. No se afirma lectura íntegra o revisión exhaustiva. No se atribuyen a este código reputación o instituciones de los artículos citados.

## 4. Brecha y alcance S2

El programa S1 de transmisión monetaria plantea anticipación estratégica y sistemas de Markov heterogéneos. Una búsqueda acotada no encontró esta auditoría específica de sesgo inflacionario en sus README/código/notebooks. Este componente aporta un benchmark lineal-cuadrático previo, sin implementar el programa completo ni su hipótesis de liquidez y heterogeneidad. S2 local, no promoción del dominio entero.

## 5. Modelo, secuencia y datos

Oferta: y=α(π−πe)+ε. Objetivo del banco: L=0,5[π²+λ(y−k)²], con k un objetivo por encima del producto natural. El privado fija πe antes de ε; el banco observa el shock y elige inflación. En discreción, el privado anticipa esa mejor respuesta. En compromiso se asume una regla contingente creíble sin coste, fijada antes de expectativas: no hay mecanismo institucional endógeno que la garantice.

α en {0,5;1;1,5}, λ en {0,5;1;2}, k en {0;0,5;1}, σ en {0;1}: 54 escenarios. ε toma ±σ con probabilidad 0,5; se calculan expectativas exactamente. σ=0 repite un mismo estado con peso 0,5, no dos observaciones independientes. Tres regímenes producen 324 registros. Datos sintéticos propios, sin clientes o fuentes externas; hashes, configuración, plataforma y versiones guardados. No tasas calibradas ni previsiones reales.

## 6. Derivación y oráculo

Mejor respuesta condicional: πBR=λα(απe+k−ε)/(1+λα²). Exigir πe=Eπ implica πe=λαk=b. Así, πD=b−λαε/(1+λα²). Bajo compromiso óptimo dentro de reglas afines, πC=−λαε/(1+λα²), con expectativa cero. Ambas generan y=ε/(1+λα²).

Por media cero del shock, ELD−ELC=0,5b². Esta identidad pertenece al modelo especificado; no prueba una ganancia empírica. La regla comprometida responde a shocks: no es inflación rígida cero. Compromiso impide reoptimizar después del shock, por lo que no debe pasar el test de mejor respuesta discrecional ex post.

Un optimizador escalar independiente minimiza la misma pérdida dada πe y ε y contrasta la mejor respuesta de discreción. No resuelve un juego repetido o credibilidad. La alternativa ingenua fija πe=0 y usa la mejor respuesta unilateral; cuando k>0, genera Eπ>0 y falla la restricción de expectativas racionales.

## 7. Tests, coste y ejecución

`bash run.sh` instala dependencias directas fijadas, corre tests con cobertura, ruff/mypy, grilla y notebook. Tests verifican ancla, identidad exacta en veinte economías reproducibles, oráculo condicional, control k=0 y contratos. Son propiedades parametrizadas, no una suite Hypothesis inexistente. Semilla solo para tests; no se presentan bandas Monte Carlo para expectativas exactas.

Resultado ejecutado: **4/4 tests pasan**, cobertura de sentencias ejecutables del núcleo **28/29 (97%)**, ruff sin hallazgos y mypy sin errores en tres archivos `src` (imports sin stubs ignorados). Suite común **8/8**, sin medir cobertura. Notebook: **seis celdas de código** ejecutadas con PNG persistido e inspeccionado legible; no se probó un frontend completo de Jupyter.

Tiempo y pico de asignaciones Python se miden para el experimento completo, incluidos oráculos escalares; no son RSS, coste por régimen o latencia operacional. CPU AMD EPYC 9V74 80-Core Processor, 9 procesadores lógicos visibles; tiempos sujetos a carga concurrente. No se estudia alta dimensión: modelo deliberadamente pequeño. No hay C/C++, por lo que ctest/sanitizers no aplican. Suite común económica ejecutada con registro, sin medir su cobertura.

Notebook ejecutado secuencialmente en IPython limpio en proceso, sin kernel/socket; captura outputs y aborta ante error. Validación nbformat e inspección de PNG no certifican todos los frontends.

## 8. Resultados reales

Ancla α=λ=k=σ=1:

| Régimen | Pérdida esperada | Residuo RE | Producto medio |
|---|---:|---:|---:|
| Compromiso |0,75|0|0|
| Discreción |1,25|0|0|
| Naive, inconsistente |0,50|0,50|0,50|

La diferencia factible es 0,50 unidades de pérdida, exactamente 0,5(λαk)². La aparente pérdida menor de naive no se cuenta como mejora factible, porque su expectativa supuesta cero contradice inflación media 0,5. En los 54 casos, error máximo de identidad de pérdida 4.44e-16; diferencia máxima de BR frente a oráculo 1.42e-08. Valores completos constan en CSV/JSON.

![Pérdidas y expectativas](results/comparison.png)

## 9. Falsaciones y control negativo

Naive demuestra por qué minimizar una función no certifica un equilibrio: obtiene una ganancia media de producto que solo existe bajo expectativas congeladas incorrectamente. Un agente racional anticipa la política y esa sorpresa sistemática desaparece. El componente no afirma que ningún shock monetario tenga efectos reales: los shocks y sorpresas siguen moviendo producto en el modelo.

Cuando k=0, compromiso y discreción coinciden y no hay ventaja estricta. Si no existe compromiso creíble o éste tiene costes, la comparación cambia. No se presenta compromiso como implementable automáticamente ni se atribuye dominancia de una regla rígida a esta auditoría.

## 10. Limitaciones y madurez

S2 del componente, no del programa entero ni equivalente automático a M2. Oferta lineal, objetivo cuadrático y parámetros conocidos; sin agentes heterogéneos, mercados de crédito, tipo de interés, tipo de cambio, reputación, aprendizaje o calibración real. Solo dos estados exactos con media cero. No recomendación para un banco central real ni causalidad observacional.

## 11. Cómo correr

Desde la carpeta: `bash run.sh`. Python 3.11+, venv y PyPI. Dependencias directas fijadas, no lock transitivo por hash. `PYTHON` permite seleccionar intérprete. Notebook en proceso sin kernel/socket, explícito en metadatos.

## 12. Referencias BibTeX

Cinco entradas en `referencias.bib`: Kydland–Prescott, dos Barro–Gordon, Rogoff y Walsh. DOI o URL primarios verificados; §3 distingue el benchmark de mecanismos no implementados. No se inventan citas ni resultados.

## 13. Rúbrica de autor, 1–5

| Novedad | Rigor | Reproducibilidad | Código | Claridad | Impacto | Honestidad | MVP |
|---:|---:|---:|---:|---:|---:|---:|---:|
|2|4|4|4|4|3|5|4|

Autoevaluación; la teoría clásica y ausencia de datos reales impiden máximos de novedad/impacto. El revisor independiente del ciclo reprodujo `bash run.sh` completo con salida cero, leyó la mejor respuesta y políticas del núcleo y no identificó bloqueantes. No equivale a validación empírica externa.

## 14. Siguiente iteración recomendada

1. `01-macroeconomics/01-strategic-monetary-transmission/inflation-bias-audit`: coste de compromiso e instituciones que hagan la regla compatible con incentivos.
2. `01-macroeconomics/01-strategic-monetary-transmission`: expectativas aprendidas frente a RE, conservando explícita la diferencia de régimen.
3. `01-macroeconomics/01-strategic-monetary-transmission`: identificar parámetros y heterogeneidad con datos aprobados, sin trasladar resultados sintéticos a política real.
