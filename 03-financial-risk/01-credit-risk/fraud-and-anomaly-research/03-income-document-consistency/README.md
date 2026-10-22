# 03 · Consistencia de ingresos y evidencia documental

**S1 — diseño detallado.** Priorizar discrepancias que requieran corroboración: ingresos sobrerreportados, soportes reutilizados y contradicciones entre declaración y evidencia disponible. No confundir informalidad, estacionalidad o baja bancarización con fraude.

## Hipótesis y alcance

Hipótesis: modelar el ingreso esperable condicionado al tipo de actividad y la cobertura permite separar discrepancia económica de error de observación mejor que un umbral fijo. El resultado es una solicitud de aclaración documentada antes de aprobar o desembolsar.

Ejemplo ilustrativo: el ingreso mensual declarado excede de manera persistente el ingreso neto compatible con evidencia de varios períodos. Antes de elevar alerta hay que reconciliar frecuencia de pago, moneda, período, ingreso del hogar versus individual y ventas brutas versus ingreso disponible.

El modelo de capacidad de pago y el detector de engaño son productos separados. Puede haber capacidad insuficiente con información veraz, o declaración falsa en un cliente que paga.

## Contrato de evidencia y variables

| Evidencia | Construcción propuesta | Riesgo de interpretación |
|---|---|---|
| Ingreso declarado | Monto, periodicidad, base bruta/neta, fuente | No sumar bases incompatibles |
| Flujos observados | Entradas recurrentes verificadas, transferencias internas separadas | Créditos y traslados no son ingreso laboral |
| Actividad | Antigüedad, estacionalidad, recurrencia, dispersión | Nuevos negocios e informalidad tienen mayor incertidumbre |
| Documento | Consistencia aritmética, período, emisor, confianza de extracción | Errores OCR no prueban falsificación |
| Reutilización | Coincidencias de contenido/plantilla y soporte entre expedientes | Un formato común de nómina es legítimo |

Para empresas y microcrédito, estimar margen y retiro del propietario por separado; no usar ventas como salario. La pertenencia o autenticidad de una fuente debe corroborarse por canal independiente cuando sea posible. El diseño no incluye un detector forense de imágenes ni certifica autenticidad de un PDF.

## Modelos

**Baseline de conciliación:** reglas de sumas, períodos, identidad y titularidad; residuo robusto `r=(log(1+D)-median(log(1+I_peer)))/(1.4826*MAD+epsilon)`. `D` e `I` deben estar en la misma base monetaria y temporal. Exigir tamaño mínimo de pares y fallback jerárquico; el valor de `epsilon` y los grupos se fijan en entrenamiento.

**Modelo de ingreso:** regresión cuantílica de `log(1+I)` sobre variables de actividad, historial y cobertura, con pérdida pinball `rho_q(u)=u*(q-1[u<0])`. Estimar bandas para el ingreso corroborado, no para la declaración sospechosa. Un ingreso declarado sobre el cuantil superior es una discrepancia, no una probabilidad de fraude. Si la cobertura es parcial, ampliar incertidumbre o abstenerse.

**Challenger supervisado:** logit/boosting con residuos, contradicciones y resultados de verificaciones disponibles antes de la decisión. Objetivo: tergiversación confirmada, no mora. Una investigación realizada como consecuencia de la alerta inicial no puede entrar como predictor del score inicial. Puede alimentar un segundo score de investigación con nuevo corte y propósito explícito.

**Challenger documental:** distancia entre campos estructurados y patrones de consistencia; evaluar similitud de soportes como señal auxiliar. No usar Benford como sentencia de falsedad ni presentar OCR/LLM como perito. Cualquier extractor debe conservar confianza y trazabilidad a campo, con muestras sintéticas en público.

## Experimentos

1. Simular asalariados e independientes con ingresos variables, pagos quincenales, temporadas, gastos de negocio y períodos faltantes.
2. Inyectar sobrerreporte de varias intensidades y contradicciones documentales; incluir discrepancias legítimas difíciles y fraude con ingresos aparentemente normales.
3. Comparar regla de razón fija, residuo robusto, cuantiles y clasificador a igual capacidad. Separar la calidad del modelo de ingreso de la calidad de detección de fraude.
4. Evaluar sensibilidad a cobertura 1/3/6 meses, ruido OCR y transferencias internas no identificadas. No entrenar la imputación con test.
5. Validar por cohortes de actividad y cobertura; reservar ocupaciones o mecanismos de manipulación como prueba de extrapolación.

Métricas: cobertura y amplitud de bandas del ingreso corroborado; AP/precisión a `K` sobre etiquetas investigadas; fricción y solicitudes de soporte adicionales en clientes legítimos. La cobertura cuantílica agregada no garantiza cobertura por segmento ni bajo cambio de régimen.

## Refutación y entregables

El enfoque fracasa si detecta principalmente independientes, penaliza datos ausentes o deja de aportar cuando se corrige la definición bruta/neta. Un modelo muy preciso en datos simulados por su propia regla no acredita utilidad real.

Entregables propuestos: diccionario de conciliación; generador por tipo de ingreso; pipeline de variables al corte; modelos de cuantiles; notebook de cobertura, errores y ablaciones; formato de explicación con campos y períodos discrepantes. Pruebas: conversión de moneda coherente, anual/mensual/quincenal, faltantes distintos de cero y transferencias internas que no duplican ingreso. Ningún contrato real o soporte sensible se añade al repositorio.

La revisión humana debe poder concluir error de captura, diferencia explicable, evidencia insuficiente o tergiversación confirmada, conservando la explicación y su versión. Esa separación permitirá mejorar las variables sin fabricar etiquetas de fraude.

## Integración con motores y capas

Este especialista conserva estado S1. Su familia de señal se representa mediante una variable sintética en el [motor S2 de comparación y asignación](../loss-minimization-engine/README.md); ese experimento no implementa el detector especializado descrito arriba. Véanse [capas y contratos](../ARCHITECTURE.md) y [técnicas y función de pérdida](../MODEL_AND_LOSS_METHODS.md) para el desarrollo incremental y los criterios de comparación.

## Notebooks ejecutados: experimentos S2 acotados

- [Cuantiles, bandas y cobertura](notebooks/01-income-quantiles-and-coverage.ipynb)
- [Conciliación y robustez](notebooks/02-flow-reconciliation-and-robustness.ipynb)

Los dos experimentos incluyen 76 celdas y 7 figuras en conjunto, con derivaciones, diccionario de símbolos, ajuste de alternativas y casos de uso. Usan datos sintéticos y no completan el detector especializado de esta ficha. Las ecuaciones y los resultados se desarrollan dentro de las celdas; las preguntas abiertas conservan estado de investigación.

[Agenda de investigación y ecuaciones adicionales](EQUATIONS_AND_RESEARCH.md) · [Reproducción y evidencia](../notebook-lab/README.md).

[Catálogo de modelos y usos](../MODEL_CATALOG.md) · [Revisión integral y resultados](../REVIEW_AND_RESULTS.md).
