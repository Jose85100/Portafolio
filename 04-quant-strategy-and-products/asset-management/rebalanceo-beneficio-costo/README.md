# Rebalanceo por beneficio frente a costo · CICLO_DIARIO 2026-10-12

**M2 — prototipo verificado con evidencia sintética; no producto listo para producción.**
Extiende `../backtest-rebalanceo-con-costos/` sin modificar su baseline histórico.

Desde la raíz del repositorio, un único comando instala el entorno, hace lint,
ejecuta tests con cobertura, corre 720 backtests, genera CSV/JSON/figura y ejecuta el notebook:

```bash
bash 04-quant-strategy-and-products/asset-management/rebalanceo-beneficio-costo/reproduce.sh
```

Requiere Python 3.12, bash, venv e internet sólo para instalar dependencias.
Entorno alternativo: `docker build -t quant-cost-gate .` y `docker run --rm quant-cost-gate`
(desde esta carpeta; los resultados quedan dentro del contenedor si no se monta un volumen).
Dockerfile provisto, **build de Docker no ejecutado**.

## Pregunta e hipótesis

¿Corregir la precisión del optimizador y evitar operaciones cuyo beneficio estimado
de riesgo es menor que el costo reduce rotación sin perder demasiado desempeño?
H1 primaria: `gate_no_shrink` reduce rotación media contra `monthly_mv` a 10 bps.
H2 secundaria: la diferencia pareada de Sharpe es positiva; puede ser refutada o inconclusa.
No se atribuye novedad mundial a la regla: la novedad incremental en el repo es
normalización + certificado de optimalidad + evaluación pareada de un filtro auditable.

## Modelo

Mínima varianza long-only, suma de pesos 1. Covarianza diaria estimada exclusivamente
con 252 retornos anteriores. SLSQP sobre covarianza dividida por traza media,
gradiente analítico, `ftol=1e-12`, máximo 1000 iteraciones, factibilidad y gap de
primer orden en simplex <=1e-5 en unidades normalizadas.
En fechas mensuales (21 días), comparar:

`beneficio = gamma * 21 / 2 * (w_actual' Σ w_actual - w_objetivo' Σ w_objetivo)`

`costo = 0.001 * sum(abs(w_objetivo - w_actual))` para 10 bps.

Operar sólo si beneficio > costo; gamma=5 fijo. Es una aproximación miope de utilidad
cuadrática que **ignora diferencias esperadas de retorno**. `gate` incorpora 20% de
shrinkage diagonal fijo, no Ledoit-Wolf estimado; `gate_no_shrink` aísla el filtro.
Los pesos derivan con precios después del retorno. Retorno neto `(1-costo)*(1+bruto)-1`.
Rotación reportada es compra + venta; no se divide por dos. rf=0, Sharpe aritmético
anualizado, drawdown incluyendo riqueza inicial=1; ver fórmulas en `src/portfolio.py`.

## Archivos y evidencia

- `main.py`, `src/portfolio.py`: benchmark y motor modular.
- `tests/`: caso analítico, invariancia a escala, 30 matrices PSD aleatorias, no lookahead,
  costos, drift, edge cases, fallos del solver y ablation costo cero.
- `results/raw.csv`: 720 registros completos; `daily.csv.gz` y `decisions.csv`: trazas seed 41.
- `results/summary.csv`, `paired_bootstrap.csv`, `solver_diagnostic.json`, `scaling.csv`.
- `results/wealth.png`, `metadata.json`, `legacy_stdout.txt`, `tests.txt`, `coverage.json`.
- `notebook.ipynb`: ejecutado con IPython en proceso, outputs visibles; `benchmarks/execute_notebook.py` lo reproduce.
- `informe.md`: cifras, fallos, sesgos y cierre; `referencias.bib`: ocho fuentes reales.
- `MVP.md`, `requirements.txt`, `Dockerfile`, `reproduce.sh`.

Pruebas aisladas desde esta carpeta: `python -m pytest tests -q --cov=src --cov-branch`.
Lint: `python -m ruff check src tests main.py benchmarks`.
Los motores C++ no se modifican; no se expone binding ni se duplican sus funciones.
No se afirma validación de GoogleTest, clang-tidy o sanitizers: CMake no estaba instalado
en este entorno al intentar una regresión adicional. El alcance entregado es Python.
