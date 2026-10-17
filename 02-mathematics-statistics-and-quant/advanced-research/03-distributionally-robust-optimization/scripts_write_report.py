"""Build the report from measured results, including both failed baseline experiments."""

from pathlib import Path
import csv
import json
import re

ROOT = Path(__file__).resolve().parent
csv.field_size_limit(10000000)
configuration = json.loads((ROOT / "config.json").read_text())
expected_final = (
    len(configuration["sizes"])
    * len(configuration["loss_families"])
    * len(configuration["seeds"])
    * len(configuration["radii"])
)
for relative, expected in [
    ("raw.csv", expected_final),
    ("initial_baseline/raw.csv", 54),
    ("two_start_baseline/replayed_raw.csv", 54),
]:
    with (ROOT / "benchmarks" / relative).open() as stream:
        records = list(csv.DictReader(stream))
    if len(records) != expected or any("n" not in row or None in row for row in records):
        raise RuntimeError(f"Incomplete or invalid benchmark CSV: {relative}")
r = json.loads((ROOT / "benchmarks/results.json").read_text())
initial = json.loads((ROOT / "benchmarks/initial_baseline/results.json").read_text())
second = json.loads((ROOT / "benchmarks/two_start_baseline/results.json").read_text())
coverage = json.loads((ROOT / "benchmarks/coverage.json").read_text())
match = re.search(r"(\d+) passed", (ROOT / "benchmarks/tests.txt").read_text())
if match is None:
    raise RuntimeError("Passing test evidence missing")
