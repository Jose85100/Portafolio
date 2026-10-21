# Information Geometry & Statistical Manifolds

> **Madurez: S2 acotado — detección de drift continuo por proyección gaussiana, calibración y auditoría categórica.** No se afirma detector financiero validado. Se conserva el protocolo original como agenda.

## Corrección de alineación — 2026-10-21

**Hilo principal: detección de cambios en variables continuas.** Se ajustan proyecciones gaussianas y se compara su distancia Fisher–Rao con KS y Wasserstein-1, usando referencia fija, calibración separada y evaluación independiente.

- API real: `src.drift.calibrate(reference, baseline_windows, alpha=.05, delta=.05)` y `Detector.predict(current)`.
- Diseño: `experiments/drift.json`; dos tamaños, 399 ventanas de calibración y 3.000 de evaluación; media, escala, mezcla con iguales momentos y control AR1.
- Calibración: estadístico de orden con cota binomial de tolerancia; Bonferroni sobre la incertidumbre de los tres umbrales. No controla una alarma conjunta ni un horizonte secuencial.
- Evidencia principal: `informe.md`, `drift_notebook.ipynb`, `benchmarks/drift-*.csv`, `benchmarks/drift.png` y `data/drift-examples.npz`.
- Se conservan resultados desfavorables: falsa alarma del piloto marginal, pérdida de cambios de forma y fallo de calibración IID bajo AR1. Las tasas finales y sus intervalos deben leerse, no sustituirse por el objetivo nominal del 5%.
- La auditoría categórica anterior queda como anexo reproducible: `docs/categorical-audit.md` y `notebook.ipynb`.

**Reproducción:** `make run` sigue instalando y ejecutando ambos estudios, tests, cobertura y los dos notebooks. El comando desde la raíz se conserva abajo. La garantía de tolerancia exige ventanas limpias de igual ley que las futuras; aquí se evalúan datos sintéticos. No se afirma detector financiero validado ni superioridad universal.

## Anexo categórico ejecutable — 2026-10-20

¿Fisher–Rao detecta cambios distintos de Hellinger usando las mismas permutaciones? En el simplex categórico ambas distancias son transformaciones estrictamente monótonas, así que sus tests tienen el mismo orden de rechazo. El MVP comprueba esa identidad, implementa geodésicas y contrasta contra Pearson permutado y asintótico. No es un algoritmo nuevo ni evidencia de superioridad universal.

### Instalar y reproducir

Entorno reproducible: **Python 3.12**, make, venv y acceso a PyPI. Desde esta carpeta:

```bash
make run
```

Desde la raíz de la rama que contenga el MVP:

```bash
make -C 02-mathematics-statistics-and-quant/advanced-research/02-information-geometry-statistical-manifolds run
```

Crea .venv, instala versiones directas fijadas, ejecuta Ruff/formato/mypy y pytest/Hypothesis con cobertura, las pruebas existentes de numerical-core, benchmark, informe, notebook y checklist. Para seleccionar intérprete: `make run PYTHON=python3.12`. Dependencias transitivas no bloqueadas: se registran en benchmarks/environment.txt. No requiere servicios ni datos privados durante los experimentos. La reproducción reescribe salidas generadas del MVP; tiempos y metadatos pueden cambiar.

### Artefactos y semántica

- src/geometry.py: Fisher–Rao estable por cuerda, Hellinger, cuadrático local y geodésicas.
- src/testing.py: particiones uniformes condicionadas a los conteos combinados, tres tests permutados y Pearson asintótico.
- src/reference.py: oráculo mpmath de 80 dígitos mediante ángulo y afinidad.
- config.json: 16 escenarios, semillas, 100 réplicas por escenario, 199 particiones y siete umbrales anteriores al experimento.
- benchmarks/: 1.600 datasets guardados en NPZ, 6.400 p-valores en CSV, 64 tasas con Wilson 95%, 75 tiempos, 12 verificaciones de alta precisión, 132 puntos geodésicos, figura y logs.
- notebook.ipynb: seis celdas ejecutadas con outputs; código gráfico editable en src/benchmark.py.
- informe.md, MVP.md, referencias.bib, fuentes.md: prueba elemental, límites y cinco fuentes primarias verificadas.

