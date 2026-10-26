# 03-financial-risk: 6 ideas de vanguardia por carpeta

**Alcance.** Repositorio `Jose85100/Portafolio`, carpeta `03-financial-risk`, 7 áreas. Revisé la estructura y los README de cada área. No auditamos el código de cada subcarpeta, así que cada idea se contrasta solo con lo que el README describe. Antes de implementar, conviene confirmar que no duplica un proyecto existente.

**Convención de verificación.**
- **[V]**: respaldada por una fuente encontrada en esta búsqueda (se indica cuál).
- **[C]**: literatura clásica o estándar conocida; citar antes de usar en producción.

Cada idea incluye: hipótesis, formulación mínima, validación y refutación (el riesgo que el enfoque podría ocultar).

---

## 01 · Riesgo de crédito (`01-credit-risk`)

### 1.1 Intervalos de ECL con cobertura garantizada (conformal survival)
- **Hipótesis.** Los intervalos de pérdida lifetime pueden tener cobertura finita garantizada sin supuestos distribucionales fuertes.
- **Método.** Análisis de supervivencia conformal para datos censurados a la derecha: dado un nivel \(\alpha\), construir \([L_{\text{low}}(x), L_{\text{up}}(x)]\) tal que \(P(T \in C(x)) \ge 1-\alpha\) bajo intercambiabilidad. Usar ponderación por probabilidad inversa de censura para el caso de censura general.
- **Validación.** Cobertura empírica por estrato (no solo marginal) y ancho medio del intervalo. Comparar con el intervalo de Kaplan-Meier sin condicionar.
- **Refutación.** La cobertura marginal no implica cobertura condicional; con cambio de covariables (originación nueva vs. cartera madura) la garantía se degrada sin ponderación por *covariate shift* (Tibshirani et al., 2019) [C].
- **Fuente.** Davidov et al., *Conformalized Survival Analysis for General Right-Censored Data*, ICLR 2025 [V].

### 1.2 Alerta temprana de quiebres en cosechas con BOCPD
- **Hipótesis.** Un cambio en la tasa de mora de una cosecha se detecta antes que el DPD30 por encima de su umbral.
- **Método.** Detección de puntos de cambio bayesiana en línea (Adams & MacKay, 2007) sobre la serie de mora por cosecha, con probabilidad posterior de *run length*.
- **Validación.** Retardo medio de detección vs. falsas alarmas (ARL₀ y ARL₁) sobre datos sintéticos con cambios conocidos; luego sobre histórico.
- **Refutación.** Con poca historia por cosecha, el prior domina; la hazard constante es inadecuada si hay estacionalidad. Requiere calibrar la hazard por ciclo económico.
- **Fuente.** [C].

### 1.3 PD con procesos de Lévy-Ornstein-Uhlenbeck y saltos
- **Hipótesis.** Los saltos de calidad crediticia (choques macro abruptos) explican mejor la PD que un proceso gaussiano como el de Vasicek.
- **Método.** Modelo de PD como función de un factor latente \(X_t\) con dinámica OU conducida por un proceso de Lévy (saltos), con calibración por máxima verosimilitud aproximada.
- **Validación.** Comparar Vasicek y LOU-Lévy con BIC, prueba de calibración por cosecha y error de estimación de cola en el percentil 99,5 de pérdida.
- **Refutación.** Más parámetros implican mayor riesgo de sobreajuste; los saltos pueden absorber errores de especificación del factor macro.
- **Fuente.** arXiv:2309.12384 [V].

### 1.4 Copulas con dependencia de cola alternativa y robustez por Wasserstein
- **Hipótesis.** La copula gaussiana subestima la pérdida conjunta de cola; una copula t o de Clayton con dependencia de cola superior da una pérdida de cola mayor.
- **Método.** Comparar cópulas gaussiana, t y Clayton para la cartera. Robustez mediante optimización distribucionalmente robusta sobre una bola de Wasserstein alrededor de la cópula estimada (Esfahani & Kuhn, 2018) [C].
- **Validación.** Pérdida al 99,9 % y dependencia de cola empírica (\(\lambda_U\)) con intervalos bootstrap. Prueba de la sensibilidad de la asignación de capital.
- **Refutación.** La dependencia de cola se estima con muy pocos eventos extremos; el intervalo puede ser tan amplio que no distinga las cópulas.
- **Fuente.** [C].

### 1.5 Matriz de transición semi-Markov con tiempo de permanencia
- **Hipótesis.** Los roll rates son semi-Markov: la probabilidad de pasar de estado depende de cuánto tiempo se lleva en él, no solo del estado actual.
- **Método.** Estimador de Aalen-Johansen para transiciones con tiempo de permanencia; comparar con la cadena de Markov en tiempo continuo.
- **Validación.** Prueba de Markov (por ejemplo, test de Aalen-type sobre tiempos de permanencia) y error de predicción de saldos por estado a 12 meses.
- **Refutación.** Con datos sintéticos, cualquier diferencia es un artefacto del generador si no se controla la semilla y el régimen.
- **Fuente.** [C].

