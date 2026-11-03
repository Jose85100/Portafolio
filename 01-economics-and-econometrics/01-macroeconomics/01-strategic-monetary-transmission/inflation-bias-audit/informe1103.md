# Informe de incremento — varianza de shocks AR(1)

Fecha de corrida: 2026-11-03. Línea acumulativa: auditoría de expectativas y varianza en un modelo de inconsistencia temporal; se amplía el componente `inflation-bias-audit` y no se crea un programa aparte.

## 1. Título y pregunta

**¿Cómo estimar e intervalar la varianza marginal del shock de una pérdida monetaria cuando los shocks son persistentes?** El artefacto ofrece un estimador por diferencias de primer orden, una cota de Chebyshev bajo gaussianidad conjunta y un baseline GLS exacto con el parámetro AR(1) conocido.

## 2. Hipótesis, aporte y novedad incremental

H1, fijada antes de leer los outputs: en las ocho celdas \((n,\rho)\), el límite inferior de Wilson 95% para cobertura del intervalo GLS debe ser ≥0.80, con 90 réplicas por celda. H1 **falla en dos celdas**. Es una regla de cribado Monte Carlo, no un test del teorema de GLS. La hipótesis analítica de cobertura GLS sigue condicionada a Gaussianidad y \(\rho\) conocido. El aporte defendible de este incremento es ingeniería/auditoría: se implementa la covarianza de cuadrados de incrementos solapados y se la compara justamente con GLS. No es novedad científica original.

Se conserva un registro histórico de trabajo del 3-nov previo que mencionaba 79/90, 77/90 y 78/90 para otra corrida/versión de configuración y tres celdas. Sus ficheros y SHA no sobrevivieron al entorno; por tanto, **esos conteos no se presentan como reproducidos ni se mezclan** con esta corrida recuperada. Esta tabla procede sólo de los seeds/config publicados aquí.

## 3. Estado del arte y matriz de prior art

La matriz de ocho fuentes con problema, supuesto, método y diferencia está en `prior-art1103.md`; referencias BibTeX en `referencias.bib`. Las fuentes directamente relevantes incluyen Prais–Winsten (transformación GLS), Penn State STAT 510 (autocovarianza AR(1)), Isserlis (momento gaussiano de cuadrados) y Cochran (formas cuadráticas normales). Kydland–Prescott y Barro–Gordon contextualizan la pérdida monetaria previa, no sustentan la parte inferencial. Cobertura suficiente para el modelo gaussiano AR(1) con \(\rho\) dado; insuficiente para \(\rho\) estimado, shocks pesados, ruptura, HAC/bootstrap y evidencia macro.

## 4. Brecha y candidatas consideradas

La ruta anterior estimaba shocks iid y usaba un pivote \(\chi^2\) iid. Bajo AR(1), el intervalo iid falla cobertura porque ignora la estructura serial. Se contrastaron: (a) pares temporales y Chebyshev, seleccionado como extensión de bajo costo y con abstención; (b) GLS conocido-\(\rho\), retenido como baseline exacto, más eficiente y principal para evaluar; (c) HAC/bootstrap o estimar \(\rho\), diferido hasta especificar incertidumbre del primer paso y un diseño de longitud de bloque. Este incremento complementa la investigación persistente, no afirma que la corrección de una fórmula sea nueva por sí misma.

## 5. Diseño y configuración

Modelo: \(X_t=\mu+U_t\), \(U_t=\rho U_{t-1}+\eta_t\), \(|\rho|<1\), \(\eta_t\sim N(0,v(1-\rho^2))\). Datos sintéticos, \(v=1\), media desconocida, observaciones estacionarias, \(n\in\{64,256\}\), \(\rho\in\{0,.5,.9,.95\}\), confianza 90%, seeds raíz `[1103,1104,1105]`, 30 trayectorias por seed/celda (90/celda). Config: `dependent-config.json`; Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8, Linux x86_64, CPU EPYC visible según registro de entorno. Sin dataset licenciado ni hardware acelerador.

## 6. Fórmula original y propuesta

El módulo anterior aplica \((n-1)s^2/v\sim\chi^2_{n-1}\), válido bajo iid normal, y el modelo monetario optimiza la misma pérdida social cuadrática. Para el proceso AR(1), \(D_t=X_t-X_{t-1}\) tiene varianza \(2v(1-\rho)\). La propuesta \(Z_t=D_t^2/[2(1-\rho)]\) mantiene \(E Z_t=v\). Isserlis implica \(\operatorname{Cov}(D_t^2,D_{t+h}^2)=2\operatorname{Cov}(D_t,D_{t+h})^2\), con \(\operatorname{Cov}(D_t,D_{t+h})=-v(1-\rho)^2\rho^{h-1}\). Por ello \(\operatorname{Var}(\hat v_P)=c_{m,\rho}v^2\), donde

