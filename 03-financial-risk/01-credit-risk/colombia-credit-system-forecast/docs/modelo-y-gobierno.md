# Especificación técnica y gobierno

## 1. Decisión, población y unidad

El objetivo es investigar monitoreo de cartera de los establecimientos de crédito sin IOE, no resolver decisiones sobre personas o entidades. Unidad: mes de corte nacional. Objetivo: porcentaje agregado de saldo vencido sobre cartera bruta publicado en el archivo NIIF. No incluye todo el sistema financiero ni identifica riesgo individual, probabilidad de incumplimiento, severidad de pérdida o pérdidas esperadas IFRS 9. Una reducción del cociente puede deberse tanto a cambios en numerador como denominador, castigos, ventas u otros movimientos: el modelo no identifica su causa.

## 2. Trazabilidad y comprobaciones

Fuentes y consultas están en `src/download.py` y `data/raw/manifest.json`. El XLSX se lee por rótulos en la hoja de mora, sin sumar filas de diferentes secciones. Cifras de saldo en millones de pesos corrientes; razones como fracción antes de convertirlas a puntos porcentuales. Se validan meses únicos y continuos, columnas y nombres esperados, denominadores positivos, valores finitos y saldos no negativos. Se comprueba `vigente + vencido = bruto` con tolerancia relativa de 1e−7 y la razón calculada contra la publicada con tolerancia de 1e−6 en proporción. Son tolerancias técnicas de reconciliación, no límites regulatorios.

TRM: se verifican moneda, positividad y vigencias únicas, no solapadas y que cubran cada fin de mes. Los hashes protegen la integridad de las instantáneas, no prueban su corrección ni disponibilidad en una fecha pasada. Revisiones, cambios de composición, fusiones y diferencias en definiciones o métodos pueden afectar la serie.

## 3. Variables y horizonte

En una predicción retrospectiva de t, suponemos cierre operativo al final de t−1 e información financiera disponible solo hasta t−2. Entrenamiento y variables respetan ese corte: ICV total en t−2, t−3, t−4, t−6, t−12 y t−14; ICV de cada modalidad en t−2; TRM de cierre en t−2 y variación interanual; crecimiento nominal interanual de la cartera bruta en t−2; y mes cíclico. El crecimiento nominal incluye inflación. El uso de tasas rezagadas no demuestra causalidad ni permite concluir transmisión monetaria.

El supuesto de publicación debe verificarse con registros históricos por fuente; el archivo actual puede tener retransmisiones. Si un valor de t−2 no estaba publicado en la fecha de decisión, la evaluación es optimista. No se incorporan PIB, desempleo ni inflación por falta de una integración con fechas reales de divulgación y revisiones. La TRM es un proxy económico limitado, no una medición de actividad real.

## 4. Modelos y entrenamiento

Referencia de persistencia: `ŷ_t = ICV_(t−2)`. Tendencia: `ŷ_t = ICV_(t−2) + ICV_(t−2) − ICV_(t−3)`. Ridge y boosting estiman el cambio respecto a ICV_(t−2), con parámetros prefijados. Ridge utiliza normalización estimada únicamente con los datos de entrenamiento. Boosting no utiliza parada temprana con partición aleatoria. No se han impuesto límites físicos a predicciones; eso es una brecha antes de cualquier uso.

La ventana crece mensualmente y solo incluye etiquetas hasta t−2. 2020–2022 aporta 36 pronósticos de desarrollo para elegir por MAE; 2023–septiembre 2026 aporta 45 pronósticos posteriores. Cada periodo incluye situaciones económicas distintas, pero la muestra es corta y se ha observado; no aporta validación independiente futura ni comparación con pronósticos oficiales. No hay ajuste de hiperparámetros sobre evaluación posterior.

## 5. Métricas, intervalos y acciones pendientes

MAE y RMSE están expresados en puntos porcentuales del indicador, no en porcentaje relativo. Sesgo = predicción − observado. La banda usa el percentil empírico con objetivo de 90 % de errores absolutos del modelo elegido en desarrollo; esa misma muestra participó en la selección. Dependencia temporal y cambio de distribución impiden prometer cobertura. Informar cobertura observada y ancho, también por régimen y modalidad cuando existan muestras suficientes.

Antes de decisiones: reconstruir vintages y calendarios de publicación; probar periodos nuevos con diseño congelado; incorporar series macro oficiales disponibles a tiempo, y comparar contra pronósticos oficiales; estudiar rupturas, fusiones, castigos y denominadores; probar calibración, estabilidad, límites físicos, seguridad, pruebas independientes y monitoreo de deterioro. No generar alertas regulatorias ni evaluaciones de clientes con este prototipo.