### 1.6 Auditoría de monotonía y equidad en scorecards con modelos de gradiente
- **Hipótesis.** Un modelo de gradiente con restricciones de monotonía iguala el Gini de la regresión logística sin violar la lógica de negocio ni introducir impacto dispar.
- **Método.** Gradient boosting con restricciones monótonas por variable. Medir impacto dispar entre grupos protegidos sustitutos, con análisis de causalidad donde sea posible.
- **Validación.** Gini, calibración por decil y prueba de la diferencia de Gini (DeLong). Métricas de equidad: impacto dispar y tasas de error por grupo.
- **Refutación.** La equidad depende de la definición (paridad demográfica, igualdad de oportunidades); ninguna es neutral. Las variables sustitutas pueden reconstruir atributos excluidos.
- **Fuente.** [C].

---

## 02 · Riesgo de mercado y de modelo (`02-market-and-model-risk`)

### 2.1 Backtesting de Expected Shortfall con pruebas Z
- **Hipótesis.** El ES puede validarse con pruebas de magnitud (no solo de conteo de excepciones), con potencia suficiente en muestras de 250 días.
- **Método.** Pruebas Z de Acerbi & Székely (2014) sobre la distribución de pérdidas de excepción, junto con la prueba de Kupiec para VaR.
- **Validación.** Potencia y tamaño (tipo I) por simulación Monte Carlo con colas t y sesgo de ES.
- **Refutación.** Con colas pesadas y ventana corta, la potencia de cualquier prueba de ES es baja. Un resultado "pasa" puede ser solo falta de potencia.
- **Fuente.** [C]; relevante para el marco FRTB (cambio a ES) [V, búsqueda sobre FRTB].

### 2.2 Validación de modelos de IA generativa bajo SR 26-2
- **Hipótesis.** Un marco de validación con desafiante (*challenger*), monitoreo de deriva y pruebas de robustez cubre los riesgos de un LLM usado en decisiones de riesgo.
- **Método.** Matriz de riesgos del LLM: alucinación, deriva de datos y prompts, dependencia de proveedor. Pruebas: consistencia entre ejecuciones, pruebas adversarias y comparación contra un modelo estadístico de referencia.
- **Validación.** Tasa de error sobre un conjunto de preguntas con respuesta verificada y estabilidad de la salida ante perturbaciones menores del prompt.
- **Refutación.** La no determinación de los LLM hace difícil reproducir resultados. Una buena métrica de evaluación de un LLM puede no predecir su error en producción.
- **Fuente.** Federal Reserve, carta SR 26-2, 17-abr-2026, que reemplaza SR 11-7 [V, sitio oficial de la Reserva Federal]. Aplica a bancos de más de 30 000 millones de dólares; la aplicabilidad a una entidad colombiana requiere análisis regulatorio propio.

### 2.3 Escenarios sintéticos con modelos generativos evaluados por hechos estilizados
- **Hipótesis.** Un generador de series (GAN temporal o modelo de difusión) produce escenarios de estrés que respetan los hechos estilizados (agrupamiento de volatilidad, colas pesadas, ausencia de autocorrelación en retornos).
- **Método.** Entrenar TimeGAN (Yoon et al., 2019) o un modelo de difusión sobre retornos; evaluar con ACF de \(|r_t|\), índice de cola de Hill y pruebas de distribución.
- **Validación.** Distancia de los hechos estilizados frente a la historia real y prueba de cobertura del VaR generado.
- **Refutación.** Colapso de modos: el generador puede replicar la cola histórica pero no los escenarios nuevos. Un buen ajuste histórico no garantiza que el escenario de estrés sea plausible.
- **Fuente.** [C].

### 2.4 VaR con cobertura adaptativa (conformal) bajo no estacionariedad
- **Hipótesis.** El VaR con cobertura adaptativa mantiene la tasa de excepciones objetivo aun con cambios de régimen.
- **Método.** Inferencia conformal adaptativa (Gibbs & Candès, 2021), que actualiza el nivel de error \(\alpha_t\) según la excepción observada.
- **Validación.** Tasa de excepciones frente a \(\alpha\) nominal, cobertura condicional por régimen y número de excepciones consecutivas.
- **Refutación.** La garantía asintótica no es válida en muestras cortas; el ajuste puede volverse inestable tras un choque grande.
- **Fuente.** [C].

### 2.5 Riesgo de modelo como prima sobre familias GARCH
- **Hipótesis.** La diferencia de VaR entre GARCH, EGARCH y GJR-GARCH es una medida cuantificable del riesgo de modelo, y debe reportarse junto al VaR.
- **Método.** Calcular VaR y ES con cada especificación; medir la dispersión (rango o desviación) y la prima de riesgo de modelo como el máximo de la diferencia.
- **Validación.** Sobre datos sintéticos con la especificación conocida, verificar que la métrica identifica el modelo verdadero.
- **Refutación.** Un rango pequeño puede reflejar que todas las especificaciones comparten el mismo error (por ejemplo, la distribución de innovaciones).
- **Fuente.** [C].

