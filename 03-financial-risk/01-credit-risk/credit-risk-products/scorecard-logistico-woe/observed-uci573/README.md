# Benchmark externo: South German Credit UCI 573

Este experimento añade un segundo benchmark de clasificación de riesgo, independiente del conjunto UCI de tarjetas de Taiwán. Usa las categorías `bueno/malo` observadas en **1.000 créditos de Alemania, 1973–1975**: 700 buenos y 300 malos. Los malos fueron sobremuestreados deliberadamente. El resultado evalúa una muestra histórica seleccionada, **no estima la PD de una cartera poblacional**, una PD a 12 meses ni una provisión IFRS 9. El conjunto no contiene fechas individuales para validación temporal; tampoco informa recuperaciones, EAD o pérdidas monetarias.

## Fuente, archivo y condiciones

- Fuente: [UCI South German Credit](https://archive.ics.uci.edu/dataset/573/south+german+credit), DOI [10.24432/C5QG88](https://doi.org/10.24432/C5QG88), publicado en 2020; el conjunto corrige problemas de documentación del Statlog German original. UCI lo distribuye con licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), que exige atribución a los autores y al repositorio.
- Descarga oficial: [`south+german+credit+update.zip`](https://archive.ics.uci.edu/static/public/573/south%2Bgerman%2Bcredit%2Bupdate.zip), consultada el 18-nov-2026. El [ZIP original](data/south-german-credit-update.zip) se preserva íntegro y su SHA-256 es `0b40d40eb7321693d559e247a556f88a6cc8df8489c3cb2ae084db7592584551`. Contiene la tabla original, código R y tabla de códigos. El runner rechaza cualquier otro hash y verifica 1.000 filas y 300 etiquetas malas.
- La tabla no incluye identificadores directos, pero contiene edad, información combinada de estado civil/sexo y condición de trabajador extranjero. No se incorporan esas variables al modelo. Su exclusión no demuestra ausencia de sesgo o de variables indirectamente correlacionadas.
- Una fila representa un crédito histórico. La etiqueta `kredit=0` indica contrato no cumplido; `Y=1−kredit` representa la clase mala. El horizonte y la regla exacta de default no se identifican como un estándar bancario contemporáneo. El importe `hoehe` procede de una transformación monótona no documentada, por lo que **no se usa como exposición o pérdida**.

## Variables y modelo

Se usan `laufkont` (categoría de cuenta corriente), `moral` (historial de crédito), `sparkont` (ahorro), `beszeit` (duración de empleo), `rate` (categoría de cuota/ingreso) y `laufzeit` (duración contractual en meses). Los cinco códigos discretos usan codificación one-hot ajustada solo en entrenamiento; no se supone que la distancia entre códigos sea cardinal. La duración se estandariza con media y desviación de entrenamiento. Las categorías nuevas en prueba se codifican sin activar columnas conocidas. Estas variables son descriptivas; el archivo no acredita de manera verificable su disponibilidad exacta antes de cada decisión.

Con transformaciones `z(x)` y etiqueta `Y`, la regresión logística regularizada estima

\[
q(x)=\frac{1}{1+\exp[-(\beta_0+\beta^\top z(x))]},\qquad
\hat\beta=\arg\min_\beta\left[-\sum_i\{Y_i\log q_i+(1-Y_i)\log(1-q_i)\}+\lambda\|\beta\|_2^2\right].
\]

El estimador usa las opciones predeterminadas de `LogisticRegression` de scikit-learn (`C=1`); la ecuación muestra la forma de la penalización y no interpreta `λ` como una tasa económica. Frente a la tasa constante de entrenamiento se comparan Brier, pérdida logarítmica y AUC:

\[
\mathrm{Brier}=n^{-1}\sum_i(q_i-Y_i)^2,\quad
\mathrm{LogLoss}=-n^{-1}\sum_i[Y_i\log q_i+(1-Y_i)\log(1-q_i)],\quad
\mathrm{AUC}=P(q_{Y=1}>q_{Y=0})+\tfrac12P(q_{Y=1}=q_{Y=0}).
\]

Si se conociera una prevalencia poblacional `π` y se justificara que la distribución de predictores condicional a la clase se conserva entre muestra y población, la corrección de *prior probability shift* ajustaría los odds por `[π/(1−π)]/[s/(1−s)]`, con `s=0,30`. Aquí no se conoce `π` ni se ha verificado ese supuesto, por tanto no se aplica esa corrección ni se reporta una PD poblacional.

## Evaluación y límites

La división aleatoria 75/25 estratificada por etiqueta usa semilla 42, con 750 filas de entrenamiento y 250 de prueba; preprocesamiento y ajuste se realizan únicamente en entrenamiento. Esta división usa etiquetas para preservar proporciones y no representa una evaluación prospectiva. Hay **56 patrones de las seis variables compartidos** entre entrenamiento y prueba; no hay identificadores para determinar si son créditos de una misma persona. Esto limita la interpretación de independencia y la capacidad de detectar filtraciones por persona.

En prueba, el modelo obtiene Brier **0,1552** frente a **0,2100** para la tasa constante, AUC **0,8066** y log loss **0,4802** frente a **0,6109**. El incremento de Brier (baseline menos modelo) es **0,0548**, con intervalo bootstrap pareado condicional al modelo ajustado **[0,0319; 0,0745]** usando 1.000 remuestras de prueba. Este intervalo no captura reentrenamiento, selección de variables, dependencia ni cambios temporales. Las cinco agrupaciones de calibración de prueba y los parámetros del ejercicio están en [results.json](results.json); las agrupaciones se definen retrospectivamente y no son bandas de confianza.

La muestra es pequeña, histórica y seleccionada; no se usa para decidir originaciones ni demostrar equidad, calibración en Colombia o LGD/EAD. Para aplicación real se necesita un panel gobernado, datos disponibles al momento de decisión, definición y horizonte de incumplimiento, selección y censura documentadas, prevalencia representativa, separación temporal y por persona, además de revisión independiente.

## Reproducción

Con Python 3, pandas, numpy y scikit-learn:

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python3 03-financial-risk/01-credit-risk/credit-risk-products/scorecard-logistico-woe/observed-uci573/run.py
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python3 -m unittest discover -s 03-financial-risk/01-credit-risk/credit-risk-products/scorecard-logistico-woe/observed-uci573 -v
```
