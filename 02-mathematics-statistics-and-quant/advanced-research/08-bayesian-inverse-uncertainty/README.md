# Bayesian Inverse Problems & Uncertainty Quantification

**Madurez: S2 — prototipo ejecutable acotado (2026-10-14).** No valida el programa
completo, no es investigación publicada ni demuestra originalidad algorítmica.

## Pregunta y alcance
¿Puede una implementación estable del posterior gaussiano separar error numérico
de mala calibración por un ruido o prior mal especificados?

Modelo: `y = A theta + eta`, `theta ~ N(0, tau² I)`, `eta ~ N(0, sigma² I)`.
Se implementan media y covarianza posterior mediante SVD, QR aumentado y
ecuaciones normales, con referencia independiente de 80 dígitos para las entradas
float64 reales. Un experimento separado mide cobertura prior-predictiva bajo
supuestos correctos e incorrectos, con 1.000 réplicas.

## Un comando de reproducción
Desde esta carpeta (Linux/macOS, Python 3.11+, make e internet para pip):
```bash
make run
```
Crea `.venv`, instala versiones directas fijadas, ejecuta Ruff, mypy, tests y
cobertura, benchmarks, notebook y reporte. BLAS/OMP se limitan a un hilo.

## Artefactos
- `config.json`: semillas, dimensiones, condicionamiento y umbrales fijados antes de ejecutar.
- `src/posterior.py`: kernels con validación y tipos.
- `src/oracle.py`: referencia mpmath de 80 dígitos, solo para validación.
- `src/benchmark.py`: precisión, tiempo, memoria y calibración separados.
- `tests/`: fórmulas escalares, nulidad, equivarianza, límites y Hypothesis.
- `benchmarks/`: resultados crudos CSV, resumen JSON, figura y evidencia de pruebas.
- `notebook.ipynb`: ejecutado con salidas visibles.
- `informe.md`, `referencias.bib`, `MVP.md`: análisis crítico, referencias y límites.

## Tests aislados
```bash
.venv/bin/python -m pytest --cov=src.posterior tests
```
La cobertura reportada corresponde a `src.posterior`, no a toda la aplicación.
El notebook se ejecuta realmente mediante IPython en proceso; no necesita kernel
TCP. Sigue siendo un notebook Python estándar reejecutable por Jupyter.

## Límites del entorno y del modelo
Versiones directas fijadas; no lock transitivo ni imagen Docker. Dominio del
kernel: A no vacío, cuadrado o alto, entradas y datos finitos con magnitud ≤1e4;
sigma/tau entre 1e-14 y 1e4. Dense float64, no problemas gigantes ni garantía de
precisión para toda combinación admitida. Un posterior correcto numéricamente
no corrige ruido, prior u operador equivocados. Cobertura prior-predictiva no es
cobertura frecuentista uniforme para parámetros fijos.