### 2.6 Validación de PD con desafiante de gradiente y prueba de estabilidad de Gini
- **Hipótesis.** La diferencia de Gini entre campeón (logística) y desafiante (gradiente) es estadísticamente significativa solo en algunas cosechas.
- **Método.** Bootstrap por cosecha del diferencial de Gini; prueba de estabilidad de PSI por ventana móvil.
- **Validación.** Intervalos de confianza del diferencial y consistencia entre ventanas.
- **Refutación.** Los bootstrap sobre datos con dependencia temporal subestiman la varianza; se requiere bloqueo temporal (*block bootstrap*).
- **Fuente.** [C].

---

## 03 · Liquidez y riesgo de mercado (`03-market-liquidity-research`)

### 3.1 Regiones de insolvencia con liquidez y crédito acoplados (HJB)
- **Hipótesis.** La insolvencia ocurre en regiones no lineales del espacio (liquidez, crédito), y el efecto conjunto es mayor que la suma de los efectos individuales.
- **Método.** Control óptimo estocástico con ecuación de Hamilton-Jacobi-Bellman y un modelo acoplado de liquidez (LCR/NSFR de Basilea III) y crédito.
- **Validación.** Trayectorias de la región de insolvencia frente a combinaciones de estrés; sensibilidad a parámetros; comparación con pruebas de estrés estándar.
- **Refutación.** El resultado de umbral depende de la calibración; el artículo original usa datos bancarios de otro país, así que la transferencia a Colombia no es automática.
- **Fuente.** arXiv:2607.17381, "Determining Insolvency Regions in Banks" [V].

### 3.2 Liquidity-adjusted VaR con impacto de mercado
- **Hipótesis.** El VaR debe ajustarse por el costo de salir de la posición, que depende del tamaño y del horizonte de liquidación.
- **Método.** Costo de liquidación con impacto temporal y permanente tipo Almgren-Chriss (2000) [C]; VaR ajustado con horizonte igual al tiempo de liquidación.
- **Validación.** Sensibilidad del LVaR al tamaño de la posición y a la tasa de liquidación.
- **Refutación.** Los parámetros de impacto se estiman con datos de ejecución que pueden no existir en el mercado objetivo.
- **Fuente.** [C] (Bangia et al., 1999, es el antecedente clásico de LVaR).

### 3.3 Contagio de *margin calls* con procesos de Hawkes
- **Hipótesis.** Las ventas forzadas se auto-excitan: una venta eleva la probabilidad de la siguiente en un período corto.
- **Método.** Proceso de Hawkes multivariado para eventos de llamadas de margen, con intensidad \(\lambda_i(t)=\mu_i+\sum_j \int g_{ij}(t-s)\,dN_j(s)\). Calibración por máxima verosimilitud.
- **Validación.** Prueba de bondad de ajuste (residuos de Ogata) y predicción de la cola de la intensidad.
- **Refutación.** Un Hawkes con núcleo exponencial puede confundir autoexcitación con ciclos comunes o estacionalidad no modelada.
- **Fuente.** [C].

### 3.4 Resiliencia del libro de órdenes como medida de liquidez
- **Hipótesis.** La resiliencia (velocidad de recuperación de la profundidad del libro tras una orden grande) es un predictor de liquidez más robusto que el diferencial.
- **Método.** Estimar la resiliencia con el modelo de decaimiento del impacto de orden de Bouchaud; compararla con la profundidad y el diferencial.
- **Validación.** Correlación con el costo de ejecución realizado en datos de libro de órdenes.
- **Refutación.** La resiliencia en mercados poco líquidos (como muchos de Latinoamérica) puede no ser estable en el tiempo.
- **Fuente.** arXiv:2607.16970, "Herding and Liquidity in Order-Book Markets. II" [V, como lectura de punto de partida].

### 3.5 CVaR con optimización distribucionalmente robusta y costos de liquidación
- **Hipótesis.** Optimizar el CVaR con el conjunto de incertidumbre de Wasserstein es más estable que el CVaR con muestra histórica cuando hay pocas observaciones de cola.
- **Método.** Programa DRO: \(\min_w \sup_{Q:\,W_p(Q,\hat P)\le\varepsilon}\mathrm{CVaR}_\alpha^Q(w^\top R - c(w))\). Con costos lineales por tramos.
- **Validación.** Estabilidad de los pesos frente a remuestreo y pérdida fuera de muestra.
- **Refutación.** Un \(\varepsilon\) mal calibrado puede volver la solución excesivamente conservadora.
- **Fuente.** Rockafellar & Uryasev (2000) para CVaR [C]; Esfahani & Kuhn (2018) para Wasserstein [C].

