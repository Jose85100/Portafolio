"""Write the critical report using actual retained results, never hard-coded metrics."""

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent
report = json.loads((ROOT / "benchmarks/results.json").read_text())
coverage = json.loads((ROOT / "benchmarks/coverage.json").read_text())
evidence = (ROOT / "benchmarks/tests.txt").read_text()
tests = re.search(r"(\d+) passed", evidence).group(1)
precision_table = "\n".join(
    f"| {r['d']} | {r['method']} | {r['median_mean_relative_error']:.6g} | {r['max_covariance_relative_error']:.6g} | {r['failed']} | {1000 * r['median_seconds']:.4f} | {r['traced_peak_bytes']} |"
    if r["successful"]
    else f"| {r['d']} | {r['method']} | N/A | N/A | {r['failed']} | {1000 * r['median_seconds']:.4f} | {r['traced_peak_bytes']} |"
    for r in report["selected"]
)
cal_table = "\n".join(
    f"| {r['scenario']} | {r['direction']} | {100 * r['coverage_95']:.1f}% | [{100 * r['coverage_wilson_low']:.2f}%, {100 * r['coverage_wilson_high']:.2f}%] | {r['posterior_sd']:.6g} |"
    for r in report["calibration"]
)
checks = "; ".join(
    f"d={r['d']}: improvement={r['improvement_vs_normal']}, passed={r['passed']}"
    for r in report["checks"]
)
text = f"""# Posterior lineal gaussiano: estabilidad numérica no es calibración

Fecha: 2026-10-14. Programa 08: **S1 → S2**, prototipo acotado.
Base inspeccionada: `e19d56d7f36ea1e521a814aa495ac49e3d1847eb`.

## 1. Pregunta
¿Cómo distinguir inestabilidad numérica de incertidumbre mal especificada en un problema inverso lineal?

## 2. Estado del arte y prior art
Se verificaron referencias y páginas primarias el 2026-10-14, mediante búsqueda focalizada, no revisión sistemática exhaustiva.
- Stuart (2010), Acta Numerica 19, 451–559, DOI 10.1017/S0962492910000061: marco bayesiano de problemas inversos.
- Hansen (1998), Rank-Deficient and Discrete Ill-Posed Problems, DOI 10.1137/1.9780898719697: regularización y análisis espectral. Página del autor: https://www.imm.dtu.dk/~pcha/Book/mm04.html.
- Björck (1996), Numerical Methods for Least Squares Problems, DOI 10.1137/1.9781611971484: métodos numéricos de mínimos cuadrados. Metadatos verificados en SIAM; no se afirma lectura completa del libro.
- Rasmussen y Williams (2006), Gaussian Processes for Machine Learning, https://gaussianprocess.org/gpml/: regresión bayesiana gaussiana; aquí solo se implementa el caso lineal finito, no un motor GP.
- Anderson et al. (1999), LAPACK Users' Guide, edición 3, https://www.netlib.org/lapack/lug/: QR/SVD y métodos de solución.
- Documentación SciPy lstsq: https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lstsq.html; gelsy es el baseline aumentado con factorización ortogonal completa.

SVD, QR y posterior gaussiano son métodos establecidos. La contribución incremental es el kernel y benchmark del portafolio que separa error de cómputo, supuesto de ruido y supuesto de prior, con referencia independiente, réplicas y outputs verificables. No se afirma un algoritmo nuevo, originalidad teórica, ni mejora universal frente a QR.

## 3. Brecha cerrada
El programa 08 solo tenía diseño S1; el proyecto histórico de ridge/lasso no implementaba este posterior ni auditaba su covarianza y calibración contra alta precisión. Se revisaron numerical-core, métodos cuantitativos y el aporte anterior del programa 18, ya fusionado. Se añadió un prototipo independiente sin modificar esos trabajos. La brecha es convertir la formulación inversa en código que diagnostique tanto pérdida de precisión como confianza injustificada por supuestos equivocados.

## 4. Hipótesis falsable y umbrales previos
En cond(A)=1e10 y sigma=1e-8, para d=4,12,32, SVD debe presentar error relativo máximo de media y covarianza ≤1e-5 frente a referencia de 80 dígitos, y mejora mediana ≥100 veces frente a ecuaciones normales (o fallo total explícito de ese baseline). Además SVD y QR deben concordar a ≤1e-5 en tres probes deterministas. `config.json` se escribió antes de ejecutar. No se afinó para acomodar resultados.
Resultado del gate: **{report["success"]}**. {checks}. Diferencia máxima SVD/QR en probes: **{report["max_svd_qr_difference"]:.9g}**.
La cobertura no se usa para ajustar el método ni como gate de superioridad; se reportan proporciones y Wilson 95% con 1.000 réplicas independientes por escenario/dirección.

## 5. Diseño experimental y configuración
y=A theta+eta, theta~N(0,I), eta~N(0,sigma² I). Operadores cuadrados con bases ortogonales aleatorias y singular values geométricos, cond(A)=1e2,1e6,1e10; d=4,12,32; sigma=1e-3/1e-8. Veinte realizaciones de theta/ruido por operador: 18 escenarios, 360 datasets y 1.080 solves de método. El mismo A/y se usa para los tres comparadores. Operador fijo por escenario; no son 20 realizaciones independientes de A. La referencia evalúa las entradas float64 reales, no factores ideales previos al redondeo.
Los seeds del operador y de theta/ruido se derivan de 20261014; los seeds por dataset están en raw.csv. PCG64 vía default_rng. El script conserva fallos, sin imputar error cero ni ocultarlos. Tiempo por solve incluye media y covarianza; la referencia se excluye porque no es un algoritmo de producción comparable. QR calcula la media con gelsy y la covarianza mediante otro QR pivotado; esta implementación hace trabajo redundante, por lo que no se afirma superioridad de tiempo universal. Memoria: una corrida separada con tracemalloc, no RSS total ni todos los buffers nativos.
Calibración: d=6, cond(A)=1e5, verdadero sigma=.001/tau=1; 1.000 draws conjuntos independientes con el mismo operador. Se evalúa el mismo dataset bajo supuestos correctos, sigma diez veces menor y prior diez veces más estrecho. Se estudian dos direcciones singulares, fuerte y débil, no todas las coordenadas. Comparación pareada, descriptiva; no implica pruebas de causalidad.
Hardware/entorno: {report["environment"]}. Make limita OPENBLAS_NUM_THREADS y OMP_NUM_THREADS a 1; tiempos son locales, no una garantía portátil. No hay datos financieros externos.

## 6. Formalización y código
Espacio paramétrico R^d, observaciones R^m, m≥d; prior propio N(0,tau² I), ruido independiente N(0,sigma² I), A conocido. Para sigma,tau>0:
H=AᵀA/sigma²+I/tau² es definida positiva porque vᵀHv=||Av||²/sigma²+||v||²/tau²>0 para v≠0. Por completar cuadrados, C=H⁻¹ y m=C Aᵀy/sigma². Existe un posterior normal propio incluso si A es singular. Esto no implica identificabilidad de la likelihood.
Si A=U diag(s) Vᵀ, los autovalores posteriores son c_j=sigma²/(s_j²+sigma²/tau²), y la media es V diag(s_j/(s_j²+sigma²/tau²)) Uᵀy. Por tanto 0<c_j≤tau²; en s_j=0, c_j=tau²: el dato no informa esa dirección. El código usa hypot y filtros espectrales, evitando formar AᵀA para SVD. La demostración algebraica no depende de un test; los tests solo verifican instancias numéricas.
El baseline QR resuelve [A; (sigma/tau) I] theta≈[y;0]. La covarianza se obtiene de R⁻¹R⁻ᵀ y se revierte la permutación; no se aplica un prior diferente para favorecer SVD. El baseline de ecuaciones normales forma la misma regularización en float64; su pérdida de precisión es una práctica conocida, no un hallazgo inédito. La matriz aumentada es de rango completo teórico gracias al prior; el normal-equations matrix puede perderlo por redondeo. Los tiempos son exploratorios: orden fijo de métodos y sin protocolo de warm-up dedicado, por lo que no se extraen conclusiones universales de velocidad.
Referencia: mpmath workdps(80), inversión y multiplicación para las mismas entradas binarias. Luego se convierte a float64 para comparar normas. No es una cota de error formal certificada ni se supone válida para escalas arbitrarias; el régimen ensayado queda documentado.

## 7. Pruebas y controles
**{tests} tests pasan**. Cobertura de líneas de src.posterior: **{coverage["totals"]["percent_covered"]:.1f}%**, {coverage["totals"]["covered_lines"]}/{coverage["totals"]["num_statements"]} líneas. No es cobertura completa de benchmark, oracle o runners.
Pruebas: fórmula diagonal independiente para los tres métodos; comparación con oracle en matriz alta; dirección nula; validación de entradas, sigma/tau y método desconocido; equivarianza ante rotación; property-based de cota prior y monotonicidad con ruido. Evidencia en tests.txt y coverage.json. Ruff/mypy se ejecutan en make run. No hay C/C++ nuevo, por eso no se aplican sanitizers.
Notebook ejecutado realmente con IPython en proceso; guarda salidas de texto, figura y prueba de la dirección nula. No se fabrican outputs ni se necesita kernel TCP para make run. La regresión externa del repo puede reejecutarlo con python3.

## 8. Resultados duros: cond(A)=1e10, sigma=1e-8
Errores relativos en norma Euclídea de media y Frobenius de covarianza frente al oracle; mediana sobre 20 datasets, máximo de covarianza sobre esos datasets.

| d | Método | Error mediano media | Error máximo covarianza | Fallos | Mediana ms | Peak bytes rastreados |
|---:|---|---:|---:|---:|---:|---:|
{precision_table}

### Calibración separada
Cobertura del intervalo posterior nominal 95%; intervalos Wilson para la proporción empírica, no para theta.

| Supuesto | Dirección | Cobertura | Wilson 95% | SD posterior |
|---|---|---:|---|---:|
{cal_table}

![Auditoría](benchmarks/audit.png)

Salidas: raw.csv (1.080 solves), summary.csv (54 grupos), calibration_raw.csv (6.000 evaluaciones de intervalos), calibration_summary.csv (6 grupos), results.json y audit.png. Los seis grupos de calibración reutilizan los mismos 1.000 datasets; no son 6.000 datasets independientes. Tests y notebook acompañan la evidencia.

## 9. Análisis crítico y experimentos negativos
Separar error numérico de error estadístico es esencial: métodos estables no corrigen sigma ni tau mal especificados. Un prior estrecho puede concentrar la dirección débil aunque el operador apenas la observe. Ese resultado refleja mala especificación respecto al generador; no invalida el teorema de Bayes bajo su modelo.
QR es el comparador fuerte, no se oculta si iguala o supera SVD; se reportan sus errores y costos. Ecuaciones normales pueden ser precisas en casos benignos y son más baratas en algunos escenarios. El benchmark conserva todos los regímenes. Los gates prueban únicamente los casos definidos, no toda la familia de problemas inversos.
Una dirección muy observada puede tener varianza tan pequeña que reconstruir la covarianza completa pierde PSD aparente a nivel de roundoff. Se conserva el mínimo autovalor numérico en raw.csv; no se recorta la matriz para esconderlo. Para uso extremo conviene trabajar con factores o varianzas espectrales, no inferir precisión ilimitada de una matriz densa.

## 10. Límites y alcance reducido
Gaussianidad e isotropía, prior cero y A conocido. Kernel admite A cuadrado/alto pero el benchmark de estabilidad usa solo matrices cuadradas; tests incluyen un caso alto. No MCMC, Laplace no lineal, VI, correlación, heterocedasticidad, aprendizaje de sigma/tau, sparse solvers o aplicación a datos económicos. No se modela ni estima la discrepancia del operador: se cubren solamente mala especificación del ruido/prior y redondeo computacional.
Cobertura evaluada bajo el prior-predictivo, no frecuentista uniforme con theta fijo. Un conjunto fijo de operadores y veinte datasets por escenario no establecen robustez general. Dependencias directas fijadas, sin lock transitivo ni Docker; instrucciones de entorno en README. El contrato EL=83 permanece intacto, porque no se modifica quant-libraries. Madurez S2, no S3/S4.

## 11. Un comando
Desde esta carpeta: `make run`. Python 3.11+, make e internet para pip. Crea el entorno, ejecuta checks, pruebas, benchmarks, notebook y este informe. Un gate fallido conserva resultados y devuelve exit code no cero; no se declara éxito ocultando el fallo. Tiempos y fechas de cobertura varían al reejecutar.

## 12. BibTeX
Seis entradas reales con DOI/URL en referencias.bib. Métodos y limitaciones son trazables; búsqueda focalizada, no reivindicación exhaustiva de novedad.

## 13. Rúbrica 1–5
| Criterio | Valor | Motivo |
|---|---:|---|
| Novedad incremental | 2 | Kernel/auditoría nuevos en el repo; métodos conocidos |
| Rigor | 4 | Fórmulas, oracle, réplicas, supuestos; sin garantías generales |
| Reproducibilidad | 4 | Un comando, seeds y versiones directas; sin lock completo |
| Código | 4 | Modular, tipos y tests; solo Python |
| Claridad | 4 | Separa precisión y calibración |
| Impacto | 3 | Fundamento reusable; aún sintético |
| Honestidad | 5 | Baseline fuerte, fallos y límites visibles |
| MVP completo | 5 | Artefactos y ejecución, sin reclamar producción |

## Checklist
- [x] Código real en src/
- [x] Comando único documentado
- [x] Tests pasando y cobertura medida
- [x] Baselines comparados con números
- [x] CSV/JSON/figura verificables
- [x] README.md, informe.md, referencias.bib, MVP.md
- [x] Notebook ejecutado con outputs
- [x] Subcarpeta correcta; alcance del programa 08 S2

Siguiente iteración recomendada: ampliar el diagnóstico sin confundir concentración con identificación.
1. advanced-research: ruido correlacionado y prior no isotrópico mediante whitening y pruebas de invariancia.
2. advanced-research: operador mal especificado con discrepancia explícita, sin atribuir todos los errores a sigma.
3. quantitative-methods: benchmark de factores de covarianza y QR sin factorizaciones duplicadas, a presupuesto de tiempo equivalente.
"""
(ROOT / "informe.md").write_text(text)
print("Report regenerated from actual results and test evidence.")
