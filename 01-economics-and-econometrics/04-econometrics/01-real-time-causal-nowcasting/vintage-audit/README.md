# Vintage Audit — auditor factorial de filtración temporal

**Madurez: S2 (prototipo sintético)** del componente de evaluación del programa
Real-Time Causal Nowcasting. El modelo de factores/MIDAS y la identificación causal
siguen en S1. No se afirma validación S3 ni resultados empíricos.

Desde la raíz del repositorio, instalación, checks, tests, benchmark y notebook en un comando:

```bash
bash 01-economics-and-econometrics/04-econometrics/01-real-time-causal-nowcasting/vintage-audit/reproduce.sh
```

Requiere Python 3.12, `venv`, Bash y acceso a PyPI la primera vez. Probado en Linux
x86_64. Dependencias directas fijadas en requirements.txt; entorno completo observado
en environment-lock.txt. Se crea un entorno local .venv; no modifica el Python global.
El comando es fail-fast: cualquier test/check fallido detiene la ejecución.

## Qué produce

- `results/predictions.csv`: 108 000 predicciones pareadas, cinco brazos, cuatro escenarios, 30 seeds.
- `results/release_ledger_seed0.csv`: event time, availability time, primer/final release.
- `results/summary.csv`, `seed_metrics.csv`, `paired.csv`, `uncertainty.csv`: RMSE, diferencias de MSE y bootstrap entre seeds.
- `results/cost_by_arm.csv` y `results/scalability.csv`: tiempo y memoria Python trazada para n=240/480/960.
- `results/comparison.png`, `metadata.json`, `coverage.txt`, `benchmark.log`.
- `notebook.ipynb`: celdas ejecutadas en IPython in-process, outputs visibles, figura y cobertura.

## Implementación

`src/vintages.py` contiene simulación, consulta as-of, controles retrospectivos y
rolling-origin OLS. Importa el OLS original de `computational-economics/src/econlab.py`.
`benchmarks/run.py` ejecuta todos los escenarios; `tests/` incluye invariancia ante
mutación futura, casos degenerados, control positivo y equivalencia numérica con NumPy.

Ver [informe.md](informe.md), [MVP.md](MVP.md) y [referencias.bib](referencias.bib).

## Entorno alternativo

Desde la raíz del repositorio:

```bash
docker build -f 01-economics-and-econometrics/04-econometrics/01-real-time-causal-nowcasting/vintage-audit/Dockerfile -t vintage-audit .
docker run --rm vintage-audit
```

Dockerfile incluido como receta; build Docker no ejecutado en este ciclo. Las instrucciones
venv anteriores sí se ejecutaron. Los artefactos Docker quedan en el contenedor salvo montaje.
No comparar tiempos instrumentados con tiempos de producción; tracemalloc no mide RSS ni BLAS.
