# Scorecard logístico con WoE e IV

Construcción de un scorecard de probabilidad de incumplimiento: discretización por cuantiles, Weight of Evidence, Information Value, regresión logística y evaluación con AUC y KS en una muestra de prueba.

## Método y contrato

Para cada bin \(b\), \(WoE_b=\log(\%good_b/\%bad_b)\), y \(IV=\sum_b(\%good_b-\%bad_b)WoE_b\). Sobre las variables transformadas se ajusta \(P(D=1\mid x)=\operatorname{logit}^{-1}(\beta_0+\beta^\top WoE(x))\). El suavizado de 0.5 evita divisiones por cero en esta demostración.

El grano es **solicitud o cuenta–fecha de corte**. `ingreso`, `edad`, `utilizacion` y `mora_previa` deben existir antes de la ventana de desempeño; `default` es la etiqueta posterior. La división aleatoria se usa solo para hacer el ejemplo compacto: una implementación real exige split temporal, definición aprobada de `bad`, tratamiento de rechazados, estabilidad y revisión de sesgo. Véase el [contrato común](../docs/DATA_CONTRACTS.md) y la [guía de gobierno](../docs/QUALITY_AND_GOVERNANCE.md).

## Datos

Datos **sintéticos** generados con semilla fija (`numpy.random.default_rng`). No hay datos de clientes, de empresas ni confidenciales. Los resultados son **ilustrativos del método**, no evidencia de desempeño real.

## Cómo ejecutar

```bash
pip install numpy pandas scikit-learn
python3 main.py
```

## Resultado de ejemplo

```text
Information Value por variable:
  ingreso      IV = 0.054
  edad         IV = 0.020
  utilizacion  IV = 0.141
  mora_previa  IV = 0.105
Tasa de default en prueba: 0.094
AUC = 0.667 | Gini = 0.333 | KS = 0.254
```

## Notebook

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.
