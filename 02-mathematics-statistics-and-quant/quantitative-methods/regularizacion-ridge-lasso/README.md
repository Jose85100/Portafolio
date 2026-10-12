# Regularización: OLS, Ridge y Lasso

Comparación de mínimos cuadrados, Ridge y Lasso en un problema con 60 variables de las que solo 6 importan. Mide error fuera de muestra y capacidad de recuperar las variables verdaderas.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy scikit-learn
python3 main.py
```

## Resultado de ejemplo

```text
n=200 observaciones, p=60 variables, 6 relevantes
OLS    RMSE prueba=2.667 | variables no nulas=60 | relevantes recuperadas=6/6
Ridge  RMSE prueba=2.532 | variables no nulas=60 | relevantes recuperadas=6/6
Lasso  RMSE prueba=2.238 | variables no nulas=26 | relevantes recuperadas=6/6
Error irreducible (sigma) = 2.000
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
