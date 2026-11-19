# Modelo de ranking, capacidad y umbral fijado

Este ejercicio usa el mismo [snapshot ULB y contrato de datos](README.md), con 284.807 transacciones de dos días. Continúa la separación cronológica 60/20/20 y conserva, por construcción, transacciones con el mismo `Time` en un bloque. La transformación de los componentes `V1`–`V28` por el proveedor, la falta de fecha de adjudicación de etiquetas y la posible dependencia entre transacciones siguen limitando la interpretación temporal. Este es fraude de pagos, no de originación.

## Modelo y variables

Sea `y_i ∈ {0,1}` la etiqueta provista, `x_i` los 28 componentes anonimizados más `log(1+Amount_i)`, y `z_ij=(x_ij−μ_j)/σ_j` usando medias y escalas ajustadas únicamente en entrenamiento. Para parámetros `β`, la logística calcula

\[
s_i=\sigma(\beta_0+z_i^\top\beta)=\frac{1}{1+\exp[-(\beta_0+z_i^\top\beta)]}.
\]

El estimador de `sklearn` minimiza pérdida logística binaria con regularización L2 según `LogisticRegression(solver="liblinear", C=1)` y sus convenciones de implementación. Las ponderaciones y el escalador se congelan antes de validación y prueba; no se ajustan con las etiquetas del bloque de prueba. Los scores se utilizan para **ordenar**, sin asegurar calibración de probabilidad. Como referencia sencilla, se ordena por `Amount`; no equivale a la política actual de un banco.

## Curva retrospectiva de capacidad

Para un bloque con `n` transacciones y presupuesto relativo `c`, se toma `k=ceil(c n)` y se seleccionan los `k` mayores scores (los empates respetan el orden original). Si `A_k` es la selección:

\[
TP_k=\sum_{i\in A_k}y_i,\quad
\mathrm{precisión}_k=\frac{TP_k}{k},\quad
\mathrm{recobro}_k=\frac{TP_k}{\sum_i y_i}.
\]

El recobro queda indefinido si no hay positivos. Los cinco niveles 0,1%, 0,25%, 0,5%, 1% y 2% fueron definidos antes de consultar el bloque de prueba. Ordenar todo el bloque exige observar todos sus scores: **la curva es retrospectiva**, no un sistema en línea ni una agenda diaria real. `Average precision` del ejercicio original resume precisión según cambios en recobro; no debe confundirse con precisión a un cupo determinado.

Con 56.962 transacciones y 75 fraudes etiquetados en prueba:

| Capacidad | Alertas | TP logística | Precisión logística | Recobro logística | TP regla de monto |
|---:|---:|---:|---:|---:|---:|
| 0,10% | 57 | 41 | 71,93% | 54,67% | 0 |
| 0,25% | 143 | 60 | 41,96% | 80,00% | 0 |
| 0,50% | 285 | 63 | 22,11% | 84,00% | 1 |
| 1,00% | 570 | 64 | 11,23% | 85,33% | 3 |
| 2,00% | 1.140 | 65 | 5,70% | 86,67% | 4 |

La comparación se refiere a este conjunto y al baseline elegido. La reducción de precisión al ampliar el cupo no incluye costos de revisión ni pérdida evitada; con 75 eventos y dependencia desconocida no se justifican garantías de efectividad.

## Sensibilidad con umbral congelado

Para evitar seleccionar el corte usando la distribución completa de prueba, ordenamos los scores **solo de validación** y fijamos `τ` como el score del rango `ceil(0,01 n_validación)`. Luego se alerta si `s_i ≥ τ` en prueba. Los empates en `τ` pueden generar más del 1%; si cambia la distribución de scores, tampoco existe garantía de mantener el cupo en prueba. `FN = Σy − TP` y `FP = alertas − TP`. Precisión es indefinida cuando no hay alertas.

La logística produjo `τ≈0,007792` (escala de score, no probabilidad calibrada): 570 alertas en validación; en prueba, 530 alertas, 64 TP, 466 FP y 11 FN. La regla de monto, con umbral 1.128,2 de la unidad de origen, produjo 416 alertas, 1 TP, 415 FP y 74 FN. Estos resultados **no igualan capacidad en prueba**, por eso la comparación justa a presupuesto fijo sigue siendo la curva retrospectiva. El corte congelado ilustra sensibilidad al cambio de distribución, sin simular disponibilidad real de etiquetas ni interacción con el investigador.

## Reproducción y controles

Con el CSV externo y dependencias de [README](README.md):

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 03-financial-risk/01-credit-risk/fraud-and-anomaly-research/observed-card-fraud-benchmark/capacity_analysis.py --input /ruta/privada/creditcard.csv
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python3 -m unittest discover -s 03-financial-risk/01-credit-risk/fraud-and-anomaly-research/observed-card-fraud-benchmark -v
```

[Resultados agregados](capacity_results.json). Los tests contrastan cálculo manual, empates, ausencia de alertas o positivos, entradas no finitas y que las etiquetas de prueba no alteran el umbral de validación. Ordenar predicciones casi empatadas y el ajuste numérico pueden variar entre versiones de bibliotecas/BLAS. El hash identifica el CSV utilizado pero no acredita la cadena original de custodia del proveedor. Es necesario disponer de decisiones, fechas de resultado, costos, entidades y un periodo operativo independiente antes de evaluar una política real.
