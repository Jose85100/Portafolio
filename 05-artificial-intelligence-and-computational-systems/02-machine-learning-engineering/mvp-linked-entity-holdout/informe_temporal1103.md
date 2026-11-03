# Informe de investigación: historial de reemplazos en holdout de identidades

Estado: rama de dominio local candidata a PR; revisión independiente y PR remoto pendientes. Programa acumulativo `mvp-linked-entity-holdout`, no carpeta nueva. El incremento del 2 nov cerró gates de semántica y cutoff; este incremento prueba la siguiente precondición, versionado de reemplazos completos.

## Catorce puntos de revisión

1. **Título:** Selección temporal de revisiones completas para auditoría de holdout por identidad.
2. **Hipótesis/novedad incremental:** H1: latest-known-at-cutoff y luego validez debe coincidir con oracle independiente en todas las consultas diseñadas y exponer el caso de resurrección filter-first. Adaptación de ingeniería acumulativa; no claim de novedad científica.
3. **Estado del arte:** bitemporalidad separa cuándo un dato es válido y cuándo se registra; leakage temporal debe controlarse en evaluación. La matriz y BibTeX contienen seis fuentes primarias/estándares verificadas y la diferencia del proyecto. La revisión no es sistemática exhaustiva.
4. **Brecha:** el snapshot gate de 2nov validaba dos timestamps de una sola revisión, no selección entre historial reemplazante; un filtro de vigencia antes del cutoff podía reciclar un registro histórico.
5. **Diseño/configuración:** `config_temporal1103.json`: datos deterministas sintéticos; 36 histories×10 availability cutoffs×3 identity instants=1,080 consultas, seis policies, un generador declarado seed1103 (grilla determinista; no aleatoriedad), Python3.12+, hardware y versión en `environment.json`/`versions.txt`.
6. **Implementación:** `src/temporal_revisions.py` provee selección, normalización timezone-aware UTC, intervalos semiabiertos, tie-break abstention y error en entradas ambiguas; `src/revision_experiment.py` da oracle simple, policies y mediciones reproducibles. API local; sin modificar shared/risk contracts. Complejidad por consulta O(m) escaneo de m revisiones por identidad; coste/almacenamiento no optimizado.
7. **Tests y benchmarks:** `bash run_temporal_revisions.sh` ejecuta 57 tests acumulados (47 regresión +10 nuevos), Ruff y mypy estricto en módulos nuevos, 1,080 consultas comparadas con oracle. Hay casos límite de intervalos, timezone, empates, duplicados, ausencias, revisión no disponible y permutación de empates antiguos ya superados. Sin benchmark production/escala.
8. **Resultados, tabla y figura:** valores exactos están en `results/temporal1103/summary.json`, cada política en `raw.csv.gz` (CSV crudo comprimido), contraejemplo en `counterexample.json`, sensibilidad agregada en `admissions.png`, mediciones de tiempo/memoria en `cost.json`. H1 software: regla seleccionada concuerda con oracle 1,080/1,080 y cero falsas admisiones; filter-first registra falsas admisiones en el régimen sintético. Es diseño, no frecuencia empírica. `notebook_temporal1103.ipynb` ejecutado conserva tabla/conteos y figura.
9. **Análisis crítico:** el contraste evidencia que bajo reemplazo completo una nueva revisión ya disponible puede retirar la supuesta validez abierta de una revisión anterior. La política base abstain-all evita falsas admisiones por construcción pero rechaza los casos válidos; disponibilidad-sola también confunde ser conocido con ser vigente. Revisar semántica del productor antes de usar.
10. **Límites/sesgos:** 36 fixtures diseñadas, dependencias sintéticas, una regla de negocio asumida, no casos empíricos, entidad adjudicada no validada. Timestamps no autenticados; hash/tie error no prueban honestidad. `latest` no representa histories con deltas, distintas autoridades, múltiples afirmaciones paralelas o reglas retroactivas alternativas. La comparación no demuestra reducción de leakage final, AUC, ni causalidad.
11. **Comando:** `bash run_temporal_revisions.sh` desde `05-artificial-intelligence-and-computational-systems/02-machine-learning-engineering/mvp-linked-entity-holdout/`.
12. **Referencias BibTeX:** `referencias.bib`, keys clifford_isakowitz_1992, jensen_snodgrass_1996, torp_jensen_snodgrass_2000, sklearn_timeseries_split_2026, sklearn_leakage_pitfalls_2026, kapoor_narayanan_2023_temporal. Matriz en `prior_art_temporal1103.md`.
13. **Rúbrica original (1–5):** novedad 2 (adaptación, no método nuevo); rigor 4 (derivación consistente dentro del contrato asumido); reproducibilidad 4 (un comando, deps fijadas y logs; requiere pip al instalar desde cero); código 4 (módulo tipado y errores explícitos); claridad 4 (contrato, ablation y límites documentados); impacto 3 (útil si el productor confirma full replacement); honestidad 5 (sintéticos etiquetados, ninguna afirmación empírica); completitud MVP 4 (código, test, benchmark, notebook, figura, docs y deps ejecutados; fuente real e integración operacional pendientes).
14. **Siguiente iteración:** contrato con owner de fuente y fixture real anonimizada, medir cutoffs bajo correcciones tardías/concurrentes y decidir si history es replacement o event/delta; no escalar until semantics approved.