\[
c_{m,\rho}=\frac{2m+(1-\rho)^2\sum_{h=1}^{m-1}(m-h)\rho^{2(h-1)}}{m^2},\quad m=n-1.
\]

Chebyshev relativo, con \(\epsilon=\sqrt{c/\alpha}<1\), da intervalo \([\hat v_P/(1+\epsilon),\hat v_P/(1-\epsilon)]\). Si \(\epsilon\ge1\), el límite superior no es finito y el código abstiene. El competidor GLS blanquea el AR(1), estima la media desconocida y usa \(RSS/v\sim\chi^2_{n-1}\). Conserva exactitud bajo supuestos más restrictivos y requiere \(\rho\) conocido; el estimador de pares es menos informativo pero explícito ante persistencia. Derivación completa en `derivacion1103.md` y notebook.

## 7. Implementación y artefactos

Código modular/tipado: `src/dependent_interval.py`, `src/run_dependent_interval.py`. Pruebas: `tests/test_dependent_interval.py`. Configuración congelada, BibTeX/matriz de prior art, informe de limitaciones, script de notebook ejecutable y notebook con celdas narrativas/LaTeX y outputs. Instrucciones y dependencias existentes se conservan; `run.sh` integra el nuevo módulo y notebook al flujo acumulativo. Las métricas de cobertura se simulan; no se genera inferencia causal.

## 8. Tests, baselines y mediciones reales

Los ocho tests nuevos pasaron en ejecución local, incluyendo comparación del blanqueo GLS contra la forma densa \(R^{-1}\), aproximación de insesgamiento del estimador por pares, dominio estacionario y casos de datos inválidos. Hay medición Monte Carlo de cobertura Wilson por celda y medición micro de tiempo/pico Python (30 repeticiones, n=256, rho=.9); no son benchmark de latencia operacional.

**Baseline justo:** los tres intervalos usan exactamente las mismas 720 trayectorias simuladas y observan la misma secuencia; GLS es el principal porque es exacto bajo el mismo DGP y competitivo estadísticamente. El iid se muestra como ablación mal especificada. Paired-Chebyshev no se declara superior por su cobertura: su amplitud media es casi 3 veces GLS.

| Método | Cobertura media entre 8 celdas | MAE medio de \(\hat v\) | Ancho medio del intervalo | Menor límite Wilson 95% |
|---|---:|---:|---:|---:|
| iid chi-cuadrado (ablación) | 0.5667 | 0.2388 | 0.3916 | 0.0864 |
| Pares + Chebyshev | 0.9972 | 0.1162 | 1.3458 | 0.9397 |
| GLS chi-cuadrado exacto | 0.9097 | 0.1072 | 0.4585 | 0.7813 |

La cobertura nominal 0.90 GLS queda dentro del rango global observado, pero H1 de umbral por celda falla:

| n | rho | GLS cubiertos/90 | Cobertura | Wilson 95% |
|---:|---:|---:|---:|---:|
| 64 | 0.0 | 79/90 | 0.8778 | [0.7943, 0.9304] **H1 falla** |
| 64 | 0.5 | 81/90 | 0.9000 | [0.8208, 0.9465] |
| 64 | 0.9 | 84/90 | 0.9333 | [0.8621, 0.9691] |
| 64 | 0.95 | 83/90 | 0.9222 | [0.8481, 0.9618] |
| 256 | 0.0 | 81/90 | 0.9000 | [0.8208, 0.9465] |
| 256 | 0.5 | 85/90 | 0.9444 | [0.8765, 0.9760] |
| 256 | 0.9 | 78/90 | 0.8667 | [0.7813, 0.9221] **H1 falla** |
| 256 | 0.95 | 84/90 | 0.9333 | [0.8621, 0.9691] |

El GLS es el baseline principal aunque dos Wilson lower bounds no alcancen 0.80: el umbral es una regla de evidencia de Monte Carlo finita y conservadora, no premisa de exactitud; el pivote es exacto condicional al DGP. Las celdas fallidas no se borran, y el resultado no refuta el método teórico. El paired interval cubre mucho más pero con ancho medio 1.3458 frente a 0.4585 GLS, costo de la garantía conservadora.

Tiempo/espacio instrumentados por llamada, n=256/rho=.9 (30 repeticiones, muestra ya cargada): mediana paired 0.000222 s y 5,216 bytes Python; mediana GLS 0.000691 s y 21,930 bytes Python. Estos valores dependen de entorno y tracemalloc, no son coste de producción. Sensibilidad de \(c_{m,\rho}\) y radio Chebyshev para cinco tamaños y 75 valores de \(\rho\) se guarda en CSV/figura; no se declaran propiedades fuera de |rho|<1.

## 9. Figuras y resultado positivo/negativo

