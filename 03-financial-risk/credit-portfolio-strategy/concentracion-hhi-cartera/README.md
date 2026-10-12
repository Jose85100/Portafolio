# Concentración de cartera con HHI

Medición de concentración por deudor y por sector con el índice Herfindahl-Hirschman, número efectivo de contrapartes, participación de los mayores deudores y comparación con límites de apetito.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas
python3 main.py
```

## Resultado de ejemplo

```text
HHI por deudor: 0.0081 | numero efectivo de deudores: 124 de 500
HHI por sector: 0.1800 | numero efectivo de sectores: 5.6 de 8
Participacion top 10 deudores: 21.0% | mayor deudor: 3.99%
Participacion por sector:
sector
comercio        0.281
industria       0.206
servicios       0.154
agro            0.126
transporte      0.111
construccion    0.078
energia         0.030
tecnologia      0.016
  mayor deudor <= 5%: CUMPLE
  top 10 <= 25%: CUMPLE
  mayor sector <= 30%: CUMPLE
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