Métrica por UNA observación categórica: d_FR está entre 0 y pi. No confundir con el modelo multinomial escalado por tamaño n. Ceros soportados por extensión continua a la frontera; la aproximación tangente requiere base positiva. Los ceros empíricos no son prueba de imposibilidad poblacional. Sin pseudoconteos implícitos.

### Calidad y límites

El presupuesto de 199 particiones implica resolución .005 del p-valor; se usa corrección +1 para evitar cero. IID e intercambiabilidad bajo el nulo son indispensables. No hay detección online, dependencia temporal, binning aprendido, datos financieros ni comparación universal de potencia. Verificar monotonía no equivale a aceptar igualdad de distribuciones porque un test no rechace.

El notebook se ejecuta realmente con IPython en proceso (sin sockets locales). `.venv/bin/python scripts_notebook.py --kernel` permite nbclient convencional; el workflow Notebook Reliability también lo ejecuta con kernel separado. Figura inspeccionada por separado; revisión visual integral del notebook en visor no reclamada. Para completarla abrirlo en Jupyter o exportar a HTML mediante nbconvert. Las guías de notebooks y visualización orientan la estructura de evidencia, supuestos y límites.

## Protocolo S1 original — agenda fuera del MVP


## Pregunta de investigación

¿La geometría Fisher–Rao identifica cambios de distribución invisibles para pruebas convencionales?

## Hipótesis contrastable

El método propuesto supera a baselines explícitos en al menos una métrica predefinida, sin degradación inaceptable en robustez, calibración ni costo. Esta hipótesis debe operacionalizarse antes de observar resultados.

## Formulación matemática

g_ij(θ)=E_θ[∂_i log p(X|θ) ∂_j log p(X|θ)]; estudiar geodésicas, curvatura y singularidades.

**Trabajo teórico pendiente:** definir espacios de probabilidad y parámetros, supuestos de existencia e identificabilidad, resultados de convergencia o estabilidad, demostraciones y contraejemplos. No se presume que tales propiedades estén establecidas.

## Modelado estadístico y estimación

Contrastar distancia geodésica, KL, Jensen–Shannon, Wasserstein, KS y PSI.

Estimar sesgo, varianza, consistencia bajo supuestos adecuados e intervalos de incertidumbre. Separar evaluación predictiva de identificación causal.

## Métodos numéricos y protocolo experimental

Gaussianas, mezclas, colas pesadas, parámetros casi no identificables; bootstrap dependiente, potencia y tasa de falsas alarmas.

**Diseño mínimo:** (1) generador sintético con verdad conocida; (2) baseline trivial y avanzado; (3) evaluación fuera de muestra o por réplicas independientes; (4) ablaciones y pruebas adversariales; (5) tiempos, memoria y sensibilidad a hiperparámetros; (6) semillas, versiones y resultados reproducibles.

## Aplicación económico-financiera

Drift de modelos y cambios estructurales macroeconómicos.

## Limitaciones y posibles fallos

Estimar la matriz de Fisher bajo muestras pequeñas y geometría singular.

## Entregables y criterios de aceptación

- **S1:** revisión bibliográfica verificable, hipótesis operacionales, teoremas/proposiciones y plan preregistrado de simulación.
- **S2:** módulos `src/`, `tests/`, datos sintéticos y script de reproducción, con cobertura de invariantes y casos límite.
- **S3:** comparadores estadísticos, tablas y figuras generadas, análisis de sensibilidad, errores numéricos y benchmark de recursos.
- **S4:** réplica independiente, aplicación con datos públicos licenciados, documentación de riesgos y límites de validez.

## Estructura prevista para el programa completo (MVP anterior implementado)

```text
theory/       # supuestos, derivaciones y pruebas
src/          # modelos, estimadores y algoritmos
tests/        # tests unitarios y estadísticos
experiments/  # simulaciones y benchmarks
data/         # manifiestos y fuentes públicas
docs/         # interpretación, limitaciones y referencias
```

**Regla de evidencia:** no reportar métricas, resultados, referencias bibliográficas ni garantías matemáticas que no hayan sido verificadas.
