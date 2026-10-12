# Monitor de límites de apetito de riesgo

Tablero de límites de apetito: calcula utilización de cada límite por sector, rating y deudor y asigna un semáforo (verde, ámbar, rojo) con reglas explícitas de umbral.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas
python3 main.py
```

## Resultado de ejemplo

```text
limite  valor  tope  utilizacion estado
    sector comercio  0.352  0.30        1.172   ROJO
sector construccion  0.208  0.15        1.384   ROJO
         rating C+D  0.330  0.30        1.099   ROJO
           rating D  0.098  0.08        1.225   ROJO
       mayor deudor  0.022  0.04        0.557  VERDE
estado
ROJO     4
VERDE    1
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
