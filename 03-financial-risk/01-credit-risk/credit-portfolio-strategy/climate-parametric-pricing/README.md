# Tarifación paramétrica climática bajo no estacionariedad

**Madurez: prototipo reproducible con DGP sintético; no constituye tarifa comercial ni recomendación actuarial.**

## Pregunta

¿Cómo tarifar una cobertura paramétrica climática cuando la distribución del índice cambia en el tiempo, y cómo hacer visible el tradeoff entre suficiencia actuarial, riesgo de base, volatilidad de tarifa y asequibilidad? La aplicación de referencia es sequía agrícola o interrupción de pequeña empresa expuesta al clima. El esquema puede adaptarse a calor, lluvia extrema, niveles de embalse o logística, redefiniendo índice, pérdida y contrato.

## Contrato e hipótesis

(W_{g,t}): precipitación acumulada (mm); (K_g): trigger; (A_g<K_g): agotamiento; (L_g): límite. Para sequía:
[
q(W;K,A)=\min\{1,\max[0,(K-W)/(K-A)]\}, qquad Z=Lq.
]
El pago es función del índice observado y no de la indemnización de daño. Para pérdida económica (Y), el residuo de base es (B=Y-Z): shortfall (B^+=\max(B,0)) y pago excedente (B^-=\max(-B,0)).

Comparamos burn analysis estacionario, pesos por recencia y una distribución condicional a tendencia/escenario. La prima pura es (E[Z]); una carga de cola es (\lambda(TVaR_\alpha(Z)-E[Z])), con gastos, reaseguro y capital expuestos como componentes adicionales sin doble conteo. El análisis no trata escenarios de cambio climático como probabilidades calibradas si no existe una base defendible para hacerlo.

Hipótesis refutables: (H1) modelos condicionales reducen error de prima OOS bajo deriva, pero no necesariamente en DGP estacionario; (H2) elegir índice/trigger por pérdida reduce shortfall fuera de muestra solo si índice y daño conservan relación estable; (H3) carga de cola aumenta suficiencia en estrés y puede reducir asequibilidad/uptake. Se reportan resultados por replicación y sensibilidad, no solo una trayectoria favorable.

## Modelos y diagnóstico

1. **Burn analysis:** promedio histórico de pagos, benchmark transparente; vulnerable a drift, exposiciones cambiantes y ventanas con pocos eventos.
2. **Tendencia condicional:** media/escala de índice varía con tiempo y covariables; la extrapolación estadística no equivale a un escenario físico de clima.
3. **Régimen/covariables:** distribución condicionada a régimen observable o latente; comparar con splines/GAM y modelos de extremos cuando el peligro sea cola.
4. **No estacionariedad:** ventana móvil, ponderación exponencial (w_t\propto e^{-\gamma(T-t)}), cambio estructural y escenarios múltiples.
5. **Riesgo de base:** correlación índice-pérdida, shortfall, pago sin daño, reducción de varianza de pérdida y sensibilidad al punto/estación del índice.
6. **Cartera:** dependencia espacial de eventos, acumulación, VaR/TVaR, reaseguro y concentración. Precio individual no garantiza solvencia agregada.
7. **Asequibilidad:** mostrar tasa de exposición que puede comprar a cada precio y brecha explícita. Subsidio/tope no reduce el costo técnico: identifica quién financia la diferencia.

## Experimento del notebook

DGP controlado con tendencia, cambio de media, escala variable, daño dependiente del déficit climático y vulnerabilidad idiosincrática. Separación temporal train/test; umbrales se seleccionan únicamente en train. Experimentos: payout y propiedades contractuales; prima burn vs distribución condicional; pesos exponenciales y tamaño efectivo; riesgo de base; optimización simple de trigger; carga TVaR; curva sintética de asequibilidad; réplicas estacionarias y con deriva. Se guardan seis figuras y resumen reproducible. Todas las magnitudes son sintéticas.

## Relevancia para crédito

Una póliza indexada puede mitigar faltantes de flujo de caja en un productor/negocio expuesto. No sustituye PD, LGD o EAD: la recuperación crediticia solo incorpora el pago si es jurídicamente asignable, oportuno, verificable y cobrable. Se debe estimar conjuntamente evento climático, daño, mora y pago; publicar escenario bruto y mitigado por separado. El cuaderno no prueba que el seguro reduzca incumplimiento.

## Arquitectura de referencia

Fuente meteorológica y dato satelital → calidad/homogeneidad y metadatos → índice contractual versionado → simulación condicional por escenario → motor de pérdida y basis risk → tarificación técnica → límites de acumulación/capital/reaseguro → explicación/cotización → observación del índice, liquidación y monitoreo de deriva. Registrar revisiones, faltantes, latencia, cambios de sensor, punto geográfico, regla de disputa y fallback.

## Criterios de avance y falsación

- Contrastar tarifa contra benchmark en validación temporal y espacial fuera de muestra.
- Evaluar calibración del trigger, error de prima, incertidumbre, estabilidad y error de cola.
- Refutar utilidad si la cobertura no mejora el riesgo económico neto, si el basis risk es excesivo o si el contrato es menos robusto que una alternativa de ahorro/crédito contingente.
- Requerir pérdidas económicas etiquetadas, series climáticas con trazabilidad, escenarios físicos, información de exposición/adaptación y revisión actuarial/legal antes de calibración real.
- Para Colombia: escoger región/actividad y revisar disponibilidad/calidad de estaciones y marco aplicable; ningún resultado sintético se extrapola a tarifas o decisiones reales.

## Referencias iniciales

- Daron, J. D. & Stainforth, D. A. (2014), “Assessing pricing assumptions for weather index insurance in a changing climate”, *Climate Risk Management* 1, 76–91, DOI: 10.1016/j.crm.2014.01.001.
- Ingels et al. (2024), “The state of the art and future of climate risk insurance modeling”, *Annals of the New York Academy of Sciences*, DOI: 10.1111/nyas.15255.
- Steinmann et al. (2023), “A generalized framework for designing open-source natural hazard parametric insurance”, *Environment Systems and Decisions* 43, 555–568, DOI: 10.1007/s10669-023-09934-x.
- Figueiredo et al. (2018), “A Probabilistic Paradigm for the Parametric Insurance of Natural Hazards”, *Risk Analysis* 38(11), 2400–2414.
- Zhang, Tan & Weng (2019), “Index Insurance Design”, *ASTIN Bulletin* 49(2), 491–523.
- Turvey et al. (2021), “Optimal drought index for designing weather index insurance”, *European Review of Agricultural Economics* 48(3), 573–599.

La revisión de Ingels et al. declara una búsqueda en Scopus y resume brechas en modelos prospectivos, no estacionariedad, asequibilidad, multi-riesgo y aplicaciones geográficas. No afirmamos indexación bibliométrica independiente de cada referencia.

## Reproducibilidad

Instalar `requirements.txt` y ejecutar `notebook.ipynb`. `src/pricing.py` implementa payout y principios de prima acotados para pruebas unitarias. Semilla fija en el notebook. DGP sintético, sin PII ni datos de asegurados.
