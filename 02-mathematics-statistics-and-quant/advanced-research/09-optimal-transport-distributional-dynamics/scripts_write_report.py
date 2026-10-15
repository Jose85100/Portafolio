"""Render a critical report from actual benchmark and test evidence."""

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent
r = json.loads((ROOT / "benchmarks/results.json").read_text())
coverage = json.loads((ROOT / "benchmarks/coverage.json").read_text())
match = re.search(r"(\d+) passed", (ROOT / "benchmarks/tests.txt").read_text())
if match is None:
    raise RuntimeError("Passing test evidence missing")
tests = match.group(1)
selected = "\n".join(
    f"| {s['scenario']} | {s['method']} | {s['reference']:.9g} | {s['upper']:.9g} | {s['relative_cost_error']:.6g} | {s['raw_residual']:.5g} | {s['converged']} | {1000 * s['seconds']:.3f} | {s['traced_peak_bytes']} |"
    if not s["failed"]
    else f"| {s['scenario']} | {s['method']} | {s['reference']:.9g} | FALLÓ | N/A | N/A | False | {1000 * s['seconds']:.3f} | {s['traced_peak_bytes']} |"
    for s in r["selected"]
)
summary = "\n".join(
    f"| {s['method']} | {s['total']} | {s['failed']} | {s['nonconverged']} | {s['max_raw_residual']:.6g} | {s['max_rounded_residual']:.6g} |"
    for s in r["summary"]
)
ad = r["adversarial"]
text = f"""# Transporte óptimo: factibilidad antes de interpretar el costo

Fecha: 2026-10-15. Programa 09: **S1 → S2**, prototipo acotado.
Base revisada: `a8199a6864c63d25bd322537f60cc184e8c43bc7`.

## 1. Pregunta
¿Cómo evitar interpretar como mejora un costo Sinkhorn bajo que viola los marginales, y separar factibilidad, estabilidad y sesgo entrópico?

## 2. Prior art y originalidad
Referencias primarias verificadas el 2026-10-15, búsqueda focalizada, no revisión sistemática exhaustiva:
- Cuturi (2013), arXiv:1306.0895: regularización entrópica y escalado Sinkhorn.
- Peyré y Cuturi (2019), Computational Optimal Transport, DOI 10.1561/2200000073, arXiv:1803.00567: formulación, dualidad, cómputo y limitaciones.
- Altschuler, Weed y Rigollet (2017), arXiv:1705.09634: aproximación y reparación al politopo de transporte. La reparación contracción+residuo rango uno es un método conocido; implementación propia de ese procedimiento, no contribución algorítmica nueva.
- Schmitzer (2019), DOI 10.1137/16M1106018, arXiv:1610.06519: estabilización logarítmica y limitaciones para epsilon pequeño. Aquí solo se implementa dominio logarítmico con recentrado, no todo el algoritmo sparse/multiescala/epsilon-scaling del artículo.
- Feydy et al. (2019), PMLR 89, 2681–2690, https://proceedings.mlr.press/v89/feydy19a.html: divergencias Sinkhorn des-sesgadas. Se cita para distinguirlas del costo transportado por un plan regularizado; NO se implementan estas divergencias.

La novedad incremental es un módulo y auditoría nuevos en el portafolio: costo, factibilidad, cotas numéricas, referencia independiente y fallos guardados. No se reclama un nuevo método de OT ni que el problema de subdesbordamiento sea desconocido.

## 3. Brecha
El programa 09 solo contenía README/protocolo S1. numerical-core tiene W1 empírico para muestras equiponderadas de igual tamaño, no este W2² ponderado ni LP/Sinkhorn. Se revisaron los programas 08 y 18, ya integrados; no se modifican ni se repite su experimento. Se cierra la brecha entre una fórmula de transporte y un prototipo que exige marginales válidos antes de interpretar el costo. No se identifica movilidad individual o causalidad con datos marginales.

## 4. Hipótesis y umbrales previos
`config.json` se escribió antes del primer benchmark. Para todos los casos logarítmicos: resultados finitos, residuo L1 combinado después de reparación ≤1e-10 y cotas que contienen el LP dentro de 1e-8*max(1,|LP|). LP y referencia monótona 1D deben concordar a 1e-8 en la misma escala. En soportes separados, epsilon=.005, error relativo de costo reparado ≤.001; el directo debe fallar explícitamente en esos casos. Un contraejemplo debe detectar costo falso bajo con residuo >.1. No se exige ni afirma convergencia de todos los iterados dentro del presupuesto.
Gate: **{r["success"]}**. Chequeos reales: `{r["checks"]}`. No se modificaron umbrales después de observar resultados. La hipótesis es sobre estos casos sintéticos, no una garantía universal ni una reivindicación de mayor velocidad.

## 5. Diseño y configuración
Problema finito balanceado: min <C,P> sujeto a P≥0, P1=a, Pᵀ1=b. C_ij=(x_i-y_j)²; el óptimo no regularizado es W2², no W2.
Tamaños n=8,32,64; epsilon=1,.05,.005; presupuesto 1.000 iteraciones, chequeo de convergencia cada 10 y al final, tolerancia L1 1e-9. Overlap: dos seeds independientes 20261015/20261016, soportes normales y pesos Dirichlet(3). Separated: malla [0,1] trasladada 20 unidades, pesos uniformes. Mass_mismatch: misma malla y masas concentradas en extremos opuestos; ambos totales siguen siendo 1. Los dos últimos son deterministas y se ejecutan una vez por tamaño, no se duplican como supuestas réplicas.
Hay **{r["dataset_count"]} datasets**, {r["raw_rows"]} corridas temporizadas Sinkhorn, más 12 LP y referencias monótonas; cada corrida Sinkhorn se repite por separado para memoria. Se conservan todos los soportes/pesos en datasets.json, semillas y resultados en CSV; dos casos especiales guardan el contraejemplo y el sesgo propio. Mismo problema y epsilon para directo/log; LP es un baseline competitivo no regularizado, no se degrada su tolerancia para favorecer Sinkhorn. Referencia LP HiGHS con tolerancias primal/dual 1e-9; no es un oracle racional exacto. El acoplamiento monótono es un algoritmo independiente 1D, también float64.
Entorno real: `{r["environment"]}`. Make fija BLAS/OMP a un hilo. Tiempos por instancia con orden fijo, sin warm-up dedicado; solo dos réplicas aleatorias, insuficientes para conclusiones de microbenchmark generales. Memoria = peak de asignaciones rastreadas por tracemalloc en otra ejecución, no RSS completo ni garantía de capturar todos los buffers externos. Complejidad del kernel denso por iteración O(nm), memoria O(nm); el LP usa restricciones dispersas.

## 6. Matemática e implementación
El politopo de transporte no está vacío: abᵀ es factible para a,b probabilidades; es cerrado y acotado, por lo que un costo finito alcanza mínimo. Con masas positivas tras retirar soportes de peso cero, la regularización min <C,P>+epsilon ΣP(log P-1) tiene solución positiva y escalable en aritmética exacta. No se infiere convergencia numérica a partir de esa existencia.
`src/transport.py` implementa dos métodos para el mismo problema regularizado: escalados sobre K=exp(-C/epsilon) y actualizaciones f_i=epsilon[log a_i-logsumexp((g_j-C_ij)/epsilon)] y análogas para g. El recentrado f←f-aᵀf, g←g+aᵀf preserva f+g y el plan. El directo registra división por cero/overflow, no devuelve NaNs como éxito.
La reparación contrae filas para no exceder a, luego columnas para no exceder b. En aritmética exacta, residuos r=a-P1 y s=b-Pᵀ1 son no negativos y tienen la misma masa t. Si t>0, añadir rsᵀ/t corrige ambos marginales; si t=0, ya es factible. En float64 se evita división por cero y se verifica el residuo posterior. Reparar **no** demuestra optimalidad ni conserva el óptimo entrópico.
Dual no regularizado: maximizar aᵀf+bᵀg sujeto a f_i+g_j≤C_ij. Restar a g la máxima violación positiva genera un candidato dual factible en aritmética exacta. Por dualidad débil, L≤W2²≤U para el costo U de un plan factible. Las comprobaciones aquí son **cotas numéricas con tolerancias**, no certificación formal con redondeo dirigido. Soportes de peso cero se retiran y se reinsertan con filas/columnas nulas. Se aceptan masas con suma a distancia ≤1e-12 de 1 y se normalizan explícitamente; se rechazan otras masas y costos no finitos/negativos o >1e6.
La referencia 1D usa el acoplamiento monótono ponderado, válido para costo cuadrático en la recta. No se extrapola a costo arbitrario ni dimensión mayor; el LP sí acepta costos finitos no negativos genéricos en el kernel limitado.

## 7. Tests y ejecución
**{tests} tests pasan**. Cobertura conjunta de src.transport y src.reference: **{coverage["totals"]["percent_covered"]:.2f}%**, {coverage["totals"]["covered_lines"]}/{coverage["totals"]["num_statements"]} líneas. La rama de fallo del optimizador LP no se fuerza artificialmente; no se afirma cobertura 100% de toda la aplicación. Tests incluyen Hypothesis determinista, no negatividad/marginales/idempotencia de reparación, fórmulas exactas de dos puntos, LP vs cuantiles, cotas, soporte cero, masa en un átomo, invariancia ante offset de costo y entradas inválidas. El caso de sesgo propio verifica 1/(1+exp(1)) contra el kernel.
Ruff y mypy se ejecutan en make run. Sin código C/C++ nuevo, no aplican sanitizers. Notebook ejecutado realmente mediante IPython en proceso, cuatro celdas con outputs de texto/figura; no requiere kernel TCP para el comando local. CI añade reproducción completa y el notebook sigue siendo Python estándar para la regresión del repo.

## 8. Resultados
### Contraejemplo de una iteración
a=(.9,.1), b=(.1,.9), C=[[0,1],[1,0]], epsilon=.01. Óptimo exacto analítico y LP **{ad["reference"]}**.
- Costo del iterado sin factibilidad: **{ad["raw_cost"]:.9g}**.
- Residuo L1 combinado: **{ad["raw_residual"]:.9g}**.
- Costo después de reparación: **{ad["rounded_cost"]:.17g}**.
- Residuo después de reparación: **{ad["rounded_residual"]:.9g}**.
- Convergió el iterado: **{ad["converged"]}**. Reparar recupera el óptimo en este ejemplo especial, no en general. Planes y masas están guardados en adversarial_plans.npz y JSON.

### Resumen completo
| Método | Corridas | Fallos explícitos | No convergió sin fallo numérico | Máximo residuo crudo | Máximo residuo reparado |
|---|---:|---:|---:|---:|---:|
{summary}

### n=64, epsilon=.005, primera seed
| Escenario | Método | LP W2² | Costo reparado | Error relativo | Residuo crudo | Convergió | ms | Peak bytes |
|---|---|---:|---:|---:|---:|---|---:|---:|
{selected}

![Auditoría](benchmarks/audit.png)

Sesgo propio: para masas (.5,.5) sobre puntos (0,1), W2²(μ,μ)=0, pero el costo transportado regularizado con epsilon=1 es **{r["self_bias"]["regularized_transport_cost"]:.12g}**. No debe llamarse distancia Wasserstein exacta ni confundirse con una Sinkhorn divergence des-sesgada.

## 9. Análisis crítico y fallos
La estabilidad logarítmica evita los seis fallos observados del directo, pero no implica convergencia rápida: se conserva el caso logarítmico que agotó el presupuesto. Su plan reparado es factible, no se etiqueta como óptimo regularizado convergido. En los casos benignos directo/log dan prácticamente los mismos costos y el directo suele ser más barato: no se oculta ese resultado negativo para la estabilización.
El error regularizado/reparado puede ser material frente al LP, aun con residuo pequeño; se reportan gap y error en raw.csv. Estabilidad, factibilidad y exactitud son tres criterios distintos. El LP puede resultar preferible para tamaños pequeños; la referencia monótona es particularmente eficiente en 1D y evita un solver genérico. Se conserva la separación entre error de regularización y error de parada: sin solución regularizada independiente no se cuantifica exactamente cuánto aporta cada uno al costo observado.

## 10. Límites
Solo soportes sintéticos 1D hasta 64 puntos por medida; no validación de dinámica, JKO, causalidad, geodésicas, movilidad individual ni datos financieros. Balanced OT: no se permite creación/destrucción de masa. Sin epsilon-scaling, GPU, multiescala, autodiferenciación, sparse kernels o Sinkhorn divergences. Los límites de epsilon/costo de la API no constituyen garantía de convergencia o precisión en toda combinación admitida. Las cotas float64 se verifican contra referencias en estos casos, no son pruebas con aritmética de intervalos. Dependencias directas fijadas, sin lock transitivo ni Docker; instrucciones de entorno en README. EL=83 no cambia: quant-libraries queda intacto. Madurez S2 acotada, no S3/S4.

## 11. Cómo correr
Desde esta carpeta: `make run`. Python 3.11+, make, internet para pip. Instala dependencias, ejecuta lint/tipos/tests, genera CSV/JSON/NPZ/PNG, notebook e informe. Un gate fallido conserva evidencia y termina con error. Los tiempos y timestamp de cobertura varían al reproducir; datasets y seeds son fijos.

## 12. Referencias BibTeX
Cinco entradas verificadas con DOI/arXiv/URL en referencias.bib. La bibliografía identifica los métodos conocidos; la búsqueda focalizada no demuestra ausencia de prior art.

## 13. Rúbrica 1–5
| Criterio | Valor | Motivo |
|---|---:|---|
| Novedad incremental | 2 | Auditoría nueva en el repo; métodos establecidos |
| Rigor | 4 | Referencias independientes, fórmulas y cotas; no certificación formal |
| Reproducibilidad | 4 | Un comando, datos guardados, seeds y versiones; sin lock completo |
| Código | 4 | Modular/tipado, invariantes; solo Python |
| Claridad | 4 | Separa costo, factibilidad y error |
| Impacto | 3 | Kernel reutilizable, sin evidencia económica externa |
| Honestidad | 5 | Fallos y no convergencia visibles |
| MVP completo | 5 | Ejecución y artefactos, no promesa de producción |

## Checklist
- [x] src/ real y ejecutable
- [x] Un comando documentado
- [x] Tests pasando, cobertura medida
- [x] Baselines comparados con números
- [x] CSV/JSON/NPZ/figura guardados
- [x] README.md, informe.md, referencias.bib, MVP.md
- [x] Notebook con salidas ejecutadas
- [x] Programa 09 en subcarpeta correcta, S2 acotado

Siguiente iteración recomendada: mejorar el control de precisión antes de ampliar aplicaciones.
1. advanced-research: epsilon-scaling con presupuesto y criterio primal-dual explícitos, conservando casos no convergidos.
2. advanced-research: extender a soportes 2D y contrastar contra LP, sin usar el oracle monótono fuera de la recta.
3. quantitative-methods: benchmark de divergencia Sinkhorn des-sesgada con pruebas de autocomparación y límites de interpretación.
"""
(ROOT / "informe.md").write_text(text)
print("Report generated from retained measurements and tests.")