## Rúbrica ampliada de investigación (1–5)

- Profundidad teórica: **3** — distingue availability/transaction time de interval-valid y deriva el selector; no formaliza todos los casos bitemporales ni prueba teorema general.
- Aporte defendible: **3** — contraejemplo reproducible y adaptación de ingeniería acotada; diferencia incremental al repo identificable, pero no hay claim de originalidad disciplinar.
- Calidad experimental: **4** — 1,080 consultas, seis políticas, oráculo separado, ablation adversarial y sensibilidad de cutoff; la grilla sintética determinista no permite inferencia externa.
- Utilidad: **3** — puede bloquear una clase concreta de resurrección temporal si el dueño de datos confirma semántica full replacement; sin esa confirmación no debe entrar como gate productivo.
- Reproducibilidad: **4** — comando, config, deps, CSV/JSON, versionado y outputs en notebook; requiere entorno Python y acceso inicial a pip.
- Honestidad: **5** — declara que sus etiquetas vienen del DGP, separa regla asumida de evidencia, registra negative/control baselines y acota fuente, reloj y madurez.

## Cartera acumulativa, fórmulas y decisiones

Ideas consideradas: (a) selección latest-known→interval valid (seleccionada por cerrar gap local y posibilitar refutación), (b) ledger de intervalos no superpuestos (más general pero requeriría contrato/base nueva), (c) firma de fuente (no hay PKI/signer en arquitectura actual). Decisiones descartadas: no revivir revisiones viejas si la revisión latest está fuera del intervalo; ties de latest son error; no tratar timestamps como autenticados.

La ecuación, unidades temporal UTC y propiedades de validez se exponen en `derivacion_temporal1103.md` y notebook. Se preserva latest available cutoff; adaptación solo compone con interval validity para datos full-replacement. Propiedades: decisión determinista si timestamps sin empates, invariancia al expresar el mismo instante con offset diferente, corte future information. Se niega validez si `valid_until<=effective_at`.

## Madurez y aporte defendible

Local: implementación, ejecución del benchmark diseñado y tests. El revisor independiente y chequeo remoto/CI todavía deben reproducir/Auditar; no incluido en este informe como estado revisado. No publicado hasta que exista PR remoto; no merge. La contribución defendible es contraejemplo ingenieril documentado que la cartera puede reutilizar para exigir semantics version-specific; datos de producción y relevancia cuantitativa siguen pendientes.
