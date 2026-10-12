# Métricas de desempeño y atribución

Biblioteca de métricas de desempeño de un portafolio frente a su benchmark: retorno anualizado, volatilidad, Sharpe, Sortino, máximo drawdown, Calmar, alfa y beta por regresión, tracking error e information ratio.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas statsmodels
python3 main.py
```

## Resultado de ejemplo

```text
portafolio  benchmark
retorno_anual          0.0720     0.0116
volatilidad            0.1814     0.1529
sharpe                 0.3088    -0.0446
sortino                0.4466    -0.0626
max_drawdown          -0.3390    -0.3599
calmar                 0.2125     0.0321
alfa_anual             0.0636        NaN
beta                   1.1072        NaN
tracking_error         0.0671        NaN
information_ratio      0.9365        NaN
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
