# Validación de modelo: Gini, calibración y PSI

Validación independiente de un modelo de PD: comparación champion (regresión logística) contra challenger (gradient boosting), discriminación (Gini), calibración por deciles y estabilidad (PSI) entre desarrollo y muestra fuera de tiempo, con umbrales de alerta.

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas scikit-learn
python3 main.py
```

## Resultado de ejemplo

```text
champion (logit): Gini desarrollo=0.521 OOT=0.549 | PSI score=0.163 [AMBAR]
challenger (GBM): Gini desarrollo=0.648 OOT=0.555 | PSI score=0.128 [AMBAR]
Calibracion del champion en OOT (por quintil):
       pd_media  tasa_observada
decil                          
0        0.0314          0.0331
1        0.0693          0.0650
2        0.1163          0.0975
3        0.1902          0.1631
4        0.3695          0.3938
PD media predicha 0.1553 vs tasa observada 0.1505
```