### 3.6 Alerta temprana de estrés de liquidez con causalidad
- **Hipótesis.** Un modelo de aprendizaje automático con interpretación causal identifica mejor los valles de mercado que la correlación simple.
- **Método.** Aprendizaje automático con validación por tiempos de rezago y estimación causal de efectos (por ejemplo, doble aprendizaje automático, Chernozhukov et al., 2018) [C].
- **Validación.** Predicción fuera de muestra con ventanas temporales y pruebas de robustez a la omisión de variables.
- **Refutación.** La causalidad en series temporales es difícil de identificar; los efectos estimados pueden ser espurios si hay variables comunes no observadas.
- **Fuente.** arXiv:2509.05922, "Predicting Market Troughs: A Machine Learning Approach with Causal Interpretation" [V].

---

## 04 · Investigación avanzada (`04-advanced-research`)

Estas ideas complementan los siete proyectos existentes sin duplicarlos.

### 4.1 Efectos heterogéneos de la política de aprobación con bosques causales
- **Hipótesis.** El efecto causal de aprobar un crédito varía por segmento, y un bosque causal lo estima con mejor precisión que un modelo de respuesta.
- **Método.** Bosques causales (Wager & Athey, 2018) [C] con doble aprendizaje automático para el efecto de tratamiento; restricción de equidad en la asignación.
- **Validación.** Curva de calibración del efecto (*calibration of CATE*) y evaluación de la política con estimador doblemente robusto.
- **Refutación.** Los datos de aprobación son observacionales; la identificación depende de la ignorabilidad, que no se puede probar.
- **Fuente.** Relacionado con la literatura de aprendizaje automático causal aplicado a límites de crédito (arXiv:2508.02183) [V].

### 4.2 Detección de regímenes en el gemelo digital con cambio de estado oculto
- **Hipótesis.** Un modelo de Markov oculto con dos o tres regímenes detecta la transición de estabilidad a fragilidad antes que los indicadores de cosecha.
- **Método.** Modelo de Markov oculto con emisiones gaussianas o de Student-t; selección de número de regímenes por BIC o validación cruzada de verosimilitud.
- **Validación.** Probabilidad de régimen fragil frente a choques conocidos en simulación.
- **Refutación.** El número de regímenes es sensible a la muestra y a la elección de la distribución de emisión.
- **Fuente.** [C].

### 4.3 Política de cobranza con RL fuera de línea y evaluación off-policy
- **Hipótesis.** Una política de cobranza aprendida de datos históricos puede superar a la regla actual, con evaluación confiable fuera de línea.
- **Método.** Aprendizaje por refuerzo fuera de línea (Q-learning conservador) y evaluación off-policy con estimador doblemente robusto.
- **Validación.** Estimación del valor de la política en datos retenidos; sensibilidad a la cobertura de exploración.
- **Refutación.** La evaluación off-policy requiere soporte común: si la política nueva visita acciones nunca observadas, la estimación es inválida.
- **Fuente.** [C].

### 4.4 Staging SICR con conformal para la clasificación de etapa
- **Hipótesis.** Un umbral de SICR basado en un intervalo conformal de PD es más estable que un umbral puntual.
- **Método.** Intervalo conformal de PD por cartera; cambio de etapa cuando el límite inferior supera el umbral.
- **Validación.** Frecuencia de cambios de etapa y estabilidad temporal (flip rate).
- **Refutación.** Un intervalo más amplio reduce cambios pero puede retrasar la detección de deterioro real. Hay un trade-off que debe justificarse ante auditoría.
- **Fuente.** Vinculado a conformal survival (Davidov et al., 2025) [V].

### 4.5 Contagio con algoritmo de clearing de Eisenberg-Noe
- **Hipótesis.** La red de exposiciones interbancarias amplifica pérdidas más allá de los choques directos; el efecto se cuantifica con el algoritmo de pago de Eisenberg-Noe (2001) [C].
- **Método.** Simulación de choques sobre la red con el algoritmo de punto fijo de pagos; medir el multiplicador de pérdida.
- **Validación.** Pruebas de estrés por nodo y sensibilidad a la estructura de la red.
- **Refutación.** La estructura de la red suele no observarse completa; la estimación de exposiciones bilaterales puede ser muy incierta.
- **Fuente.** [C].

### 4.6 Control de cartera con restricción de capital (proceso de decisión restringido)
- **Hipótesis.** La asignación de originación bajo restricción de capital y provisión se resuelve con un proceso de decisión de Markov restringido por multiplicadores de Lagrange.
- **Método.** Programa de Lagrange: \(\max_\pi\,\mathbb{E}[\sum_t \gamma^t r_t]\) sujeto a \(\mathbb{E}[\sum_t \gamma^t c_t]\le b\).
- **Validación.** Cumplimiento de la restricción de capital fuera de muestra y brecha de dualidad.
- **Refutación.** La dualidad es fuerte solo bajo condiciones de convexidad que pueden no cumplirse.
- **Fuente.** Altman (1999), *Constrained Markov Decision Processes* [C].

---

## 05 · Enterprise Risk Advisory (`05-enterprise-risk-advisory`)

