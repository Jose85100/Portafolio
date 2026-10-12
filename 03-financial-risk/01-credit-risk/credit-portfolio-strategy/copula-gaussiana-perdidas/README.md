# Distribución de pérdidas con cópula gaussiana

Simulación de la distribución de pérdidas de una cartera heterogénea de 200 deudores con un modelo de factor común (cópula gaussiana). Calcula pérdida esperada, VaR y expected shortfall al 99,9 % y los compara con el caso de incumplimientos independientes.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy scipy
python3 main.py
```

## Resultado de ejemplo

```text
Exposicion total: 5,645,840
independientes   EL=     93,320 VaR99.9=     266,769 ES99.9=     285,408
cópula factor    EL=     93,112 VaR99.9=     662,536 ES99.9=     791,101
El VaR con correlacion es 2.48x el de incumplimientos independientes
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
