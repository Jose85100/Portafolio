# Pronóstico con ARIMA y selección por AIC

Pronóstico de una serie con tendencia y estacionalidad: selección de orden ARIMA por AIC en una malla, validación en un tramo reservado y comparación contra un pronóstico ingenuo estacional.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas statsmodels
python3 main.py
```

## Resultado de ejemplo

```text
Orden elegido por AIC: ARIMA(1, 1, 1) x (1,0,0,12) | AIC=775.9
RMSE modelo   = 1.731
RMSE ingenuo estacional = 2.869
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
