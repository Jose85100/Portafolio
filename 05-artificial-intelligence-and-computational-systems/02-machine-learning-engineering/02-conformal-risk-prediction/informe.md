# Auditor conformal de masa test — ciclo 2026-10-23

## 1. Título
Intervalos ponderados que reconocen cuándo la evidencia sólo permite un conjunto infinito.

## 2. Hipótesis y novedad incremental
Hipótesis fijada en config.json: con n=80 y mezcla destino 80% frente a fuente 10%, método correcto logra cobertura marginal >=88% y mejora >=10 puntos porcentuales sobre split conformal sin ponderar. Es una auditoría incremental del portafolio; no se reivindica nuevo algoritmo. La propuesta anterior era sólo S0/S1. Esta implementación verifica explícitamente masa test, fracción de intervalos finitos y fallo bajo cambio condicional.

## 3. Estado del arte
Tibshirani et al. (2019, arXiv:1904.06019) fundamenta ponderación por razón de densidades bajo covariate shift. Lei et al. (2016, arXiv:1604.04173) desarrolla split conformal y cobertura marginal. Angelopoulos y Bates (2021, arXiv:2107.07511) presenta el marco general de cuantificación de incertidumbre. Barber et al. (2022, arXiv:2202.13415) estudia desviaciones de intercambiabilidad; no convierte ratios incorrectos en garantía exacta. Gibbs y Candès (2021, arXiv:2106.00170) trata adaptación online, diferente del presente experimento independiente. Metadatos abiertos y verificados en páginas primarias arXiv el 23-10-2026; no revisión exhaustiva. BibTeX y registro de verificación incluidos.

## 4. Brecha
El repositorio tenía una especificación conformal sin implementación y otros controles conformes de routing, pero no una auditoría de intervalos ponderados donde la masa test produce infinito. No duplica el detector KYC/Mondrian del dominio riesgo: aquí se evalúa regresión y cambio de mezcla con pesos oráculo.

## 5. Diseño/configuración
Predictor fijo cero, por lo que no se requiere entrenamiento y no existe fuga de calibración al ajuste. Fuente X~Bernoulli(.1), destino X~Bernoulli(.8); Y|X normal centrada, desviación 1 o 4. Ratios exactos .8/.1 y .2/.9. 100 repeticiones independientes por n=40/80/320, 2.000 puntos test por repetición. Semilla base 20261023; métodos pareados. Escenarios no_shift, covariate_shift, conditional_shift (ruido test duplicado). Cada cambio usa las mismas variables latentes para contrastes pareados. No representa dependencia temporal ni datos operativos. Config guarda parámetros, fuentes sintéticas e hipótesis; summary.json registra CPU, Python, NumPy, plataforma y recursos.

## 6. Implementación real
src/conformal.py ordena scores y acumula pesos O(n log n), consulta umbral por binary search O(m log n). Cuantil de calibración con masa test w(x)/(sum(w)+w(x)) en +infinito. Si el objetivo excede la masa finita devuelve infinito, sin recortarlo. Baseline unweighted incluye corrección finita; naive_weighted omite masa test como ablación explícita. Rechaza NaN, pesos no positivos, vacío y ratios de rango dinámico que underflowean. Pruebas de reescala hasta 1e100 no certifican precisión arbitraria. src/experiment.py conserva réplicas y resúmenes.

## 7. Tests y benchmarks ejecutados
9 pruebas unittest: rango finito exacto, infinito, ablación, 100 permutaciones/reescalas aleatorias, 100 monotonías alpha, monotonía masa test, inválidos, ratios y empates. Comando `python -m unittest discover -s tests -v`. Ruff en src/tests/benchmarks y mypy en núcleo pasan. Cobertura de líneas no medida; no se afirma porcentaje. Benchmark 2.700 filas CSV y 27 resúmenes JSON; tiempo aproximado 0,9 s, memoria Python pico aproximada 2 MB, RSS de proceso aproximado 55 MB (mediciones exactas actualizadas en JSON). Tiempo engloba todas las políticas, no benchmark individual de latencia; tamaños 40/80/320 son sensibilidad y escalabilidad estadística, no prueba de carga operacional. C++/sanitizers no aplican.

## 8. Resultados
Promedios sobre 100 calibraciones, test marginal de 2.000 puntos cada una:

