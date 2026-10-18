# Ampliación de notebooks recientes — 2026-10-18

Base revisada: `41fc967f2965b00c7c27a911d3b4694cedfbc2cb`.

Se amplían los seis notebooks modificados en los ocho commits más recientes de main. Se conservan sus experimentos históricos y se incorporan derivaciones, experimentos desde inputs, tablas, ocho figuras nuevas, comprobaciones e interpretación de resultados. Ningún nivel de madurez se eleva por esta ampliación.

| Trabajo | Desarrollo añadido |
|---|---|
| OU | Error de medición, identificación por autocovarianzas, 300 réplicas por nivel y comparación a horizonte fijo |
| DRO KL | Derivación primal-dual, 71 radios contra oráculo Bernoulli, saturación, umbral minimax e invariancia afín |
| Transporte | 16 combinaciones de epsilon y presupuesto, cotas vs LP y referencia monótona, mapas de masa y unidades |
| Familias racionales | Contraejemplo exacto de no convexidad, mapa de regret, proyección y lectura geométrica del corpus |
| Forma estratégica | Derivación del problema de tipos raros, tolerancias, recálculo de matrices e invariancia de marginales |
| ES | Integración racional discreta, 60 distribuciones para propiedades y comparación decimal cerca del umbral |

## Reproducción

Instalar `requirements-research.txt` y ejecutar cada notebook desde su propia carpeta. Por ejemplo:

```bash
python -m jupyter nbconvert --execute --to notebook --inplace notebook.ipynb
```

Los experimentos nuevos no requieren red, credenciales ni ejecutar Gambit. Las secciones históricas conservan referencias a resultados ya versionados; releerlos no equivale a volver a ejecutar los solvers externos.

## Verificación realizada

Se validaron los seis archivos con nbformat y se ejecutaron todas sus celdas de código, en orden, en seis procesos Python separados con IPython y directorio de trabajo local por notebook. Se guardaron salidas y figuras y se inspeccionaron visualmente las ocho figuras nuevas. Todos los asserts finalizaron correctamente.

El entorno bloqueó la apertura de sockets de Jupyter, por lo que la ejecución se hizo directamente con IPython, sin kernel Jupyter. La ejecución de los workflows de GitHub queda pendiente del PR; no se afirma haber reproducido todos los benchmarks históricos ni toda la suite del repositorio.

## Notebooks

- [01-stochastic-critical-transitions](02-mathematics-statistics-and-quant/advanced-research/01-stochastic-critical-transitions/notebook.ipynb)
- [03-distributionally-robust-optimization](02-mathematics-statistics-and-quant/advanced-research/03-distributionally-robust-optimization/notebook.ipynb)
- [09-optimal-transport-distributional-dynamics](02-mathematics-statistics-and-quant/advanced-research/09-optimal-transport-distributional-dynamics/notebook.ipynb)
- [rational-family-audit](01-economics-and-econometrics/03-game-theory/01-endogenous-credit-freeze/rational-family-audit/notebook.ipynb)
- [strategic-form-audit](01-economics-and-econometrics/03-game-theory/01-endogenous-credit-freeze/strategic-form-audit/notebook.ipynb)
- [weighted-tail-underflow-guard](03-financial-risk/02-market-and-model-risk/weighted-tail-underflow-guard/notebook.ipynb)
