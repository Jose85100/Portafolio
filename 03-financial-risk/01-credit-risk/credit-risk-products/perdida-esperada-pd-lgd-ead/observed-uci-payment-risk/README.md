# Benchmark de impago del mes siguiente con UCI

Este ejercicio compara dos estimadores de la etiqueta observada `default payment next month`, con horizonte de **un mes**, y construye una sensibilidad de pérdida hipotética. El motor de doce meses del proyecto principal permanece separado: **no se extrapola esta tasa a 12 meses ni se valida una provisión o ECL**.

## Fuente y población

- I-Cheng Yeh (2009), [UCI Default of Credit Card Clients](https://doi.org/10.24432/C55S3H), licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Treinta mil titulares de tarjeta en Taiwán en 2005, no solicitantes de originación; resultados no transferibles a Colombia sin validación.
- XLS congelado reutilizado desde [observed-uci350](../../scorecard-logistico-woe/observed-uci350/README.md); descarga documentada del 12-nov-2026. SHA-256 `30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933`. El runner verifica hash, estructura, número de filas, ID único, finitud y etiqueta binaria. No hay actualización automática.
- `PAY_0`, `PAY_2` … `PAY_6`: estados codificados de pago reportados para septiembre hasta abril de 2005; se tratan como variables numéricas ordinales. Esta restricción funcional es una simplificación, pues los códigos negativos tienen significado específico. Son datos posteriores a la concesión y no se atribuye su disponibilidad al momento de originación.
- `default payment next month`: etiqueta binaria observada del dataset, no necesariamente equivalente a la definición contractual o prudencial de default de una entidad colombiana.
- `LIMIT_BAL`: cupo autorizado en nuevos dólares taiwaneses (TWD). Es un **proxy de escala de exposición**, no saldo utilizado ni EAD. LGD es 45% hipotética, sin datos de recuperaciones. El proxy `etiqueta × cupo × 0,45` no es pérdida realizada.

## Diseño

Partición estratificada aleatoria 75/25, semilla 42: 22.500 entrenamiento y 7.500 prueba. El baseline es la tasa de entrenamiento, constante en prueba. El modelo es regresión logística con los seis estados de pago y estandarización aprendida solo en entrenamiento. No se utilizan como predictores cupo, identificador, demografía, montos de facturación ni información de prueba. Se comparan Brier y log loss frente al baseline, y AUC del modelo. Se muestran grupos de calibración basados en cuantiles de las predicciones de prueba con `duplicates='drop'`: predicciones repetidas reducen el número de grupos a siete, sin partir empates artificialmente. Los intervalos de cuantiles no son intervalos de confianza de calibración.

El bootstrap pareado de 500 remuestras de prueba para la diferencia `Brier baseline − Brier modelo` conserva el ajuste ya entrenado. El intervalo percentil refleja variación de la muestra de prueba **condicional al modelo**; no incluye reentrenamiento, selección de variables ni incertidumbre por cambio temporal. La estratificación utiliza el target para asignar la muestra y estabiliza su prevalencia; no representa un despliegue prospectivo.

## Resultado del snapshot

En la prueba retenida, prevalencia 22,12%; Brier baseline **0,17227**, Brier modelo **0,14726**, AUC **0,69888**. La mejora pareada de Brier es 0,02501, con intervalo bootstrap condicional [0,02167; 0,02831]. La calibración no es uniforme: por ejemplo, el grupo inferior tiene predicción media 4,94% y frecuencia observada 15,15%, y el mayor grupo tiene 20,01% frente a 11,41%. Por tanto, una mejora promedio no valida la calibración por segmento.

Con LGD 45% y cupo como exposición ficticia, la suma de `PD × LGD × cupo` es TWD 107.713.020; el mismo proxy ponderado por etiqueta observada suma TWD 100.191.456. La comparación no valida pérdida esperada monetaria, ya que cupo y LGD no son EAD ni pérdidas observadas. Resultados completos y grupos en [results.json](results.json).

## Ejecución

Desde la raíz del repositorio, Python 3 con pandas, numpy, scikit-learn y xlrd (también incluidos en los requisitos de investigación del repositorio):

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python3 03-financial-risk/01-credit-risk/credit-risk-products/perdida-esperada-pd-lgd-ead/observed-uci-payment-risk/run.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python3 -m unittest discover -s 03-financial-risk/01-credit-risk/credit-risk-products/perdida-esperada-pd-lgd-ead/observed-uci-payment-risk -v
```

Los controles cubren integridad de entradas, conservación de observaciones, reproducibilidad, separación de cupo y predictor, y rechazo de muestras con una sola clase. Una validación aplicable exigiría panel de operaciones y recuperaciones gobernado, definición y horizonte de default, exposiciones efectivas, exclusiones y censura, prueba fuera de tiempo y revisión independiente. No se infieren cosechas, migraciones ni causas de impago de este corte.