### 5.1 Brecha de MRM frente a SR 26-2 como herramienta de consultoría
- **Hipótesis.** Un inventario de controles que mapea cada requisito de la guía de MRM (SR 26-2) a evidencia verificable reduce hallazgos de auditoría.
- **Método.** Matriz requisito → control → evidencia → prueba; priorizar brechas por severidad.
- **Validación.** Concordancia entre evaluadores independientes y hallazgos en auditoría simulada.
- **Refutación.** SR 26-2 es una guía de EE. UU. para bancos grandes. Su aplicación en Colombia requiere traducción normativa, no transferencia directa.
- **Fuente.** Federal Reserve, SR 26-2 [V].

### 5.2 Carga de cola operacional con umbral bayesiano
- **Hipótesis.** La selección del umbral en la teoría de valores extremos (POT) es la fuente principal de incertidumbre en la pérdida operacional de cola, y debe modelarse explícitamente.
- **Método.** Umbral como parámetro con prior; distribución posterior del cuantil 99,9 % promediando sobre el umbral.
- **Validación.** Cobertura de intervalos de cuantil en simulación con cola conocida.
- **Refutación.** Con pocos eventos extremos, la posterior puede depender del prior; la métrica de sensibilidad debe reportarse junto al VaR.
- **Fuente.** Pickands (1975) y McNeil & Frey (2000) [C].

### 5.3 XVA con aprendizaje diferencial para sensibilidades
- **Hipótesis.** Un modelo de red neuronal entrenado con gradientes (aprendizaje diferencial, Huge & Savine, 2020) reduce el costo computacional de XVA y sus sensibilidades.
- **Método.** Entrenar la red sobre valores y derivadas de la exposición; calcular CVA y sensibilidades.
- **Validación.** Error de CVA frente a Monte Carlo completo y error de sensibilidades.
- **Refutación.** El error de la red en cola puede ser sistemáticamente sesgado; las sensibilidades fuera del rango de entrenamiento son poco confiables.
- **Fuente.** [C].

### 5.4 Evaluación de LLM para clasificación de incidentes con métricas de calibración
- **Hipótesis.** Un LLM clasifica incidentes operacionales con precisión comparable a un revisor humano, y sus probabilidades pueden calibrarse.
- **Método.** Clasificación con LLM y calibración con regresión isotónica o escalamiento de temperatura; revisión humana sobre una muestra estratificada.
- **Validación.** Concordancia (kappa de Cohen) con revisores humanos y error de calibración esperado (ECE).
- **Refutación.** Un buen desempeño en un conjunto de prueba puede no generalizar a incidentes nuevos. Las probabilidades calibradas en un dominio pueden descalibrarse en otro.
- **Fuente.** SR 26-2 como marco de gobierno de IA [V].

### 5.5 Pruebas de robustez para control continuo con conformal
- **Hipótesis.** Un control continuo con intervalos conformales de anomalía tiene una tasa de falsas alarmas controlada.
- **Método.** Puntajes conformales sobre residuos de control; umbral por cuantil de calibración.
- **Validación.** Tasa de falsas alarmas empírica frente a la nominal y potencia ante anomalías inyectadas.
- **Refutación.** La intercambiabilidad se rompe con estacionalidad o cambios en el proceso; hay que recalibrar por ventana.
- **Fuente.** [C].

### 5.6 Priorización de alertas de AML con probabilidades calibradas y costo asimétrico
- **Hipótesis.** Un umbral de alerta optimizado con costo asimétrico (falso negativo mucho más caro) reduce pérdidas sin aumentar la carga operativa.
- **Método.** Probabilidad calibrada de alerta y umbral que minimiza el costo esperado \(C_{FN}\cdot FN + C_{FP}\cdot FP\).
- **Validación.** Curva de costo frente a umbral y pruebas por cohorte.
- **Refutación.** Los costos relativos son supuestos de negocio, no datos; el óptimo puede ser muy sensible a ellos.
- **Fuente.** [C].

---

## 06 · Motor de investigación cuantitativa (`06-quantitative-research-engine`)

### 6.1 Verificación de la matriz de correlación con proyección al cono PSD
- **Hipótesis.** La matriz de correlación estimada se puede corregir al cono de semidefinidas positivas con la mínima distorsión (proyección de Higham, 2002), y el riesgo cambia poco.
- **Método.** Proyección de Higham sobre la matriz de covarianza; medir la distancia de Frobenius y el cambio en la varianza de pérdida.
- **Validación.** Cambio en la pérdida al 99 % frente a la distancia de proyección.
- **Refutación.** La proyección puede cambiar las marginales de Bernoulli; el README del motor ya advierte que la PSD no se certifica, y esta idea lo resuelve solo parcialmente.
- **Fuente.** Higham (2002) [C].

### 6.2 Monte Carlo multinivel para la cola de pérdida
- **Hipótesis.** El Monte Carlo multinivel (Giles, 2008) reduce el costo de estimar cuantiles de cola para un nivel de error dado.
- **Método.** Estimadores de nivel con discretización de pasos finos y gruesos sobre la dinámica de factores.
- **Validación.** Costo versus error frente a Monte Carlo estándar.
- **Refutación.** Las ganancias dependen de la correlación entre niveles; para cuantiles, el sesgo es más difícil de controlar que para medias.
- **Fuente.** Giles (2008) [C].