tests = match.group(1)
summary = "\n".join(
    f"| {s['n']} | {s['cases']} | {s['slsqp_accepted']} | {s['max_gap']:.6g} | {s['root_median_ms']:.4f} | {s['slsqp_median_ms']:.4f} | {s['root_peak_bytes']} | {s['slsqp_peak_bytes']} |"
    for s in r["summary"]
)
ex = r["decision"]
scenarios = "\n".join(
    f"| {s['scenario']} | {s['true_rare_probability']} | {s['kl_to_nominal']:.9g} | {s['nominal_action_loss']} | {s['approximate_action_loss']} | {s['robust_action_loss']} |"
    for s in ex["scenarios"]
)
text = f"""# Expectativa robusta KL: una aproximación no es una cota

Fecha: 2026-10-16. Programa 03: **S1 → S2**, primer prototipo acotado.
Base inspeccionada: `2193e5a82b96ce20c3210a5c2e23f1df033e5884`.

## 1. Pregunta
¿Cuándo la aproximación media-varianza subestima una expectativa robusta KL y puede cambiar una decisión minimax?

## 2. Estado del arte y originalidad
Búsqueda focalizada con fuentes primarias verificadas el 2026-10-16; no revisión sistemática exhaustiva:
- Hu y Hong, preprint publicado en Optimization Online en noviembre de 2012, Kullback-Leibler Divergence Constrained Distributionally Robust Optimization: dualidad y reformulaciones KL. URL: https://optimization-online.org/2012/11/3677/. No se confunde la fecha de publicación del registro con otras versiones posteriores.
- Ben-Tal et al. (2013), Management Science 59(2), 341–357, DOI 10.1287/mnsc.1120.1641: incertidumbre en probabilidades mediante phi-divergencias.
- Duchi y Namkoong (2019), JMLR 20(68), 1–55, https://www.jmlr.org/papers/v20/17-750.html: contexto de regularización por varianza y DRO; no se afirma que su método sea este kernel KL ni se transfieren sus garantías al MVP.
- Rahimian y Mehrotra (2019), arXiv:1908.05659, revisión de DRO; publicación posterior OJMO 3 (2022), artículo 4. Contexto sobre conjuntos de ambigüedad, no validación del radio aquí usado.
- Boyd y Vandenberghe (2004), Convex Optimization, https://web.stanford.edu/~boyd/cvxbook/: dualidad y optimización convexa.

La inclinación exponencial, la reformulación dual y la expansión de radio pequeño son conocidas. El aporte incremental es convertirlas en un kernel, diagnóstico y benchmark reproducibles del portafolio. No se reivindica un algoritmo nuevo ni una refutación inédita de la aproximación: se demuestra ejecutablemente su límite en estos casos.

## 3. Brecha y alcance reducido
El programa 03 solo tenía formulación S1, principalmente orientada a Wasserstein. numerical-core contiene KL de Bernoulli, pero no este supremo robusto ni el ejemplo de decisiones. Se revisaron los programas 08, 09 y 18 y aportes recientes para evitar duplicaciones. Este MVP adopta **KL(q||p) en soporte finito**, no Wasserstein; es un primer submodelo del programa, no cumplimiento de toda la agenda original. La calibración del radio bajo no estacionariedad sigue pendiente.

## 4. Hipótesis y umbrales previos
config.json precede al primer experimento: violación KL ≤1e-10, error de masa ≤1e-12, brecha primal-dual escalada ≤1e-9, acuerdo con SLSQP aceptado ≤1e-5, al menos 80% de referencias SLSQP aceptadas, error contra oráculo binario ≤1e-10 y subestimación del ejemplo raro ≥.001. Escala = max(1,rango de pérdidas). No se exige que la aproximación sea siempre inferior/superior ni se afirma calibración estadística.
Gate final: **{r["success"]}**. Chequeos reales: `{r["checks"]}`.
**Los umbrales no se relajaron.** Primera configuración SLSQP: gate {initial["success"]}, fracción aceptada {initial["checks"]["accepted_slsqp_fraction"]:.6g}, diferencia máxima {initial["checks"]["max_scaled_slsqp_difference"]:.6g}. Segunda: gate {second["success"]}, fracción {second["checks"]["accepted_slsqp_fraction"]:.6g}, diferencia {second["checks"]["max_scaled_slsqp_difference"]:.6g}. Ambas ejecuciones fallidas están preservadas con CSV/JSON/resumen.

## 5. Diseño experimental
Tamaños 3,16,64; seeds 20261016,20261017,20261018; familias bounded (Dirichlet(3), pérdidas uniformes [-1,1]) y rare_spike (probabilidad .001 para pérdida 1, otras pérdidas uniformes [0,.1]). Radios .001,.05,.5. **54 casos** sobre 18 datasets. Los tres radios reutilizan cada dataset, no son muestras independientes. Datos y pesos adversarios de ambos solvers se guardan en datasets.json/weights.json; parámetros exactos en config.json.
Baselines: media nominal, aproximación media+sqrt(2*rho*Var), y optimización primal SLSQP con restricciones explícitas. Un oráculo de Bernoulli busca directamente la probabilidad mediante brentq, sin usar la parametrización de inclinación; 18 comparaciones adicionales incluyendo radio cero y saturación. No es una referencia de precisión arbitraria: todos son float64 y las identidades analíticas sirven de invariantes.
Los tiempos miden cada método por separado; memoria en otra ejecución. El costo SLSQP incluye todas sus inicializaciones y refinamiento, no solo la última llamada. Se usan dos inicializaciones factibles y un reinicio desde la mejor solución para resetear la aproximación Hessiana; el reinicio no usa el kernel KL ni el oráculo. Se conservan mensajes/advertencias de cada intento en CSV. SLSQP se acepta solo si reporta éxito, masa a 1e-8, KL≤rho+1e-8 y no negatividad a 1e-10. Las tolerancias de aceptación del baseline son distintas del gate del kernel y se declaran.
El baseline refinado impone q_i≥1e-12*p_i para evitar singularidad del gradiente en cero; por tanto resuelve una aproximación interior del mismo primal. No se oculta esa diferencia. Dado cualquier q factible, mezclarlo con p con peso 1e-12 vuelve a cumplir ese suelo, no aumenta KL por convexidad y cambia la expectativa como máximo 1e-12*rango(loss). El error de restricción interior es despreciable frente al gate 1e-5, pero no es cero.
Entorno: `{r["environment"]}`. BLAS/OMP a un hilo. Peak tracemalloc no es RSS total ni garantiza todos los buffers nativos. Orden fijo, sin warm-up dedicado; tiempos exploratorios, no una garantía portátil de velocidad. La configuración del baseline se ajustó tras fallos sobre este mismo benchmark; no hay conjunto externo de validación de rendimiento.

## 6. Formulación y código real
W(p,l,rho)=sup qᵀl sujeto a q≥0, Σq=1, D_KL(q||p)=Σq log(q/p)≤rho, con p_i>0 y soporte finito conocido. El conjunto factible es compacto y contiene p, luego existe óptimo. La orientación KL es explícita; invertirla cambia el problema. radio=0 devuelve p; pérdidas constantes fijan el valor.
Sea M=max(l), s=M-min(l)>0, x=(l-M)/s y Z(t)=Σp exp(t*x). El candidato q_t=p exp(t*x)/Z(t) se calcula con logsumexp. Por no negatividad de KL(q||q_t), t E_q[x]≤D(q||p)+log Z(t), lo que da la cota dual U(t)=M+s*(rho+log Z(t))/t para t>0. Si D(q_t||p)=rho, el candidato iguala la cota en aritmética exacta. D'(t)=t Var_qt(x)≥0 permite bisección; el extremo inferior conserva factibilidad computada. El código centra x≤0 para evitar overflow exponencial y devuelve pesos, valor primal, dual y divergencia; no inventa una garantía cuando no puede resolver el tilt.
Con S=argmax(l), rho_crit=-log p(S). Para rho≥rho_crit, p condicionado a S alcanza M y es óptimo. Se gestionan máximos empatados. En rho pequeño, la expansión leading-order es E_p[l]+sqrt(2*rho*Var_p(l)); no es cota global y no incluye términos de orden superior. Las identidades y pruebas son sobre soporte finito; no se transfieren a pérdidas no acotadas o soporte desconocido.
`src/kl_robust.py` contiene el kernel; `src/reference.py`, primal genérico y oráculo; `src/benchmark.py`, generadores, comparación y decisiones. Las cotas son diagnósticos numéricos float64, no certificados con redondeo dirigido. El API restringe p_i≥1e-12, suma a distancia ≤1e-12 de 1 y normaliza explícitamente; |l_i|≤1e6; rho=0 o 1e-10≤rho≤100. Radios positivos menores se rechazan porque la resolución KL sería poco fiable. Un fallo de bracket/tilt o no finitud produce error explícito. Esos rangos no prometen precisión en toda combinación posible.

## 7. Pruebas y ejecución
**{tests} tests pasan**. Cobertura conjunta src.kl_robust/src.reference: **{coverage["totals"]["percent_covered"]:.2f}%**, {coverage["totals"]["covered_lines"]}/{coverage["totals"]["num_statements"]} líneas; no es cobertura de toda la aplicación. Guardas numéricas difíciles de alcanzar no se fuerzan solo para elevar cobertura. Incluye oracle binario, extremos, empates, invariancia afín positiva, monotonía con radio, KL con q=0, entrada inválida y variantes del baseline. Hypothesis determinista. Ruff y mypy se ejecutan con make run; no hay C/C++ nuevo, por lo que no aplican sanitizers.
Notebook ejecutado realmente con cuatro celdas y outputs de texto/figura mediante IPython en proceso. No se fabrican salidas y no se requiere kernel TCP para make run. Workflow CI repite el comando; el notebook es Python estándar para la regresión del repositorio.

## 8. Resultados medidos
| Estados | Casos | SLSQP aceptados | Máxima brecha escalada | Mediana tilt ms | Mediana SLSQP ms | Peak tilt bytes | Peak SLSQP bytes |
|---:|---:|---:|---:|---:|---:|---:|---:|
{summary}

### Caso raro y decisión
p(rare)=.001, pérdidas riesgosas (0,1), radio=.01, acción segura de pérdida constante .006.
- Media nominal riesgosa: **{ex["nominal_risky_loss"]:.12g}**.
- Aproximación media-varianza: **{ex["mean_variance_risky_loss"]:.12g}**.
- Peor caso KL: **{ex["exact_robust_risky_loss"]:.12g}**; cota dual **{ex["dual_upper"]:.12g}**; oráculo binario **{ex["binary_oracle"]:.12g}**.
- La aproximación elige acción {ex["approximate_action"]} (0=risky), mientras el minimax exacto elige {ex["robust_action"]} (1=safe). No es una recomendación financiera real.

| Escenario explícito | Probabilidad rara | KL al nominal | Pérdida decisión nominal | Pérdida decisión aproximada | Pérdida decisión robusta |
|---|---:|---:|---:|---:|---:|
{scenarios}

Ambos escenarios están dentro de la bola; el robusto paga más en el nominal y mejora en el desplazado. No se eligió un único escenario favorable ocultando el costo de conservadurismo. No hay test fuera de muestra aprendido: son distribuciones sintéticas especificadas.

![Auditoría](benchmarks/audit.png)

En los 54 casos, la aproximación subestima en {r["approximation_underestimates"]} y sobreestima en {r["approximation_overestimates"]} (umbral 1e-9). Hay {len(r["rejected_slsqp"])} referencias SLSQP rechazadas en la ejecución final; todas las filas se conservan. No se trata una señal de éxito del optimizador como prueba de optimalidad sin contrastar valor y factibilidad.

## 9. Análisis crítico y resultados negativos
Proveniencia: la primera captura conserva su CSV completo. De la segunda se conservaron JSON/resumen originales; su captura CSV fue truncada y no se entrega como válida. Se incluye replayed_raw.csv con una reejecución de los mismos casos y tiempos nuevos explícitamente identificados, además del script para repetirla. Ver benchmarks/two_start_baseline/PROVENANCE.md. El CSV crudo final está completo e independiente de esa captura histórica.
El primer SLSQP con un solo inicio y límites q≥0 fue insuficiente; el segundo con suelo interior y dos inicios mejoró factibilidad, pero aún terminó lejos del óptimo en un caso. Ambos fallaron el gate. Reiniciar desde su propia mejor solución con Hessiano nuevo y tolerancia más estricta mejora la comparación sin usar nuestro resultado para construir el baseline. Las variantes son reejecutables llamando slsqp_reference(...,variant='initial'/'two_start'/'refined') con los datasets y radios guardados. Las capturas históricas se preservan y pueden variar en tiempos entre máquinas.
La aproximación es mucho más barata y puede ser razonable para radios muy pequeños; no se demuestra que siempre subestime ni se la presenta como un baseline inútil. El primal genérico también puede ser más rápido en tamaños pequeños. La garantía minimax es condicional al conjunto: no calibra el radio, no valida p y no protege frente a escenarios ausentes del soporte. Se preserva el costo nominal de la robustez.

## 10. Límites
Solo KL finita, sin Wasserstein, MCMC, entrenamiento, escenarios nuevos ni datos externos. No se resuelve minimización continua sobre acciones: se enumeran dos acciones explícitas. La pregunta original sobre calibración bajo no estacionariedad permanece abierta. No se deducen provisiones, capital, límites ni recomendaciones de crédito/inversión de este ejemplo. No hay cobertura estadística del radio. Dependencias directas fijadas; no lock transitivo/Docker. EL=83 y los demás programas quedan intactos. Madurez S2 acotada, no S3/S4.

## 11. Reproducción
`make run` desde esta carpeta. Python 3.11+, make, internet para pip. Instala, chequea código/tests, ejecuta benchmarks, notebook e informe. Un gate fallido conserva evidencia y termina con error; no se modifica el umbral para ocultarlo. Datos y seeds son fijos; tiempos/timestamps varían.

## 12. BibTeX
Cinco entradas verificadas con DOI/arXiv/URL en referencias.bib. Métodos conocidos y límites explícitos; no afirmación de novedad mundial.

## 13. Rúbrica 1–5
| Criterio | Valor | Motivo |
|---|---:|---|
| Novedad incremental | 2 | Auditoría nueva del repo; teoría conocida |
| Rigor | 4 | Dualidad, factibilidad, oracle y baseline; float64 |
| Reproducibilidad | 4 | Un comando, seeds/pesos/versiones; sin lock completo |
| Código | 4 | Modular/tipado y property tests; Python solamente |
| Claridad | 4 | Distingue aproximación, cota y radio asumido |
| Impacto | 3 | Kernel reusable, sin validación económica externa |
| Honestidad | 5 | Dos experimentos fallidos y conservadurismo preservados |
| MVP completo | 5 | Código y artefactos ejecutados, no promesa de producción |

## Checklist
- [x] src/ ejecutable
- [x] Comando único documentado
- [x] Tests pasando y cobertura medida
- [x] Baselines con números y fallos preservados
- [x] CSV/JSON/pesos/figura guardados
- [x] README.md, informe.md, referencias.bib, MVP.md
- [x] Notebook realmente ejecutado
- [x] Subcarpeta correcta y programa 03 S2 acotado

Siguiente iteración recomendada: estudiar calibración y soporte antes de aplicaciones financieras.
1. advanced-research: calibrar radios con un diseño separado de entrenamiento/validación y medir cobertura sin prometerla de antemano.
2. advanced-research: comparar KL con una bola Wasserstein en soporte ampliado, manteniendo distintos sus supuestos.
3. quantitative-methods: incorporar un stress test de soporte omitido y medir el costo nominal de decisiones robustas.
"""
(ROOT / "informe.md").write_text(text)
print("Report generated from actual measurements, including failed experiments.")
