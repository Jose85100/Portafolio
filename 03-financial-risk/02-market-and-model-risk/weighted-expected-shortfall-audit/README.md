# Weighted Expected Shortfall Audit

MVP de validación numérica, 2026-10-13. Integra ES ponderado por masa fraccionaria y audita convenciones incompatibles en ejemplos del portafolio. Pérdidas positivas, confianza α, cola de masa 1−α. La fórmula es conocida; el aporte incremental es el contrato explícito, soporte ponderado y evidencia reproducible contra los baselines actuales y un LP independiente.

## Un comando

Requisitos: repositorio completo, Bash, Python **3.12** con `venv`, pip, conexión para descargar dependencias inicialmente. Desde esta carpeta:

```bash
bash run.sh
```

Instala el entorno local, ejecuta Ruff, mypy, pytest con cobertura de `src.tail` y `src.oracle`, experimentos, rendimiento y notebook con salidas reales, ejecutado con IPython dentro del proceso (sin sockets de Jupyter). No usa datos externos. Comando desde la raíz del repo:

```bash
bash 03-financial-risk/02-market-and-model-risk/weighted-expected-shortfall-audit/run.sh
```

Números/errores reproducibles con seeds fijas; tiempo y memoria dependen del hardware. La instalación inicial requiere internet, la ejecución posterior solo dependencias instaladas. `requirements.txt` fija versiones directas y `requirements.lock.txt` fija el entorno completo; `results/metadata.json` identifica versiones y hardware.

## Artefactos

- `src/tail.py`: motor O(n log n), VaR por inversa CDF y ES con frontera fraccionaria.
- `src/oracle.py`: LP dual HiGHS, formulación equivalente de CVaR.
- `src/baselines.py`: extrae y ejecuta funciones reales del repo sin ejecutar sus demos; SHA256 guardados.
- `benchmarks/config.json`: diseño fijado antes de ejecutar, alpha=0.975, n=250/501, 40 réplicas, seed=20261013.
- `results/trials.csv`, `summary.csv`, `counterexample.csv`, `performance.csv`: resultados crudos.
- `results/audit.png`: contraejemplo y escalabilidad; `notebook.ipynb`: ejecutado, narrativa y outputs.
- `results/tests.txt`, `coverage.json`, `lint.txt`, `types.txt`: verificación.
- `informe.md`, `referencias.bib`, `MVP.md`: interpretación, prior art y alcance.

## Baselines y equidad

`var-es-tres-metodos.historico` y `risk_models.empirical_var_es` se comparan con el ES correcto sobre **la misma distribución finita**. `laboratorio.tail_risk` ya implementa correctamente la masa fraccionaria uniforme y debe coincidir. No se debilitan ni recalibran estos baselines. En escenarios con pesos desiguales, aplicar estos métodos uniformes es una **ablación de pesos**, no una comparación entre modelos ponderados. El competidor ponderado válido es el LP.

El error reportado NO es error de predicción ni sesgo frente al ES poblacional. VaR inversa-CDF y cuantiles interpolados son convenciones distintas; no se afirma superioridad de pronóstico del VaR.

## Verificación aislada

Con `.venv` activado: `python -m pytest -q`, `python -m ruff check src tests benchmarks`, `python -m mypy src benchmarks`, `python -m src.main`. Cobertura declarada solo para el núcleo numérico/oráculo, no todo el pipeline. Ver alcance exacto en `MVP.md` e informe.


## Revisión de contratos de riesgo — 2026-10-18

El comparador de construcción vivo ya integra masa fraccionaria y coincide con ES=40 en el contraejemplo de 99 ceros y una pérdida de 100 a 97.5%. La cifra histórica 100/3 permanece en los resultados del benchmark anterior, asociado a su commit y hashes; no se ha reescrito esa evidencia como si proviniera del código nuevo.

El extractor AST incluye ahora el cierre de helpers de la función elegida y sus primitivas numéricas explícitas; sigue excluyendo demos de nivel superior. Las pruebas contrastan el código actual. Para repetir un benchmark histórico se debe usar su versión de fuentes registrada.

El comparador histórico ingenuo se conserva con nombre explícito `historico_legacy_conditional`; la API actual `historico` ya usa masa fraccionaria. Las pruebas verifican ambas semánticas por separado.