### 6.3 Muestreo por importancia con factor condicional para eventos raros
- **Hipótesis.** El muestreo por importancia con desplazamiento del factor común (Glasserman & Li, 2005) reduce la varianza del estimador de pérdida extrema.
- **Método.** Desplazar la media del factor latente hacia la región de pérdida alta, con pesos de verosimilitud.
- **Validación.** Varianza del estimador frente a Monte Carlo ingenuo y cobertura del intervalo.
- **Refutación.** Un desplazamiento mal elegido puede aumentar la varianza; el peso puede degenerar.
- **Fuente.** Glasserman & Li (2005) [C].

### 6.4 Secuencias cuasi-Monte Carlo con aleatorización de Owen
- **Hipótesis.** Las secuencias de Sobol con aleatorización de Owen dan errores de cuantil menores que el Monte Carlo para la misma muestra.
- **Método.** Sobol aleatorizado (Owen) con repeticiones independientes para estimar el error.
- **Validación.** Error del cuantil frente al número de muestras y comparación con Monte Carlo puro.
- **Refutación.** Con muchas dimensiones efectivas, la ventaja de cuasi-Monte Carlo se pierde.
- **Fuente.** Owen (1998) [C].

### 6.5 Pruebas de paridad Python-C++ basadas en propiedades
- **Hipótesis.** Las pruebas basadas en propiedades (invariantes del motor) detectan discrepancias entre Python y C++ que las pruebas de casos fijos no detectan.
- **Método.** Generar entradas aleatorias con reglas de propiedad (monotonía de la pérdida frente a PD, linealidad de E[L]) y comparar salidas.
- **Validación.** Número de discrepancias encontradas frente a pruebas fijas existentes.
- **Refutación.** Las propiedades deben ser correctas; una propiedad incorrecta produce falsas alarmas.
- **Fuente.** [C].

### 6.6 Diferenciación automática para sensibilidades de capital
- **Hipótesis.** La diferenciación automática da sensibilidades de capital (Euler) exactas y más rápidas que diferencias finitas.
- **Método.** Diferenciación automática sobre el estimador de pérdida y asignación de Euler; validación contra diferencias finitas con paso controlado.
- **Validación.** Error relativo de la sensibilidad frente a diferencias finitas.
- **Refutación.** Las funciones con discontinuidades (como umbrales de pérdida) dan gradientes mal definidos.
- **Fuente.** [C].

---

## 07 · Riesgo financiero y de construcción (`07-financial-and-construction-risk-lab`)

### 7.1 Simulación de cronograma y costo con dependencia por cópula
- **Hipótesis.** Modelar las duraciones de actividades con dependencia por cópula, y no como independientes, cambia la distribución del retraso total y del costo.
- **Método.** Red de actividades con duraciones correlacionadas por cópula gaussiana o t; ruta crítica en cada simulación.
- **Validación.** Diferencia entre el retraso con independencia y con dependencia; sensibilidad a la correlación.
- **Refutación.** La correlación entre actividades se estima con juicio de expertos, no con datos; el resultado puede ser un artefacto del supuesto.
- **Fuente.** [C].

### 7.2 Regresión de cuantiles con bosques para costos de proyecto
- **Hipótesis.** Los bosques de cuantiles estiman el costo final con intervalos calibrados mejor que un modelo lineal con varianza constante.
- **Método.** Bosques de regresión por cuantiles (Meinshausen, 2006) [C].
- **Validación.** Cobertura de los intervalos por tipo de proyecto y ancho medio.
- **Refutación.** Con pocos proyectos completados, el modelo aprende muy poco; los bosques no extrapolan fuera del rango de entrenamiento.
- **Fuente.** [C].

### 7.3 Modelo de factores dinámicos para índices de costo de materiales
- **Hipótesis.** Un modelo de factores dinámicos con datos mensuales de precios de insumos mejora el pronóstico de inflación de costos de construcción.
- **Método.** Factores dinámicos (Giannone et al., 2008, para nowcasting) con datos mensuales y rezagos mixtos (MIDAS).
- **Validación.** Error de pronóstico fuera de muestra frente a un modelo univariado y a un paseo aleatorio.
- **Refutación.** Los precios de insumos colombianos pueden tener baja frecuencia o cambios de base; el resultado depende de la calidad del índice.
- **Fuente.** [C].

### 7.4 Alerta temprana de sobrecostos con regla de parada en línea
- **Hipótesis.** Una regla de parada secuencial (CUSUM) detecta el sobrecosto antes que el control mensual de avance.
- **Método.** CUSUM sobre la diferencia entre costo real y costo planeado ajustado por avance; calibrar la alarma con ARL.
- **Validación.** ARL₀ y ARL₁ frente a sobrecostos inyectados.
- **Refutación.** La varianza de costos es heterocedástica; un CUSUM con varianza constante genera alarmas falsas en fases de alto gasto.
- **Fuente.** [C].

