# VaR y Expected Shortfall: método controlado y aplicación observada

Este trabajo tiene dos ediciones complementarias. El laboratorio controlado permite observar el comportamiento de los estimadores cuando se conoce el proceso generador. La edición oficial contrasta su aplicación sobre cambios de tasa publicados por el U.S. Treasury, con una validación fuera de tiempo y límites explícitos.

## Edición oficial: aplicación con curva del Tesoro

La fuente oficial provee rendimientos par diarios a plazo constante a 10 años. La transformación aproxima el P&L de una posición larga con duración modificada fija de ocho años. El backtest usa 500 observaciones de estimación y 214 días fuera de tiempo; compara VaR histórico, normal y t ajustada al 95% y 99%.

Esta evidencia evalúa una exposición estilizada al factor de tasa, no el retorno total de un bono ni la aptitud de un modelo productivo. La curva se interpola desde cotizaciones indicativas; el proxy omite convexidad, carry, roll-down y flujos del instrumento. La muestra de 214 días tiene baja potencia para validar la cola de 99%.

- [Informe de aplicación observada y resultados](reports/official-application-2026-11-10.md)
- [Fuente, datos congelados y transformaciones](data/README.md)
- [Runner reproducible](official_version.py)
- [Brief ejecutivo de una página](../../../output/pdf/var-es-official-application-brief.pdf)

## Laboratorio controlado: dinámicas del método

El notebook conserva escenarios con proceso generador conocido para comparar sesgo, error de estimación y sensibilidad de cuatro métodos, incluida teoría de valores extremos. Ese diseño permite verificar propiedades del estimador bajo los supuestos del experimento; sus números no son evidencia de desempeño sobre una mesa real.

## Cómo ejecutar

```bash
pip install numpy scipy
python3 main.py
```

## Resultado del laboratorio controlado

```text
Valor del portafolio: 1,000,000 | observaciones: 2500
 nivel       metodo          VaR           ES
  0.95    historico       14,974       22,541
  0.95       normal       15,889       19,989
  0.95    t-student       14,792       22,352
  0.99    historico       27,222       35,472
  0.99       normal       22,576       25,901
  0.99    t-student       26,485       36,823
```

## Notebook controlado

[`notebook.ipynb`](notebook.ipynb) desarrolla el tema de forma extensa: versión ingenua, diagnóstico, mejoras, robustez y **pruebas automáticas** (`assert`) que fallan el notebook si un hallazgo deja de cumplirse. Las cifras de sus conclusiones se calculan desde los datos. `main.py` es la versión corta del mismo tema.


## Contrato histórico revisado — 2026-10-18

`main.py:historico` usa VaR empírico sin interpolación y ES de masa fraccionaria exacta. El caso de 99 ceros y pérdida 100 al 97.5% devuelve ES=40. La función `historico_legacy_conditional` preserva el antiguo promedio condicionado como comparador deliberado del benchmark; no es la API por defecto. Importar el módulo ya no ejecuta la demo ni ajusta modelos automáticamente.

El método t usa una distribución predictiva ajustada y 400.000 draws con semilla explícita; no es la misma medida empírica sobre las n observaciones originales. El notebook conserva su desarrollo didáctico y sus comparaciones de estimación.
