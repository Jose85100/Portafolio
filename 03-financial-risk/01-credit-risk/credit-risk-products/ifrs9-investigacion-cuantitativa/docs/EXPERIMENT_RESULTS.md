# Experimento IFRS 9 multimodelo — 18 de octubre de 2026

## Alcance ejecutado

Base: commit `494fca0` de la PR #49. Tres modelos de PD, tres LGD y dos adaptadores mixtos EAD generan **18 configuraciones completas**; la matriz simplificada se estudia aparte. Hay cuatro notebooks nuevos y se conserva el laboratorio anual. Se trata de código ajustado y ejecutado sobre datos sintéticos, sin aprobación contable ni validación externa.

## Muestra y partición

2.200 contratos históricos: 1.335 de entrenamiento y 865 OOT, con embargo de ventanas de performance. Cartera al corte independiente de 180 contratos: 97 Stage 1, 78 Stage 2 y 5 Stage 3. Los workouts reservados son 432; ventanas CCF reservadas, 390. No hay crisis ni cambio de régimen; el calendario OOT es construido para verificar separación temporal.

## PD: evidencia fuera de tiempo

| Modelo | PD media | Default observado | Brier | Log-loss | AUC |
|---|---:|---:|---:|---:|---:|
| pd_logit_12m | 10.0256% | 9.5954% | 0.080586 | 0.282988 | 0.738853 |
| pd_monthly_survival | 9.9245% | 9.5954% | 0.080516 | 0.284074 | 0.736635 |
| pd_rating_transitions | 15.1167% | 9.5954% | 0.086174 | 0.305944 | 0.714526 |

El generador usa hazard logístico, de modo que favorece modelos cercanos a esa estructura. El proceso de ratings no reproduce exactamente el generador de default, y su sobreestimación permanece visible. No se concluye que Markov sea inferior en una cartera real. La calibración a 12m no valida extrapolación lifetime. Los notebooks calculan contrastes de Brier pareados y bandas Wilson para calibración agrupada con mínimo 20 contratos por bin.

## LGD y CCF: conjuntos reservados

| Componente | Modelo | n | MAE | RMSE | Sesgo |
|---|---|---:|---:|---:|---:|
| LGD | lgd_segment_workout | 432 | 0.145686 | 0.177846 | 0.009639 |
| LGD | lgd_fractional_workout | 432 | 0.083364 | 0.103350 | -0.001933 |
| CCF | fixed_ccf | 390 | 0.103071 | 0.126557 | 0.033775 |
| CCF | fractional_ccf | 390 | 0.073152 | 0.090122 | -0.001460 |

La LGD por flujos usa parámetros suministrados, no un ajuste de workout. El CCF se evalúa en fracción del cupo no utilizado: aún falta backtest monetario de EAD por horizonte en datos reales.

## ECL integrada

La ECL agregada va de **69,345.73 a 148,061.92 unidades monetarias** según especificación. El baseline es **71,185.65**. El rango no es un intervalo de confianza ni un conjunto de opciones de política contable. Las diferencias incorporan supuestos de modelo, y la LGD estructural no está calibrada al mismo objetivo del generador de workouts.

Los stages se mantienen fijos en el factorial; la sensibilidad SICR se calcula por separado. La ruta Stage 3 no usa PD futura ni CCF y mantiene recuperaciones que pueden ocurrir después de la vida contractual. El bootstrap pareado mantiene ajustes y escenarios fijos: mide variación de composición de cartera, no incertidumbre total del modelo.

## Validación técnica

- **58 tests unittest**, incluidos los 21 heredados y 37 nuevos, aprobados. Cubren identidades independientes y entradas patológicas, no sólo réplicas de implementación.
- **5/5 notebooks** ejecutados en procesos IPython independientes con celdas en orden; cuatro guardan outputs nuevos y el anterior se comprobó sin reescribirlo.
- **9 figuras nuevas** inspeccionadas visualmente. En calibración se añadieron bandas Wilson y se evitan bins con n<20.
- HTML de los cuatro notebooks nuevos generado; revisión visual de las figuras guardadas, sin afirmar inspección del HTML en un navegador.
- CLI ejecutada y artefactos regenerados. Hashes del código y versiones numéricas en manifest; no se promete igualdad bit a bit entre versiones de sklearn.
- CI define unittest en Python 3.11/3.12 y ejecución de los cinco notebooks en kernels Jupyter limpios. La ejecución local usa IPython directo, no nbclient; CI remoto queda pendiente.
- SQLite valida claves, correspondencia stage/base y sumas de peso mediante vista de auditoría; no es un ETL ni una migración productiva.

## Entrega y siguientes brechas

Ver [arquitectura](ARCHITECTURE.md), [fichas](MODEL_CARDS.md), [método](METHODOLOGY.md) y [contratos](DATA_AND_VALIDATION.md). Los CSV y parámetros en `results/multimodel` se regeneran con `run_multimodel.py`; `--save-monthly` exporta contribuciones completas del baseline.

Persisten: datos reales, validación de vida, vintages macro, dependencia residual LGD–EAD, recuperación censurada, riesgos competitivos, sobreutilización, POCI, modificaciones, curas, asientos e interés neto. Tampoco se implementa provisión prudencial SFC. El modelo de staging recibe PD comparable como dato; no reconstruye expectativa original. Estas fronteras están en las fichas, no se presentan como funcionalidades entregadas.