### 7.5 Impacto de la liquidez del promotor sobre el riesgo de construcción
- **Hipótesis.** La probabilidad de incumplimiento del contratista depende de la liquidez del promotor. Ese vínculo se cuantifica con un modelo de contagio entre contratista y promotor.
- **Método.** Modelo de dos nodos con choques correlacionados y transferencia de pérdida por exposición; la estimación se hace con datos de pagos.
- **Validación.** Pérdida conjunta en simulación frente al caso sin contagio.
- **Refutación.** Los datos de exposición entre promotor y contratista suelen ser privados; el resultado depende de supuestos fuertes de exposición.
- **Fuente.** [C].

### 7.6 Valor de la flexibilidad (opciones reales) con aprendizaje por regresión
- **Hipótesis.** El valor de la opción de etapificar un proyecto se estima con la regresión de Longstaff-Schwartz (2001) con un error de aproximación menor que el de la cota inferior simple.
- **Método.** Método de mínimos cuadrados de Monte Carlo para la opción de posponer o abandonar; comparar con árbol binomial.
- **Validación.** Convergencia con el número de trayectorias y comparación con el árbol.
- **Refutación.** Los parámetros del proceso de demanda son el principal motor del valor, y suelen tener muy poca identificación.
- **Fuente.** Longstaff & Schwartz (2001) [C].

---

## Notas de verificación y limitaciones

- **Fuentes primarias verificadas en esta búsqueda:** carta SR 26-2 de la Reserva Federal (17-abr-2026, reemplaza SR 11-7 y SR 21-8). Para aplicarla fuera de EE. UU. se necesita revisar el anexo técnico completo, que no se leyó aquí.
- **Fuentes secundarias encontradas:** los artículos de arXiv citados (2607.17381, 2607.16970, 2509.05922, 2508.02183, 2309.12384) y el de Davidov et al. (ICLR 2025). Se leyeron los resúmenes, no los textos completos. Antes de usar cualquier resultado cuantitativo, hay que leer el artículo completo.
- **Búsqueda sobre la SFC:** no encontré documentación regulatoria reciente y específica para modelos de pérdida esperada en Colombia. Esa búsqueda debe repetirse con términos más precisos (circulares externas, Capítulo XXXI de la Circular Básica Contable y Financiera).
- **Tratamiento de la literatura clásica:** las referencias marcadas [C] son conocidas pero no se verificaron en esta sesión. Deben citarse con su fuente original antes de cualquier uso formal.
- **Prioridad sugerida:** 1.1 (conformal ECL), 2.2 (validación de IA bajo SR 26-2), 3.1 (regiones de insolvencia), 4.1 (bosques causales) y 6.3 (importancia para cola). Son las de mayor impacto por esfuerzo y las de mejor respaldo en la literatura reciente.

---

## Revisión de solapamientos con el repositorio

**Criterio:** Nueva = no hay trabajo equivalente en el repositorio. Gap explícito = el propio repositorio declara la limitación. Parcial = hay un proyecto cercano que cubre parte de la idea. Duplicada = el mismo problema ya tiene proyecto.

**Resumen:** 12 nuevas, 2 gaps explícitos, 5 duplicadas y 23 parciales. Las duplicadas deben integrarse como método en el proyecto existente, no como proyecto aparte.

