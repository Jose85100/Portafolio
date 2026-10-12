# Segmentación de clientes con k-means

Segmentación de clientes por comportamiento de crédito con k-means: estandarización, elección de k por coeficiente de silueta y lectura de la tasa de incumplimiento y el perfil de cada segmento.

## Método y contrato

Con variables estandarizadas, k-means minimiza \(\sum_{c=1}^{k}\sum_{i\in C_c}\lVert x_i-\mu_c\rVert^2\). El script elige el \(k\) de mayor silueta entre 2 y 6 y presenta perfiles descriptivos. El default se usa solo **después** para describir segmentos; no participa en el clustering.

El grano es **cuenta–fecha de corte** con `monthly_income`, `utilization`, `days_past_due`/mora y, para lectura posterior, `default_flag`. Un clúster es una agrupación exploratoria, no una clase de riesgo, score ni regla de elegibilidad. Antes de uso real se requiere estabilidad temporal, representatividad, revisión de sesgo y gobierno; véanse el [contrato común](../docs/DATA_CONTRACTS.md) y la [guía de gobierno](../docs/QUALITY_AND_GOVERNANCE.md).

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
