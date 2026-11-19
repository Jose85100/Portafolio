# Benchmark retrospectivo: IRL mensual por entidad

¿Cuánto error cometen dos pronósticos simples del IRL publicado del mes siguiente? Este ejercicio agrega una referencia empírica al laboratorio de liquidez. **No calibra ni valida el modelo de primera ruptura**, no mide un faltante de caja y no evalúa el cumplimiento actual de una entidad.

## Datos y calidad

La entrada es el [derivado de IRL SFC por entidad y mes](../observed-sfc-irl/results/sfc_irl_by_entity_month.csv), generado del [snapshot SFC y su manifiesto](../observed-sfc-irl/README.md). Fuente primaria: [Superintendencia Financiera de Colombia, IRL de establecimientos de crédito](https://www.superfinanciera.gov.co/publicaciones/10108220/informes-y-cifrascifrasestablecimientos-de-creditoinformacion-periodicamensualindicadores-de-riesgo-de-liquidez-indicador-de-riesgo-de-liquidez-irl-10108220/). Archivo descargado el 10-nov-2026; cobertura de marzo de 2020 a diciembre de 2022. El derivado usado tiene SHA-256 `d4b1e8eb6bb1606abd9c5f0fed572d00a19d2cd5a4da94d83eb4b5bb1c801929`. Se verifica el hash, claves entidad-mes únicas, fechas legibles, IRL finito no negativo y RLN positivo. Los faltantes no se imputan.

La variable objetivo es `irl_pct_reported`, la razón de activos líquidos de mercado promedio sobre requerimiento de liquidez neto promedio a 30 días, expresada en **porcentaje**, por entidad y corte. Se compara en **puntos porcentuales**. El IRL es una razón prudencial, no una probabilidad; valores elevados pueden obedecer a un denominador pequeño. Son cifras agregadas mensuales, no flujos diarios ni costos o impactos de venta.

## Diseño y resultados

Se fijó antes del cálculo la ventana de evaluación enero–diciembre de 2022. Se comparan en la **misma muestra pareada**:

1. Persistencia: usar IRL del mes anterior.
2. Media móvil: promedio de los tres meses previos consecutivos, sin incluir el mes objetivo.

Se exigen los tres meses previos para ambos métodos, para no confundir diferencia de método con diferencia de muestra. De 525 observaciones objetivo se evalúan 515 (45 entidades distintas); 10 carecen de historia consecutiva completa y se excluyen. La composición puede cambiar de un mes a otro y el cálculo pondera igualmente cada entidad-mes, no los activos. Las métricas y las 12 desagregaciones mensuales están en [results.json](results.json), y cada predicción en [predictions.csv](predictions.csv).

| Método | MAE, pp | RMSE, pp | Mediana del error absoluto, pp |
|---|---:|---:|---:|
| Persistencia | 96,49 | 249,32 | 23,87 |
| Media móvil de tres meses | 97,33 | 249,53 | 25,87 |

Los promedios son mucho mayores que las medianas: hay observaciones extremas. Por ejemplo, la entidad `1-65` pasó de 3.335,57% en agosto a 1.250,86% en septiembre de 2022. Son diferencias descriptivas sin intervalos de incertidumbre, no evidencia de superioridad general de un método. Las 515 filas proceden de entidades repetidas y meses dependientes; no deben tratarse como observaciones independientes para inferencia.

No se dispone de fecha de disponibilidad ni de vintages de publicación de cada observación. Aunque se impide usar meses futuros en el cálculo, **esto es un backtest retrospectivo**, no una prueba de operación en tiempo real. Tampoco garantiza que los cambios de denominación o estructura societaria preserven comparabilidad económica para cada código. No usar el ejercicio para predecir defaults, iliquidez, incumplimientos, flujos o fire sales. Harían falta flujos de caja fechados, posiciones, colateral, eventos de tensión y vintages disponibles para validar los modelos dinámicos.

## Reproducir

Sin dependencias externas, desde la raíz del repositorio:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 03-financial-risk/03-market-liquidity-research/03-liquidez-estocastica/irl-forecast-benchmark/run.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s 03-financial-risk/03-market-liquidity-research/03-liquidez-estocastica/irl-forecast-benchmark -v
```

El runner produce `results.json` y `predictions.csv` con el hash del insumo. Las pruebas cubren cálculos manuales, ausencia de meses, duplicados e independencia de los predictores respecto de los objetivos futuros.