`results/dependent-interval.png` presenta (i) cobertura con bandas Wilson95 y umbrales nominal90%/cribado80%, (ii) radio relativo Chebyshev y frontera de abstención. Outputs crudos: `dependent-samples.csv`, `dependent-interval.csv`, `dependent-aggregate.csv`, `dependent-runtime.csv`, `dependent-sensitivity.csv`, `dependent-summary.json`. Positivo: la fórmula por pares corrige sesgo en esperanza y el error Monte Carlo agregado queda cerca de \(v=1\); el baseline iid pierde cobertura severa con alta persistencia. Negativo: H1 Wilson/GLS falla en dos celdas y el intervalo Chebyshev es ancho; ninguna de estas simulaciones valida uso en datos reales.

## 10. Análisis crítico, fallos y ablations

La ablación iid llega a cobertura 0.1444–0.4000 cuando \(\rho=.9,.95\), evidencia del costo de ignorar dependencia en este DGP sintético. Los intervalos por pares son conservadores, no dominan GLS en ancho o error. H1 no pasa; se conserva sin selección de seed posterior. La reparametrización original/propuesta cambia la varianza que alimenta la pérdida, no la fórmula de política. Las condiciones de existencia son |rho|<1, varianza finita, normalidad conjunta, estacionariedad, \(\rho\) conocido y muestra de longitud ≥3. Ruptura de varianza, datos t, \(\rho\) estimado y dos regímenes de credibilidad quedan fuera.

## 11. Limitaciones y sesgos

Solo simulación diseñada con \(v=1\), promedio conocido por DGP, semillas fijas y menú pequeño. El estimador GLS asume conocimiento externo perfecto de \(\rho\), no típico de aplicación. Estimación del parámetro, preselección de régimen, datos faltantes, shocks no gaussianos y errores de identificación pueden invalidar resultados. Las frecuencias de cobertura tienen sólo 90 ensayos por celda; Wilson es incertidumbre Monte Carlo puntual sin ajuste simultáneo para ocho celdas. Hardware especificado; sin medición de RSS/proceso, escalabilidad operativa o costo de datos.

## 12. Comando reproducible

Desde `inflation-bias-audit/`: `bash run.sh` crea `.venv`, instala los pins de `requirements.txt`, ejecuta tests/cobertura/lint/tipos, genera simulaciones/figuras/notebooks y falla si un comando falla. Ejecución focal del nuevo incremento: `python3 -m src.run_dependent_interval`; los tests focales: `python3 -m unittest tests/test_dependent_interval.py -v`.

## 13. Referencias BibTeX

Ver `referencias.bib`; ocho fuentes en matriz `prior-art1103.md`, incluyendo Kydland–Prescott, Barro–Gordon, Prais–Winsten, Penn State, Isserlis, Cochran, NIST y Wilson. URLs/DOI comprobados el 2026-11-03; el estado y cobertura de cada fuente se explican en la matriz. No se afirma cobertura exhaustiva de literatura de series temporales.

## 14. Madurez y rúbricas

**Madurez:** implementación local S2 (prototipo reproducible); programa general conserva S1/S2 local según el estándar económico, sin elevar a S3/S4. Revisión científica independiente de esta recuperación e integración global aún pendientes hasta reproducirlas; el componente no debe marcarse como revisado antes de ese dictamen.

Rúbrica original 1–5: novedad incremental **2**; rigor **3**; reproducibilidad **4** (pendiente verificación independiente); código **4**; claridad **4**; impacto potencial **2**; honestidad **5**; cierre MVP **4**. Rúbrica ampliada: profundidad teórica **3**; aporte defendible **2** (adaptación/auditoría); calidad experimental **3** (DGP controlado, H1 fallida y buen baseline, aún pocas réplicas); utilidad **3**; reproducibilidad **4** local/independiente pendiente; honestidad **5**.

**Qué sabemos:** bajo AR(1) gaussiano conocido-\(\rho\), los incrementos requieren corrección \(1-\rho\) y tienen cuadrados serialmente correlacionados. **Qué construimos:** módulo typed con intervalo Chebyshev y GLS chi-cuadrado, tests y experimento comparativo con outputs. **Qué podemos hacer ahora:** medir el costo de una alternativa que tolera persistencia bajo supuestos explícitos y ver cuándo la cobertura extra de Chebyshev no compensa su ancho; aún no aplicarla como inferencia macro real.

### Siguiente iteración

1. Extender `inflation-bias-audit/src/dependent_interval.py` a \(\rho\) estimado, con garantía o abstención calibrada fuera de muestra.
2. Añadir un baseline HAC/bootstrap en `inflation-bias-audit/benchmarks/` con supuestos, selección de bloque y seeds confirmatorios.
3. Preparar contrato de datos/vintage/licencia/identificación macro en `inflation-bias-audit/data-contract1101.md` antes de cualquier estimación empírica.
