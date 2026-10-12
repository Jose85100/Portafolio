# Análisis de cosechas (vintage)

Curvas de incumplimiento acumulado por cohorte de originación con una hazard que crece y decae con la antigüedad. Compara cosechas, identifica la de peor desempeño y la ubica frente al promedio.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas
python3 main.py
```

## Resultado de ejemplo

```text
default_6m  default_12m  default_18m
V01      0.0313       0.0707       0.1007
V02      0.0100       0.0263       0.0333
V03      0.0187       0.0460       0.0677
V04      0.0173       0.0423       0.0557
V05      0.0183       0.0340       0.0490
V06      0.0203       0.0433       0.0650
V07      0.0127       0.0313       0.0417
V08      0.0163       0.0397       0.0613
V09      0.0270       0.0597       0.0847
V10      0.0293       0.0667       0.0963
V11      0.0197       0.0413       0.0640
V12      0.0147       0.0430       0.0653
Promedio a 12 meses: 0.0454
Peor cosecha: V01 con 0.0707 (1.56x el promedio)
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
