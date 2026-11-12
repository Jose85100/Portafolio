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

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.

## Companion con datos observados

El laboratorio de Gini, calibración y PSI de scores sigue siendo sintético. La [aplicación SFC de mezcla de calificaciones](observed-sfc-grade-composition/) calcula un PSI descriptivo sobre la composición de saldos A–E para crédito rotativo. Esta señal observada **no es PSI de scores ni valida discriminación o calibración**; para esas métricas se necesitan scores versionados enlazados a outcomes de default maduros y una partición temporal autorizada.


## Aplicación observada externa

[Benchmark de Gini, calibración y PSI con UCI](observed-uci350/README.md): regresión independiente y prueba aleatoria del mismo periodo, no validación temporal.
