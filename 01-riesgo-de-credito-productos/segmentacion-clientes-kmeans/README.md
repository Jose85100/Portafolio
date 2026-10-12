# Segmentación de clientes con k-means

Segmentación de clientes por comportamiento de crédito con k-means: estandarización, elección de k por coeficiente de silueta y lectura de la tasa de incumplimiento y el perfil de cada segmento.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas scikit-learn
python3 main.py
```

## Resultado de ejemplo

```text
k=2: silueta=0.534
k=3: silueta=0.524
k=4: silueta=0.350
k=5: silueta=0.292
k=6: silueta=0.305
k elegido = 2
          clientes   ingreso  utilizacion  mora_media  tasa_default
segmento                                                           
0             3394  3906.461        0.235       0.225         0.029
1             2606  1980.847        0.749       1.183         0.137
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
