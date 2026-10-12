# Validación cruzada temporal y fuga de información

Demostración de por qué la validación cruzada aleatoria es engañosa en series de tiempo: sobre una serie persistente sin poder predictivo real, la validación aleatoria reporta un R² alto, mientras la validación temporal muestra el desempeño verdadero.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy scikit-learn
python3 main.py
```

## Resultado de ejemplo

```text
Serie persistente sin senal predictiva real (solo indice de tiempo como variable)
R2 con KFold aleatorio (con fuga temporal): 0.961
R2 con TimeSeriesSplit (sin fuga):         -0.588
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