| n | Escenario | Método | Cobertura | Fracción finita | Ancho medio finito |
|---|---|---|---:|---:|---:|
| 80 | Covariate shift | Sin ponderar | 0,516160 | 1 | 4,29196 |
| 80 | Covariate shift | Ponderado ingenuo | 0,862670 | 1 | 12,03072 |
| 80 | Covariate shift | Ponderado correcto | 0,947170 | 0,736745 | 13,80797 |
| 320 | Covariate shift | Ponderado correcto | 0,905065 | 1 | 12,65217 |
| 80 | Conditional shift | Ponderado correcto | 0,796190 | 0,736745 | 13,80797 |

Hipótesis sintética satisfecha: mejora 43,101 puntos porcentuales sobre baseline. n80 ESS medio12,55; n320 ESS49,52. Figura results/coverage.png muestra medias ±1,96 errores estándar entre calibraciones, no intervalos simultáneos ni garantía individual. Ancho medio finito excluye infinitos; si hay cualquier infinito el ancho medio total es infinito. n40 cobertura correcta99,6055% se logra con sólo20,631% de intervalos finitos, ilustrando utilidad débil. No_shift n80 cobertura89,99%; las fluctuaciones Monte Carlo alrededor90% no invalidan ni prueban el teorema.

## 9. Análisis crítico y ablaciones negativas
Omitir masa test conserva finitud pero infracubre. Corregirla mejora cobertura a costa de abstención práctica (intervalo infinito). El cambio condicional refuta que ponderación por X resuelva cambios arbitrarios de Y|X: n320 cae a66,034% pese a pesos correctos. El baseline sin ponderar en no_shift tiene cobertura marginal cercana90% pero cobertura del grupo de ruido alto cercana40%; marginal no implica condicional. No se ajustaron parámetros tras observar resultados para rescatar hipótesis.

## 10. Limitaciones y riesgos
Pesos oráculo y media verdadera conocida simplifican mucho el problema. No hay datos abiertos externos ni estimación empírica; la propuesta original de series temporales abiertas permanece pendiente. Ninguna validación operacional, de seguridad, privacidad o rendimiento de modelos fundacionales. Datos totalmente sintéticos sin información personal. Desplegar intervalos infinitos como decisiones automáticas sería incorrecto: requieren derivación o adquisición de evidencia. El programa no alcanza S3/S4 ni estado validado/operacional. Componente S2; matriz M2 local candidato sujeto a revisión independiente.

El entorno bloquea sockets del kernel Jupyter: nbclient intentado y falló con Operation not permitted / kernel died. Se ejecutaron las cuatro celdas de código en orden con IPython in-process, capturando outputs reales y validando nbformat. No se afirma validación mediante kernel aislado. Este ejecutor es portable para este notebook sin magias; no sustituye nbclient para notebooks arbitrarios.

## 11. Cómo correr
`bash run.sh` desde la carpeta del proyecto instala requisitos fijados, prueba, simula y ejecuta notebook. Entorno preinstalado: `PYTHON="$CODEX_PRIMARY_RUNTIME_PYTHON" SKIP_INSTALL=1 bash run.sh`. Python3.12. Si la instalación no tiene red, usar dependencias ya preparadas. No se requiere clave/API/red para cálculos.

## 12. Referencias BibTeX
Cinco entradas reales en referencias.bib; identificadores 1904.06019, 2202.13415, 2107.07511, 2106.00170 y1604.04173. Se conservan años originales de preprint (no se confunden con año editorial).

## 13. Rúbrica 1–5
Novedad2 (adaptación auditada), rigor4 (supuestos y falsificación explícitos), reproducibilidad4 (semillas/código/outputs, kernel aislado pendiente), código4 (núcleo probado/tipado), claridad4, impacto3 (muestra fallo concreto, sin datos reales), honestidad5, MVP4 (ejecución in-process, evaluación empírica pendiente). Autoevaluación, no certificación externa.

## 14. Siguiente iteración
Siguiente iteración recomendada: estimar pesos y evaluar utilidad cuando la razón de densidades deja de ser oráculo.

1. 02-machine-learning-engineering/02-conformal-risk-prediction: estimar ratios con muestra no etiquetada separada y contrastar contra oráculo.
2. 02-machine-learning-engineering/02-conformal-risk-prediction: añadir datos abiertos con licencia y cortes temporales sin asumir independencia falsamente.
3. 08-ai-reliability-security-and-governance: definir contrato de derivación humana y monitorizar fracción de intervalos infinitos y anchura total.