| # | Idea | Estado | Referencia en el repositorio |
|---|---|---|---|
| 1.1 | Conformal survival para ECL | Nueva | El conformal solo aparece en KYC (`channel-conformal-audit`) |
| 1.2 | BOCPD para cosechas | Parcial | CUSUM en `fraud-and-anomaly-research/04-origination-process-anomalies` |
| 1.3 | PD con Lévy-OU | Nueva | Sin referencias |
| 1.4 | Cópulas t/Clayton y Wasserstein | Parcial | `credit-portfolio-strategy/copula-gaussiana-perdidas` |
| 1.5 | Semi-Markov en roll rates | Parcial | `credit-risk-products/matrices-de-transicion-roll-rates` (Markov) |
| 1.6 | Monotonía en GBM y equidad | Parcial | `scorecard-logistico-woe` ya fuerza monotonía en WoE; sin equidad |
| 2.1 | Backtesting de ES (Acerbi–Székely) | **Gap explícito** | `weighted-expected-shortfall-audit`: "no se ejecuta backtesting Acerbi–Szekely" |
| 2.2 | Validación de IA generativa (SR 26-2) | Parcial | `05/04-cyber-ai/ai-governance`; el repositorio no cita SR 11-7 ni SR 26-2 |
| 2.3 | Escenarios con modelos generativos | Nueva | Sin referencias |
| 2.4 | VaR con cobertura adaptativa | Nueva | Sin referencias |
| 2.5 | Riesgo de modelo entre familias GARCH | Parcial | `garch-volatilidad-y-var` (solo GARCH(1,1)) |
| 2.6 | Bootstrap de diferencial de Gini | Parcial | `validacion-de-modelo-psi-gini` |
| 3.1 | Regiones de insolvencia con HJB | Nueva | `03_LIQUIDEZ_ESTOCASTICA.md` discute déficit, sin control óptimo |
| 3.2 | LVaR con impacto | Parcial | `05_OPTIMIZACION_LIQUIDEZ.md` tiene costo de liquidación |
| 3.3 | Hawkes en margin calls | Nueva | `04_ESPIRALES_LIQUIDEZ.md` usa impacto lineal sin autoexcitación |
| 3.4 | Resiliencia del libro de órdenes | Nueva | Sin referencias |
| 3.5 | CVaR con DRO | Parcial | `05_OPTIMIZACION_LIQUIDEZ.md` (CVaR con costos); DRO es nuevo |
| 3.6 | ML causal para valles de mercado | Nueva | Sin referencias en mercado |
| 4.1 | Bosques causales para aprobación | **Duplicada** | `04-advanced-research/01-causal-origination-policy` |
| 4.2 | HMM para regímenes | Parcial | `04-advanced-research/02-nonstationary-credit-digital-twin` (método alternativo) |
| 4.3 | RL offline para cobranza | **Duplicada** | `04-advanced-research/03-collections-dynamic-treatment-regimes` (mismo marco) |
| 4.4 | SICR con conformal | Parcial | `04-advanced-research/04-ifrs9-forward-looking-ecl` |
| 4.5 | Eisenberg–Noe | Parcial | `03/04_ESPIRALES_LIQUIDEZ.md` la menciona; `04-advanced-research/05-siar` |
| 4.6 | Control con CMDP y Lagrange | **Duplicada** | `04-advanced-research/07-capital-constrained-portfolio-control` |
| 5.1 | Brecha de MRM frente a SR 26-2 | Parcial | `04-cyber-ai/ai-governance`; sin SR 11-7 en el repositorio |
| 5.2 | Umbral bayesiano en POT | Parcial | `03-operational-resilience/operational-extreme-tail` (sin prior sobre el umbral) |
| 5.3 | XVA con aprendizaje diferencial | Parcial | `07-valuation-counterparty/xva` (sin diferencial) |
| 5.4 | LLM para incidentes operacionales | Parcial | `fraud-and-anomaly-research/ai-enabled-fraud-defense` (LLM en fraude) |
| 5.5 | Control continuo con conformal | Parcial | `08-assurance-risk-data/continuous-controls` |
| 5.6 | Alertas AML con costo asimétrico | Parcial (probable solapamiento alto) | `05-financial-crime/aml-alert-prioritization` (verificar contenido) |
| 6.1 | Proyección de Higham a PSD | **Gap explícito** | README del motor: "no certifica que C sea PSD" |
| 6.2 | Monte Carlo multinivel | Nueva | Sin referencias |
| 6.3 | Muestreo por importancia | Parcial | `discrete-credit-tail-audit` (verificar implementación) |
| 6.4 | Sobol con aleatorización de Owen | Nueva | Sin referencias |
| 6.5 | Pruebas de propiedades y paridad | Parcial | `weighted-tail-underflow-guard/tests` |
| 6.6 | Diferenciación automática | Nueva | Sin referencias |
| 7.1 | Cronograma con cópula | Parcial | `02-construction-enterprise-risk/02-schedule-cost-overrun` |
| 7.2 | Bosques de cuantiles para costos | Nueva | Sin referencias en construcción |
| 7.3 | Factores dinámicos y MIDAS | Parcial | `03-research-in-progress/04-bayesian-construction-nowcasting`; `06-materials-inflation` |
| 7.4 | CUSUM para sobrecostos | Parcial | CUSUM solo en fraude; no en construcción |
| 7.5 | Contagio promotor-contratista | **Duplicada** | `03-research-in-progress/05-network-contagion-contractors`, `06-construction-network-contagion`, `02/04-contractor-counterparty-risk` |
| 7.6 | Opciones reales con LSM | **Duplicada** | `03-research-in-progress/07-real-options-staged-development` |

### Prioridad sugerida tras la revisión
1. **2.1 (backtesting de ES):** gap declarado por el propio repositorio, con literatura conocida.
2. **6.1 (proyección PSD):** el README del motor pide justamente esta verificación.
3. **1.1 (conformal survival para ECL):** nueva y de alto impacto para IFRS 9.
4. **3.3 (Hawkes en margin calls):** complementa directamente `04_ESPIRALES_LIQUIDEZ.md`.
5. **2.4 (VaR conformal adaptativo):** nueva y verificable con los backtests existentes.

### Límites de esta revisión
- Se revisaron títulos, README y palabras clave, no el código ni los resultados de cada subcarpeta. Las marcas "verificar" necesitan una lectura de código.
- Las coincidencias por palabra clave pueden ser falsos positivos. Por eso, cada entrada de la tabla se contrastó con el texto del archivo referido cuando fue posible.
