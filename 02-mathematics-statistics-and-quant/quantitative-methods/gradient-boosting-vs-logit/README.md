# Gradient boosting frente a regresión logística

Comparación de una regresión logística y un modelo de gradient boosting en un problema con interacciones no lineales: AUC, Brier score y diferencia de desempeño entre un caso lineal y uno no lineal.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy scikit-learn
python3 main.py
```

## Resultado de ejemplo

```text
caso     modelo     AUC   Brier
    lineal      logit   0.780   0.171
    lineal   boosting   0.774   0.173
 no_lineal      logit   0.626   0.226
 no_lineal   boosting   0.777   0.184
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
