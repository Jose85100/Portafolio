# Portafolio ilustrativo con cupos observados UCI

Ejercicio reproducible del motor C++ usando [Default of Credit Card Clients, UCI, I-Cheng Yeh (2009)](https://doi.org/10.24432/C55S3H), licencia CC BY 4.0. Reutiliza el XLS versionado en el [benchmark del portafolio](../../../01-credit-risk/credit-risk-products/scorecard-logistico-woe/observed-uci350/README.md); descarga del 12-nov-2026, SHA-256 `30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933`. Grano: cliente, Taiwán, 2005; etiqueta de impago de pago del mes siguiente. No es Colombia ni crédito en originación.

## Variables y supuestos

- `LIMIT_BAL`: cupo observado en TWD, **proxy ilustrativo de exposición**; no es saldo usado ni EAD. Se comprueban 30.000 filas, identificadores únicos, cupos positivos y target binario.
- `default payment next month`: impago observado, no severidad de pérdida ni recuperaciones.
- PD: tasa global de impago de 22.500 clientes de entrenamiento; se compara con tasas de tres segmentos de cupo cuyos cortes se aprenden solo en entrenamiento. División aleatoria por fila con semilla 42 y prueba con 7.500. No se estratifica ni hay separación temporal.
- LGD: 45% fija e hipotética; no se obtiene de la fuente. El proxy de pérdida realizada es `cupo × 0,45 × etiqueta`; no es pérdida real. La varianza del motor supone defaults independientes y exposiciones fijas.

## Ejecución y resultado

Requiere Python 3, pandas, xlrd y compilador C++17. Desde la raíz:

```bash
python3 03-financial-risk/06-quantitative-research-engine/examples/uci_limit_proxy/run.py
```

La salida almacenada en [results.json](results.json) documenta el corte: tasa de entrenamiento 22,09%, prueba 22,20%; suma de cupos de prueba TWD 1.249.380.000. El motor calcula pérdida proxy esperada de TWD 124.213.360 frente a TWD 97.420.500 para el proxy construido con etiquetas observadas. La diferencia refleja, entre otras cosas, la relación entre cupo e impago, no una validación de pérdidas reales. La varianza no incorpora dependencia ni incertidumbre de estimación. No usar para capital, provisiones, decisiones individuales o extrapolación a otra población; faltan EAD, recuperaciones, horizontes y validación temporal.

Como comparación, los cortes de entrenamiento son TWD 80.000 y 200.000; las tasas de los segmentos son 29,91%, 20,85% y 14,59%. En prueba, Brier es 0,17272 para la tasa global y 0,16854 para los segmentos; la pérdida proxy esperada segmentada es TWD 100.868.690. Es una comparación descriptiva en una sola división aleatoria, sin estimación de incertidumbre ni evaluación fuera de tiempo; los cupos son posteriores a la aprobación.
