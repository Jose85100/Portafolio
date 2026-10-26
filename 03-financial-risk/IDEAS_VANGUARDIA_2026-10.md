# 03-financial-risk: 6 ideas de vanguardia por carpeta

**Totales.** 42 ideas nuevas (12 de la primera revisión y 30 añadidas en 1.7–7.11) y 30 extensiones de proyectos existentes.

**Alcance.** Repositorio `Jose85100/Portafolio`, carpeta `03-financial-risk`, 7 áreas. Revisé la estructura y los README de cada área. No auditamos el código de cada subcarpeta, así que cada idea se contrasta solo con lo que el README describe. Antes de implementar, conviene confirmar que no duplica un proyecto existente.

**Convención de verificación.**
- **[V]**: respaldada por una fuente encontrada en esta búsqueda (se indica cuál).
- **[C]**: literatura clásica o estándar conocida; citar antes de usar en producción.

Cada idea incluye: hipótesis, formulación mínima, validación y refutación (el riesgo que el enfoque podría ocultar).

---

## 01 · Riesgo de crédito (`01-credit-risk`)

### 1.1 Intervalos de ECL con cobertura garantizada (conformal survival)

**Tipo:** Nueva
- **Hipótesis.** Los intervalos de pérdida lifetime pueden tener cobertura finita garantizada sin supuestos distribucionales fuertes.
- **Método.** Análisis de supervivencia conformal para datos censurados a la derecha: dado un nivel \(\alpha\), construir \([L_{\text{low}}(x), L_{\text{up}}(x)]\) tal que \(P(T \in C(x)) \ge 1-\alpha\) bajo intercambiabilidad. Usar ponderación por probabilidad inversa de censura para el caso de censura general.
- **Validación.** Cobertura empírica por estrato (no solo marginal) y ancho medio del intervalo. Comparar con el intervalo de Kaplan-Meier sin condicionar.
- **Refutación.** La cobertura marginal no implica cobertura condicional; con cambio de covariables (originación nueva vs. cartera madura) la garantía se degrada sin ponderación por *covariate shift* (Tibshirani et al., 2019) [C].
- **Fuente.** Davidov et al., *Conformalized Survival Analysis for General Right-Censored Data*, ICLR 2025 [V].

### 1.2 Alerta temprana de quiebres en cosechas con BOCPD

**Tipo:** Extensión de `fraud-and-anomaly-research/04-origination-process-anomalies` (método CUSUM, aplicado a cosechas)
- **Hipótesis.** Un cambio en la tasa de mora de una cosecha se detecta antes que el DPD30 por encima de su umbral.
- **Método.** Detección de puntos de cambio bayesiana en línea (Adams & MacKay, 2007) sobre la serie de mora por cosecha, con probabilidad posterior de *run length*.
- **Validación.** Retardo medio de detección vs. falsas alarmas (ARL₀ y ARL₁) sobre datos sintéticos con cambios conocidos; luego sobre histórico.
- **Refutación.** Con poca historia por cosecha, el prior domina; la hazard constante es inadecuada si hay estacionalidad. Requiere calibrar la hazard por ciclo económico.
- **Fuente.** [C].

### 1.3 PD con procesos de Lévy-Ornstein-Uhlenbeck y saltos

**Tipo:** Nueva
- **Hipótesis.** Los saltos de calidad crediticia (choques macro abruptos) explican mejor la PD que un proceso gaussiano como el de Vasicek.
- **Método.** Modelo de PD como función de un factor latente \(X_t\) con dinámica OU conducida por un proceso de Lévy (saltos), con calibración por máxima verosimilitud aproximada.
- **Validación.** Comparar Vasicek y LOU-Lévy con BIC, prueba de calibración por cosecha y error de estimación de cola en el percentil 99,5 de pérdida.
- **Refutación.** Más parámetros implican mayor riesgo de sobreajuste; los saltos pueden absorber errores de especificación del factor macro.
- **Fuente.** arXiv:2309.12384 [V].

### 1.4 Copulas con dependencia de cola alternativa y robustez por Wasserstein

**Tipo:** Extensión de `credit-portfolio-strategy/copula-gaussiana-perdidas`
- **Hipótesis.** La copula gaussiana subestima la pérdida conjunta de cola; una copula t o de Clayton con dependencia de cola superior da una pérdida de cola mayor.
- **Método.** Comparar cópulas gaussiana, t y Clayton para la cartera. Robustez mediante optimización distribucionalmente robusta sobre una bola de Wasserstein alrededor de la cópula estimada (Esfahani & Kuhn, 2018) [C].
- **Validación.** Pérdida al 99,9 % y dependencia de cola empírica (\(\lambda_U\)) con intervalos bootstrap. Prueba de la sensibilidad de la asignación de capital.
- **Refutación.** La dependencia de cola se estima con muy pocos eventos extremos; el intervalo puede ser tan amplio que no distinga las cópulas.
- **Fuente.** [C].

### 1.5 Matriz de transición semi-Markov con tiempo de permanencia

**Tipo:** Extensión de `credit-risk-products/matrices-de-transicion-roll-rates`
- **Hipótesis.** Los roll rates son semi-Markov: la probabilidad de pasar de estado depende de cuánto tiempo se lleva en él, no solo del estado actual.
- **Método.** Estimador de Aalen-Johansen para transiciones con tiempo de permanencia; comparar con la cadena de Markov en tiempo continuo.
- **Validación.** Prueba de Markov (por ejemplo, test de Aalen-type sobre tiempos de permanencia) y error de predicción de saldos por estado a 12 meses.
- **Refutación.** Con datos sintéticos, cualquier diferencia es un artefacto del generador si no se controla la semilla y el régimen.
- **Fuente.** [C].

### 1.6 Auditoría de monotonía y equidad en scorecards con modelos de gradiente

**Tipo:** Extensión de `credit-risk-products/scorecard-logistico-woe`
- **Hipótesis.** Un modelo de gradiente con restricciones de monotonía iguala el Gini de la regresión logística sin violar la lógica de negocio ni introducir impacto dispar.
- **Método.** Gradient boosting con restricciones monótonas por variable. Medir impacto dispar entre grupos protegidos sustitutos, con análisis de causalidad donde sea posible.
- **Validación.** Gini, calibración por decil y prueba de la diferencia de Gini (DeLong). Métricas de equidad: impacto dispar y tasas de error por grupo.
- **Refutación.** La equidad depende de la definición (paridad demográfica, igualdad de oportunidades); ninguna es neutral. Las variables sustitutas pueden reconstruir atributos excluidos.
- **Fuente.** [C].

### 1.7 Scorecard federado entre entidades sin compartir datos crudos
**Tipo:** Nueva
- **Hipótesis.** Un modelo federado entre varias entidades alcanza un Gini cercano al centralizado sin mover datos de clientes.
- **Método.** Entrenamiento federado (promedio de gradientes o de coeficientes) sobre particiones no independientes e idénticamente distribuidas; privacidad diferencial con presupuesto ε explícito.
- **Validación.** Diferencia de Gini frente al modelo centralizado, con intervalos por bootstrap entre entidades; sensibilidad a ε.
- **Refutación.** La heterogeneidad entre carteras (no IID) y el sesgo de selección de cada entidad pueden invalidar el promedio de modelos.
- **Fuente.** arXiv:2601.11134 (aprendizaje federado en riesgo de crédito) [V, lead de búsqueda].

### 1.8 Modelos de secuencia sobre historial de pagos
**Tipo:** Nueva
- **Hipótesis.** Un modelo de secuencia (transformador o red recurrente) sobre el historial mensual de pagos mejora el Gini de un GBM con variables agregadas.
- **Método.** Entrada: serie de saldos, pagos y días de mora por cliente-mes. Comparación con GBM sobre agregados, con calibración posterior (isotónica).
- **Validación.** Validación temporal estricta (sin fuga de información futura), Gini y calibración por ventana.
- **Refutación.** La ganancia puede venir de fuga de información por construcción de la ventana; sin una partición temporal estricta el resultado no es válido.
- **Fuente.** [C] (literatura de modelos secuenciales en crédito).

### 1.9 Rezago de reporte de default como sesgo de definición
**Tipo:** Nueva
- **Hipótesis.** El rezago entre la fecha efectiva de incumplimiento y su registro en el sistema sesga la PD observada, y se corrige con un modelo de censura.
- **Método.** Modelar el tiempo de reporte como variable latente y corregir la tasa de default con estimación de censura por intervalo.
- **Validación.** Sesgo de la PD estimada frente a un escenario de reporte conocido en simulación; sensibilidad al rezago.
- **Refutación.** Si el rezago depende del tipo de cliente o de la política de cobranza, la corrección puede transferir un sesgo nuevo.
- **Fuente.** [C].

### 1.10 Cópulas vine para dependencia entre sectores
**Tipo:** Nueva
- **Hipótesis.** Una cópula vine captura una dependencia entre sectores más rica que una cópula gaussiana de un factor.
- **Método.** Selección de la estructura vine con criterio AIC y ajuste por máxima verosimilitud; simulación de pérdidas de cartera.
- **Validación.** Dependencia de cola empírica frente a la simulada; comparación con la cópula gaussiana en pérdida al 99,9 %.
- **Refutación.** Con pocos sectores y pocos eventos conjuntos, la estructura vine es inestable y su elección puede no ser robusta.
- **Fuente.** [C] (Aas et al., 2009, para cópulas vine).

---

## 02 · Riesgo de mercado y de modelo (`02-market-and-model-risk`)

### 2.1 Backtesting de Expected Shortfall con pruebas Z

**Tipo:** Extensión de `02-market-and-model-risk/weighted-expected-shortfall-audit` (backtesting declarado pendiente)
- **Hipótesis.** El ES puede validarse con pruebas de magnitud (no solo de conteo de excepciones), con potencia suficiente en muestras de 250 días.
- **Método.** Pruebas Z de Acerbi & Székely (2014) sobre la distribución de pérdidas de excepción, junto con la prueba de Kupiec para VaR.
- **Validación.** Potencia y tamaño (tipo I) por simulación Monte Carlo con colas t y sesgo de ES.
- **Refutación.** Con colas pesadas y ventana corta, la potencia de cualquier prueba de ES es baja. Un resultado "pasa" puede ser solo falta de potencia.
- **Fuente.** [C]; relevante para el marco FRTB (cambio a ES) [V, búsqueda sobre FRTB].

### 2.2 Validación de modelos de IA generativa bajo SR 26-2

**Tipo:** Extensión de `05-enterprise-risk-advisory/04-cyber-ai/ai-governance`
- **Hipótesis.** Un marco de validación con desafiante (*challenger*), monitoreo de deriva y pruebas de robustez cubre los riesgos de un LLM usado en decisiones de riesgo.
- **Método.** Matriz de riesgos del LLM: alucinación, deriva de datos y prompts, dependencia de proveedor. Pruebas: consistencia entre ejecuciones, pruebas adversarias y comparación contra un modelo estadístico de referencia.
- **Validación.** Tasa de error sobre un conjunto de preguntas con respuesta verificada y estabilidad de la salida ante perturbaciones menores del prompt.
- **Refutación.** La no determinación de los LLM hace difícil reproducir resultados. Una buena métrica de evaluación de un LLM puede no predecir su error en producción.
- **Fuente.** Federal Reserve, carta SR 26-2, 17-abr-2026, que reemplaza SR 11-7 [V, sitio oficial de la Reserva Federal]. Aplica a bancos de más de 30 000 millones de dólares; la aplicabilidad a una entidad colombiana requiere análisis regulatorio propio.

### 2.3 Escenarios sintéticos con modelos generativos evaluados por hechos estilizados

**Tipo:** Nueva
- **Hipótesis.** Un generador de series (GAN temporal o modelo de difusión) produce escenarios de estrés que respetan los hechos estilizados (agrupamiento de volatilidad, colas pesadas, ausencia de autocorrelación en retornos).
- **Método.** Entrenar TimeGAN (Yoon et al., 2019) o un modelo de difusión sobre retornos; evaluar con ACF de \(|r_t|\), índice de cola de Hill y pruebas de distribución.
- **Validación.** Distancia de los hechos estilizados frente a la historia real y prueba de cobertura del VaR generado.
- **Refutación.** Colapso de modos: el generador puede replicar la cola histórica pero no los escenarios nuevos. Un buen ajuste histórico no garantiza que el escenario de estrés sea plausible.
- **Fuente.** [C].

### 2.4 VaR con cobertura adaptativa (conformal) bajo no estacionariedad

**Tipo:** Nueva
- **Hipótesis.** El VaR con cobertura adaptativa mantiene la tasa de excepciones objetivo aun con cambios de régimen.
- **Método.** Inferencia conformal adaptativa (Gibbs & Candès, 2021), que actualiza el nivel de error \(\alpha_t\) según la excepción observada.
- **Validación.** Tasa de excepciones frente a \(\alpha\) nominal, cobertura condicional por régimen y número de excepciones consecutivas.
- **Refutación.** La garantía asintótica no es válida en muestras cortas; el ajuste puede volverse inestable tras un choque grande.
- **Fuente.** [C].

### 2.5 Riesgo de modelo como prima sobre familias GARCH

**Tipo:** Extensión de `02-market-and-model-risk/garch-volatilidad-y-var`
- **Hipótesis.** La diferencia de VaR entre GARCH, EGARCH y GJR-GARCH es una medida cuantificable del riesgo de modelo, y debe reportarse junto al VaR.
- **Método.** Calcular VaR y ES con cada especificación; medir la dispersión (rango o desviación) y la prima de riesgo de modelo como el máximo de la diferencia.
- **Validación.** Sobre datos sintéticos con la especificación conocida, verificar que la métrica identifica el modelo verdadero.
- **Refutación.** Un rango pequeño puede reflejar que todas las especificaciones comparten el mismo error (por ejemplo, la distribución de innovaciones).
- **Fuente.** [C].

### 2.6 Validación de PD con desafiante de gradiente y prueba de estabilidad de Gini

**Tipo:** Extensión de `02-market-and-model-risk/validacion-de-modelo-psi-gini`
- **Hipótesis.** La diferencia de Gini entre campeón (logística) y desafiante (gradiente) es estadísticamente significativa solo en algunas cosechas.
- **Método.** Bootstrap por cosecha del diferencial de Gini; prueba de estabilidad de PSI por ventana móvil.
- **Validación.** Intervalos de confianza del diferencial y consistencia entre ventanas.
- **Refutación.** Los bootstrap sobre datos con dependencia temporal subestiman la varianza; se requiere bloqueo temporal (*block bootstrap*).
- **Fuente.** [C].

### 2.7 Control de riesgo conformal adaptativo para umbrales de cartera
**Tipo:** Nueva
- **Hipótesis.** Un control de riesgo conformal adaptativo mantiene la pérdida promedio objetivo aun con cambios de régimen.
- **Método.** Control de riesgo conformal con actualización automática del nivel objetivo (Blot et al., 2025) aplicado a un umbral de pérdida de cartera.
- **Validación.** Pérdida promedio realizada frente al objetivo y ancho de la regla de decisión.
- **Refutación.** La garantía es asintótica; en muestras cortas la regla puede ser conservadora o volátil.
- **Fuente.** Blot et al., *Automatically Adaptive Conformal Risk Control*, PMLR v258 (2025) [V, lead de búsqueda].

### 2.8 Estrés path-dependent con firmas (signatures)
**Tipo:** Nueva
- **Hipótesis.** Un modelo de firmas captura dependencia de trayectoria (por ejemplo, la secuencia de caídas) que las pruebas de estrés puntuales no capturan.
- **Método.** Calcular la firma truncada de la trayectoria de factores y regresarla contra la pérdida de cartera.
- **Validación.** Error fuera de muestra frente a un modelo de factores sin memoria; pruebas en trayectorias de estrés históricas.
- **Refutación.** El número de términos de la firma crece rápido; con truncamiento bajo puede perder la dependencia que se busca.
- **Fuente.** arXiv:2603.04525 (signature de Volterra) y arXiv:2603.24154 (SigSwap) [V, leads de búsqueda].

### 2.9 Volatilidad realizada (HAR) frente a GARCH
**Tipo:** Nueva
- **Hipótesis.** Un modelo HAR sobre volatilidad realizada pronostica mejor el riesgo de corto plazo que un GARCH(1,1) en datos intradía.
- **Método.** Modelo HAR de Corsi (2009) sobre la varianza realizada diaria, con comparación de pronósticos.
- **Validación.** Pérdida de pronóstico (QLIKE) y backtesting del VaR derivado.
- **Refutación.** Requiere datos intradía que pueden no existir en mercados poco líquidos; el ruido de microestructura sesga la volatilidad realizada.
- **Fuente.** Corsi (2009) [C].

### 2.10 Estabilidad de explicaciones como control de validación
**Tipo:** Nueva
- **Hipótesis.** Un modelo de PD con explicaciones (SHAP) inestables entre ventanas no es auditable, aunque tenga buen Gini.
- **Método.** Medir la estabilidad de los valores SHAP por variable entre cosechas (correlación de rangos) y entre semillas de entrenamiento.
- **Validación.** Umbral de estabilidad definido antes del análisis; comparación entre modelos con Gini similar.
- **Refutación.** Un SHAP estable puede ser igual de engañoso si las variables están correlacionadas; la estabilidad no implica causalidad.
- **Fuente.** [C].

---

## 03 · Liquidez y riesgo de mercado (`03-market-liquidity-research`)

### 3.1 Regiones de insolvencia con liquidez y crédito acoplados (HJB)

**Tipo:** Nueva
- **Hipótesis.** La insolvencia ocurre en regiones no lineales del espacio (liquidez, crédito), y el efecto conjunto es mayor que la suma de los efectos individuales.
- **Método.** Control óptimo estocástico con ecuación de Hamilton-Jacobi-Bellman y un modelo acoplado de liquidez (LCR/NSFR de Basilea III) y crédito.
- **Validación.** Trayectorias de la región de insolvencia frente a combinaciones de estrés; sensibilidad a parámetros; comparación con pruebas de estrés estándar.
- **Refutación.** El resultado de umbral depende de la calibración; el artículo original usa datos bancarios de otro país, así que la transferencia a Colombia no es automática.
- **Fuente.** arXiv:2607.17381, "Determining Insolvency Regions in Banks" [V].

### 3.2 Liquidity-adjusted VaR con impacto de mercado

**Tipo:** Extensión de `03-market-liquidity-research/05_OPTIMIZACION_LIQUIDEZ.md` (costos de liquidación)
- **Hipótesis.** El VaR debe ajustarse por el costo de salir de la posición, que depende del tamaño y del horizonte de liquidación.
- **Método.** Costo de liquidación con impacto temporal y permanente tipo Almgren-Chriss (2000) [C]; VaR ajustado con horizonte igual al tiempo de liquidación.
- **Validación.** Sensibilidad del LVaR al tamaño de la posición y a la tasa de liquidación.
- **Refutación.** Los parámetros de impacto se estiman con datos de ejecución que pueden no existir en el mercado objetivo.
- **Fuente.** [C] (Bangia et al., 1999, es el antecedente clásico de LVaR).

### 3.3 Contagio de *margin calls* con procesos de Hawkes

**Tipo:** Nueva
- **Hipótesis.** Las ventas forzadas se auto-excitan: una venta eleva la probabilidad de la siguiente en un período corto.
- **Método.** Proceso de Hawkes multivariado para eventos de llamadas de margen, con intensidad \(\lambda_i(t)=\mu_i+\sum_j \int g_{ij}(t-s)\,dN_j(s)\). Calibración por máxima verosimilitud.
- **Validación.** Prueba de bondad de ajuste (residuos de Ogata) y predicción de la cola de la intensidad.
- **Refutación.** Un Hawkes con núcleo exponencial puede confundir autoexcitación con ciclos comunes o estacionalidad no modelada.
- **Fuente.** [C].

### 3.4 Resiliencia del libro de órdenes como medida de liquidez

**Tipo:** Nueva
- **Hipótesis.** La resiliencia (velocidad de recuperación de la profundidad del libro tras una orden grande) es un predictor de liquidez más robusto que el diferencial.
- **Método.** Estimar la resiliencia con el modelo de decaimiento del impacto de orden de Bouchaud; compararla con la profundidad y el diferencial.
- **Validación.** Correlación con el costo de ejecución realizado en datos de libro de órdenes.
- **Refutación.** La resiliencia en mercados poco líquidos (como muchos de Latinoamérica) puede no ser estable en el tiempo.
- **Fuente.** arXiv:2607.16970, "Herding and Liquidity in Order-Book Markets. II" [V, como lectura de punto de partida].

### 3.5 CVaR con optimización distribucionalmente robusta y costos de liquidación

**Tipo:** Extensión de `03-market-liquidity-research/05_OPTIMIZACION_LIQUIDEZ.md` (CVaR con costos)
- **Hipótesis.** Optimizar el CVaR con el conjunto de incertidumbre de Wasserstein es más estable que el CVaR con muestra histórica cuando hay pocas observaciones de cola.
- **Método.** Programa DRO: \(\min_w \sup_{Q:\,W_p(Q,\hat P)\le\varepsilon}\mathrm{CVaR}_\alpha^Q(w^\top R - c(w))\). Con costos lineales por tramos.
- **Validación.** Estabilidad de los pesos frente a remuestreo y pérdida fuera de muestra.
- **Refutación.** Un \(\varepsilon\) mal calibrado puede volver la solución excesivamente conservadora.
- **Fuente.** Rockafellar & Uryasev (2000) para CVaR [C]; Esfahani & Kuhn (2018) para Wasserstein [C].

### 3.6 Alerta temprana de estrés de liquidez con causalidad

**Tipo:** Nueva
- **Hipótesis.** Un modelo de aprendizaje automático con interpretación causal identifica mejor los valles de mercado que la correlación simple.
- **Método.** Aprendizaje automático con validación por tiempos de rezago y estimación causal de efectos (por ejemplo, doble aprendizaje automático, Chernozhukov et al., 2018) [C].
- **Validación.** Predicción fuera de muestra con ventanas temporales y pruebas de robustez a la omisión de variables.
- **Refutación.** La causalidad en series temporales es difícil de identificar; los efectos estimados pueden ser espurios si hay variables comunes no observadas.
- **Fuente.** arXiv:2509.05922, "Predicting Market Troughs: A Machine Learning Approach with Causal Interpretation" [V].

### 3.7 Run-off de depósitos con supervivencia y choque de tasas
**Tipo:** Nueva
- **Hipótesis.** Un modelo de supervivencia del saldo de depósitos, condicionado a un choque de tasas, da un run-off más realista que la tasa fija regulatoria.
- **Método.** Modelo de riesgo proporcional con covariables de tasa y del tipo de depositante; estimación del saldo esperado a 30 días para el cálculo de LCR.
- **Validación.** Calibración del run-off predicho frente a retiros observados en episodios de estrés; comparación con la tasa fija.
- **Refutación.** Los depositantes pueden cambiar de comportamiento en episodios raros; un histórico sin crisis subestima el run-off.
- **Fuente.** Marco de LCR de Basilea (chapter de BCBS) [V, lead de búsqueda]; modelo de riesgo proporcional de Cox [C].

### 3.8 Curva de liquidez de activos con volumen intradía
**Tipo:** Nueva
- **Hipótesis.** El tiempo para liquidar una posición depende del volumen intradía disponible y se puede estimar como función del tamaño.
- **Método.** Estimar la fracción diaria de volumen liberable por activo y construir una curva de tiempo de liquidación frente al monto a vender.
- **Validación.** Error de la curva frente a ejecuciones reales en datos de mercado; sensibilidad a la fracción de participación.
- **Refutación.** En crisis el volumen disponible cae; la curva de días normales subestima el tiempo de liquidación.
- **Fuente.** [C] (modelos de impacto de Almgren y Chriss, 2000).

---

## 04 · Investigación avanzada (`04-advanced-research`)

Estas ideas complementan los siete proyectos existentes sin duplicarlos.

### 4.1 Efectos heterogéneos de la política de aprobación con bosques causales

**Tipo:** Extensión de `04-advanced-research/01-causal-origination-policy`
- **Hipótesis.** El efecto causal de aprobar un crédito varía por segmento, y un bosque causal lo estima con mejor precisión que un modelo de respuesta.
- **Método.** Bosques causales (Wager & Athey, 2018) [C] con doble aprendizaje automático para el efecto de tratamiento; restricción de equidad en la asignación.
- **Validación.** Curva de calibración del efecto (*calibration of CATE*) y evaluación de la política con estimador doblemente robusto.
- **Refutación.** Los datos de aprobación son observacionales; la identificación depende de la ignorabilidad, que no se puede probar.
- **Fuente.** Relacionado con la literatura de aprendizaje automático causal aplicado a límites de crédito (arXiv:2508.02183) [V].

### 4.2 Detección de regímenes en el gemelo digital con cambio de estado oculto

**Tipo:** Extensión de `04-advanced-research/02-nonstationary-credit-digital-twin`
- **Hipótesis.** Un modelo de Markov oculto con dos o tres regímenes detecta la transición de estabilidad a fragilidad antes que los indicadores de cosecha.
- **Método.** Modelo de Markov oculto con emisiones gaussianas o de Student-t; selección de número de regímenes por BIC o validación cruzada de verosimilitud.
- **Validación.** Probabilidad de régimen fragil frente a choques conocidos en simulación.
- **Refutación.** El número de regímenes es sensible a la muestra y a la elección de la distribución de emisión.
- **Fuente.** [C].

### 4.3 Política de cobranza con RL fuera de línea y evaluación off-policy

**Tipo:** Extensión de `04-advanced-research/03-collections-dynamic-treatment-regimes`
- **Hipótesis.** Una política de cobranza aprendida de datos históricos puede superar a la regla actual, con evaluación confiable fuera de línea.
- **Método.** Aprendizaje por refuerzo fuera de línea (Q-learning conservador) y evaluación off-policy con estimador doblemente robusto.
- **Validación.** Estimación del valor de la política en datos retenidos; sensibilidad a la cobertura de exploración.
- **Refutación.** La evaluación off-policy requiere soporte común: si la política nueva visita acciones nunca observadas, la estimación es inválida.
- **Fuente.** [C].

### 4.4 Staging SICR con conformal para la clasificación de etapa

**Tipo:** Extensión de `04-advanced-research/04-ifrs9-forward-looking-ecl`
- **Hipótesis.** Un umbral de SICR basado en un intervalo conformal de PD es más estable que un umbral puntual.
- **Método.** Intervalo conformal de PD por cartera; cambio de etapa cuando el límite inferior supera el umbral.
- **Validación.** Frecuencia de cambios de etapa y estabilidad temporal (flip rate).
- **Refutación.** Un intervalo más amplio reduce cambios pero puede retrasar la detección de deterioro real. Hay un trade-off que debe justificarse ante auditoría.
- **Fuente.** Vinculado a conformal survival (Davidov et al., 2025) [V].

### 4.5 Contagio con algoritmo de clearing de Eisenberg-Noe

**Tipo:** Extensión de `04-advanced-research/05-siar-integrated-risk-contagion`
- **Hipótesis.** La red de exposiciones interbancarias amplifica pérdidas más allá de los choques directos; el efecto se cuantifica con el algoritmo de pago de Eisenberg-Noe (2001) [C].
- **Método.** Simulación de choques sobre la red con el algoritmo de punto fijo de pagos; medir el multiplicador de pérdida.
- **Validación.** Pruebas de estrés por nodo y sensibilidad a la estructura de la red.
- **Refutación.** La estructura de la red suele no observarse completa; la estimación de exposiciones bilaterales puede ser muy incierta.
- **Fuente.** [C].

### 4.6 Control de cartera con restricción de capital (proceso de decisión restringido)

**Tipo:** Extensión de `04-advanced-research/07-capital-constrained-portfolio-control`
- **Hipótesis.** La asignación de originación bajo restricción de capital y provisión se resuelve con un proceso de decisión de Markov restringido por multiplicadores de Lagrange.
- **Método.** Programa de Lagrange: \(\max_\pi\,\mathbb{E}[\sum_t \gamma^t r_t]\) sujeto a \(\mathbb{E}[\sum_t \gamma^t c_t]\le b\).
- **Validación.** Cumplimiento de la restricción de capital fuera de muestra y brecha de dualidad.
- **Refutación.** La dualidad es fuerte solo bajo condiciones de convexidad que pueden no cumplirse.
- **Fuente.** Altman (1999), *Constrained Markov Decision Processes* [C].

### 4.7 Sesgo de selección en recuperaciones observadas
**Tipo:** Nueva
- **Hipótesis.** Las recuperaciones solo se observan en casos resueltos, y estimarlas sin corregir por selección subestima la pérdida.
- **Método.** Modelo de selección tipo Heckman con ecuación de resolución y ecuación de recuperación, con restricción de exclusión.
- **Validación.** Sesgo de la recuperación estimada en simulación con selección conocida; sensibilidad a la restricción de exclusión.
- **Refutación.** La restricción de exclusión es difícil de justificar; sin ella la corrección depende de la forma distribucional.
- **Fuente.** Heckman (1979) [C].

### 4.8 Transporte óptimo para cambio de covariables entre cosechas
**Tipo:** Nueva
- **Hipótesis.** Un ajuste por transporte óptimo entre la cosecha histórica y la nueva corrige el cambio de covariables mejor que la reponderación simple.
- **Método.** Estimar el mapa de transporte entre distribuciones de covariables y reponderar la PD estimada.
- **Validación.** Error de calibración de la PD en una cosecha retenida con cambio conocido.
- **Refutación.** Con muestras pequeñas el transporte es inestable; el resultado depende de la métrica de costo elegida.
- **Fuente.** [C] (Villani, 2009, para transporte óptimo).

### 4.9 Análisis de sensibilidad causal (Rosenbaum y E-value)
**Tipo:** Nueva
- **Hipótesis.** La conclusión causal de la política de aprobación es robusta a un nivel de confusión no observada moderado.
- **Método.** Límites de Rosenbaum y E-value sobre el efecto estimado; reportar el nivel de confusión que anularía el resultado.
- **Validación.** Confusión necesaria comparada con las variables observadas más fuertes (referencia empírica).
- **Refutación.** El E-value no prueba ausencia de confusión; una confusión mayor que la observable sigue siendo posible.
- **Fuente.** VanderWeele y Ding (2017), E-value [C].

### 4.10 Contagio entre cosechas con procesos de Hawkes
**Tipo:** Nueva
- **Hipótesis.** El incumplimiento de una cosecha eleva la probabilidad de incumplimiento de cosechas relacionadas en un período corto.
- **Método.** Proceso de Hawkes multivariado sobre eventos de mora por cosecha, con núcleo exponencial.
- **Validación.** Residuos de Ogata y predicción de la intensidad fuera de muestra.
- **Refutación.** La autoexcitación puede confundirse con un factor común no observado (un ciclo económico).
- **Fuente.** Hawkes (1971) [C].

### 4.11 Modelo de cura para clientes que nunca incumplen
**Tipo:** Nueva
- **Hipótesis.** Una fracción de clientes nunca incumple; un modelo de cura separa esa fracción del tiempo hasta incumplimiento.
- **Método.** Modelo de mezcla de cura: probabilidad de cura logística y supervivencia condicional para los no curados.
- **Validación.** Calibración de la supervivencia en horizontes de 12 y 24 meses; comparación con Kaplan-Meier sin cura.
- **Refutación.** La cura no es identificable si el horizonte observado es corto; la fracción curada puede estar sobreestimada.
- **Fuente.** [C] (modelos de mezcla de cura).

### 4.12 Pilotos de política con bandits y arrepentimiento acotado
**Tipo:** Nueva
- **Hipótesis.** Un diseño adaptativo con bandits asigna pilotos de política de crédito con menos costo de oportunidad que un experimento A/B fijo.
- **Método.** Muestreo de Thompson sobre las políticas candidatas, con cota de arrepentimiento y restricción de riesgo máximo por piloto.
- **Validación.** Arrepentimiento acumulado en simulación frente a un A/B fijo; cumplimiento de la restricción de riesgo.
- **Refutación.** El muestreo adaptativo puede sesgar la estimación del efecto final; hay que usar estimadores válidos tras la adaptación.
- **Fuente.** [C] (Thompson, 1933; Lattimore y Szepesvári, 2020).

---

## 05 · Enterprise Risk Advisory (`05-enterprise-risk-advisory`)

### 5.1 Brecha de MRM frente a SR 26-2 como herramienta de consultoría

**Tipo:** Extensión de `05-enterprise-risk-advisory/04-cyber-ai/ai-governance`
- **Hipótesis.** Un inventario de controles que mapea cada requisito de la guía de MRM (SR 26-2) a evidencia verificable reduce hallazgos de auditoría.
- **Método.** Matriz requisito → control → evidencia → prueba; priorizar brechas por severidad.
- **Validación.** Concordancia entre evaluadores independientes y hallazgos en auditoría simulada.
- **Refutación.** SR 26-2 es una guía de EE. UU. para bancos grandes. Su aplicación en Colombia requiere traducción normativa, no transferencia directa.
- **Fuente.** Federal Reserve, SR 26-2 [V].

### 5.2 Carga de cola operacional con umbral bayesiano

**Tipo:** Extensión de `05-enterprise-risk-advisory/03-operational-resilience/operational-extreme-tail`
- **Hipótesis.** La selección del umbral en la teoría de valores extremos (POT) es la fuente principal de incertidumbre en la pérdida operacional de cola, y debe modelarse explícitamente.
- **Método.** Umbral como parámetro con prior; distribución posterior del cuantil 99,9 % promediando sobre el umbral.
- **Validación.** Cobertura de intervalos de cuantil en simulación con cola conocida.
- **Refutación.** Con pocos eventos extremos, la posterior puede depender del prior; la métrica de sensibilidad debe reportarse junto al VaR.
- **Fuente.** Pickands (1975) y McNeil & Frey (2000) [C].

### 5.3 XVA con aprendizaje diferencial para sensibilidades

**Tipo:** Extensión de `05-enterprise-risk-advisory/07-valuation-counterparty/xva`
- **Hipótesis.** Un modelo de red neuronal entrenado con gradientes (aprendizaje diferencial, Huge & Savine, 2020) reduce el costo computacional de XVA y sus sensibilidades.
- **Método.** Entrenar la red sobre valores y derivadas de la exposición; calcular CVA y sensibilidades.
- **Validación.** Error de CVA frente a Monte Carlo completo y error de sensibilidades.
- **Refutación.** El error de la red en cola puede ser sistemáticamente sesgado; las sensibilidades fuera del rango de entrenamiento son poco confiables.
- **Fuente.** [C].

### 5.4 Evaluación de LLM para clasificación de incidentes con métricas de calibración

**Tipo:** Extensión de `01-credit-risk/fraud-and-anomaly-research/ai-enabled-fraud-defense` (uso de LLM)
- **Hipótesis.** Un LLM clasifica incidentes operacionales con precisión comparable a un revisor humano, y sus probabilidades pueden calibrarse.
- **Método.** Clasificación con LLM y calibración con regresión isotónica o escalamiento de temperatura; revisión humana sobre una muestra estratificada.
- **Validación.** Concordancia (kappa de Cohen) con revisores humanos y error de calibración esperado (ECE).
- **Refutación.** Un buen desempeño en un conjunto de prueba puede no generalizar a incidentes nuevos. Las probabilidades calibradas en un dominio pueden descalibrarse en otro.
- **Fuente.** SR 26-2 como marco de gobierno de IA [V].

### 5.5 Pruebas de robustez para control continuo con conformal

**Tipo:** Extensión de `05-enterprise-risk-advisory/08-assurance-risk-data/continuous-controls`
- **Hipótesis.** Un control continuo con intervalos conformales de anomalía tiene una tasa de falsas alarmas controlada.
- **Método.** Puntajes conformales sobre residuos de control; umbral por cuantil de calibración.
- **Validación.** Tasa de falsas alarmas empírica frente a la nominal y potencia ante anomalías inyectadas.
- **Refutación.** La intercambiabilidad se rompe con estacionalidad o cambios en el proceso; hay que recalibrar por ventana.
- **Fuente.** [C].

### 5.6 Priorización de alertas de AML con probabilidades calibradas y costo asimétrico

**Tipo:** Extensión de `05-enterprise-risk-advisory/05-financial-crime/aml-alert-prioritization`
- **Hipótesis.** Un umbral de alerta optimizado con costo asimétrico (falso negativo mucho más caro) reduce pérdidas sin aumentar la carga operativa.
- **Método.** Probabilidad calibrada de alerta y umbral que minimiza el costo esperado \(C_{FN}\cdot FN + C_{FP}\cdot FP\).
- **Validación.** Curva de costo frente a umbral y pruebas por cohorte.
- **Refutación.** Los costos relativos son supuestos de negocio, no datos; el óptimo puede ser muy sensible a ellos.
- **Fuente.** [C].

### 5.7 Riesgo de transición climática con escenarios cortos NGFS
**Tipo:** Nueva
- **Hipótesis.** Los escenarios cortos de NGFS dan un efecto de transición en PD sectorial más visible en el horizonte de presupuesto que los escenarios de largo plazo.
- **Método.** Traducir un choque de precio de carbono a cambios de PD por sector con una relación de elasticidad estimada.
- **Validación.** Sensibilidad del efecto a la elasticidad; comparación de horizontes.
- **Refutación.** La elasticidad sectorial se estima con poca historia; los escenarios no son pronósticos.
- **Fuente.** ECB, Macroprudential Bulletin 2025/11, sobre escenarios cortos de NGFS [V, lead de búsqueda].

### 5.8 Cargo de capital por riesgo de modelo con promedio bayesiano de modelos
**Tipo:** Nueva
- **Hipótesis.** La incertidumbre de especificación entre modelos alternativos se traduce en un cargo de capital cuantificable.
- **Método.** Promedio bayesiano de modelos con pesos posteriores; capital adicional como el cuantil de la pérdida ponderada.
- **Validación.** Cobertura del capital bajo modelos conocidos en simulación.
- **Refutación.** Los pesos bayesianos dependen del prior y del conjunto de modelos elegido; un conjunto incompleto subestima el cargo.
- **Fuente.** Hoeting et al. (1999), promedio bayesiano de modelos [C].

### 5.9 Monitoreo secuencial de equidad con e-values
**Tipo:** Nueva
- **Hipótesis.** Un monitoreo secuencial con e-values detecta impacto dispar en decisiones automatizadas sin inflar el error tipo I.
- **Método.** Test secuencial basado en e-values sobre la diferencia de tasas de aprobación entre grupos, actualizado con cada lote.
- **Validación.** Error tipo I bajo nulo y potencia ante un sesgo inyectado.
- **Refutación.** La prueba detecta diferencias, no causas; el impacto dispar puede venir de variables legítimas correlacionadas.
- **Fuente.** Ramdas et al. (2023), e-values [C].

### 5.10 Error de medición en RCSA
**Tipo:** Nueva
- **Hipótesis.** Las evaluaciones de RCSA contienen error de medición entre evaluadores que se estima con un modelo bayesiano jerárquico.
- **Método.** Modelo de efectos aleatorios por evaluador y riesgo, con varianza de medición estimada.
- **Validación.** Recuperación de la varianza de medición en simulación; intervalos de la calificación por riesgo.
- **Refutación.** Si los evaluadores son los mismos para todos los riesgos, el error se confunde con el efecto del riesgo.
- **Fuente.** [C].

### 5.11 Subregistro de eventos operacionales con captura-recaptura
**Tipo:** Nueva
- **Hipótesis.** Los eventos operacionales no reportados se estiman con un método de captura-recaptura entre dos fuentes independientes de registro.
- **Método.** Estimador de Lincoln-Petersen (o Chapman) sobre las dos fuentes, con intervalo de confianza.
- **Validación.** Cobertura del intervalo en simulación con subregistro conocido.
- **Refutación.** El método exige independencia entre fuentes; si ambas dependen del mismo proceso, subestima el subregistro.
- **Fuente.** Chapman (1951) [C].

### 5.12 Muestreo bayesiano adaptativo para pruebas de control
**Tipo:** Nueva
- **Hipótesis.** Un muestreo bayesiano adaptativo prueba la efectividad de un control con menos muestras que el muestreo estadístico fijo.
- **Método.** Actualizar la probabilidad de falla del control por lote y detener la prueba cuando la posterior cruza un umbral.
- **Validación.** Tamaño de muestra promedio frente al muestreo fijo, con error de decisión controlado.
- **Refutación.** Un prior demasiado optimista reduce el tamaño de muestra pero aumenta el riesgo de aceptar un control defectuoso.
- **Fuente.** [C].

---

## 06 · Motor de investigación cuantitativa (`06-quantitative-research-engine`)

### 6.1 Verificación de la matriz de correlación con proyección al cono PSD

**Tipo:** Extensión de `06-quantitative-research-engine` (verificación PSD declarada pendiente)
- **Hipótesis.** La matriz de correlación estimada se puede corregir al cono de semidefinidas positivas con la mínima distorsión (proyección de Higham, 2002), y el riesgo cambia poco.
- **Método.** Proyección de Higham sobre la matriz de covarianza; medir la distancia de Frobenius y el cambio en la varianza de pérdida.
- **Validación.** Cambio en la pérdida al 99 % frente a la distancia de proyección.
- **Refutación.** La proyección puede cambiar las marginales de Bernoulli; el README del motor ya advierte que la PSD no se certifica, y esta idea lo resuelve solo parcialmente.
- **Fuente.** Higham (2002) [C].

### 6.2 Monte Carlo multinivel para la cola de pérdida

**Tipo:** Nueva
- **Hipótesis.** El Monte Carlo multinivel (Giles, 2008) reduce el costo de estimar cuantiles de cola para un nivel de error dado.
- **Método.** Estimadores de nivel con discretización de pasos finos y gruesos sobre la dinámica de factores.
- **Validación.** Costo versus error frente a Monte Carlo estándar.
- **Refutación.** Las ganancias dependen de la correlación entre niveles; para cuantiles, el sesgo es más difícil de controlar que para medias.
- **Fuente.** Giles (2008) [C].

### 6.3 Muestreo por importancia con factor condicional para eventos raros

**Tipo:** Extensión de `01-credit-risk/credit-portfolio-strategy/discrete-credit-tail-audit`
- **Hipótesis.** El muestreo por importancia con desplazamiento del factor común (Glasserman & Li, 2005) reduce la varianza del estimador de pérdida extrema.
- **Método.** Desplazar la media del factor latente hacia la región de pérdida alta, con pesos de verosimilitud.
- **Validación.** Varianza del estimador frente a Monte Carlo ingenuo y cobertura del intervalo.
- **Refutación.** Un desplazamiento mal elegido puede aumentar la varianza; el peso puede degenerar.
- **Fuente.** Glasserman & Li (2005) [C].

### 6.4 Secuencias cuasi-Monte Carlo con aleatorización de Owen

**Tipo:** Nueva
- **Hipótesis.** Las secuencias de Sobol con aleatorización de Owen dan errores de cuantil menores que el Monte Carlo para la misma muestra.
- **Método.** Sobol aleatorizado (Owen) con repeticiones independientes para estimar el error.
- **Validación.** Error del cuantil frente al número de muestras y comparación con Monte Carlo puro.
- **Refutación.** Con muchas dimensiones efectivas, la ventaja de cuasi-Monte Carlo se pierde.
- **Fuente.** Owen (1998) [C].

### 6.5 Pruebas de paridad Python-C++ basadas en propiedades

**Tipo:** Extensión de `02-market-and-model-risk/weighted-tail-underflow-guard/tests`
- **Hipótesis.** Las pruebas basadas en propiedades (invariantes del motor) detectan discrepancias entre Python y C++ que las pruebas de casos fijos no detectan.
- **Método.** Generar entradas aleatorias con reglas de propiedad (monotonía de la pérdida frente a PD, linealidad de E[L]) y comparar salidas.
- **Validación.** Número de discrepancias encontradas frente a pruebas fijas existentes.
- **Refutación.** Las propiedades deben ser correctas; una propiedad incorrecta produce falsas alarmas.
- **Fuente.** [C].

### 6.6 Diferenciación automática para sensibilidades de capital

**Tipo:** Nueva
- **Hipótesis.** La diferenciación automática da sensibilidades de capital (Euler) exactas y más rápidas que diferencias finitas.
- **Método.** Diferenciación automática sobre el estimador de pérdida y asignación de Euler; validación contra diferencias finitas con paso controlado.
- **Validación.** Error relativo de la sensibilidad frente a diferencias finitas.
- **Refutación.** Las funciones con discontinuidades (como umbrales de pérdida) dan gradientes mal definidos.
- **Fuente.** [C].

### 6.7 Procedencia reproducible con hash de datos y semillas
**Tipo:** Nueva
- **Hipótesis.** Cada resultado del motor es reproducible bit a bit a partir de un registro de hash de datos, versión de código y semillas.
- **Método.** Manifiesto de ejecución con hash de entradas, versión del código y semillas; verificación al re-ejecutar.
- **Validación.** Reproducibilidad bit a bit entre máquinas y compiladores con la misma entrada.
- **Refutación.** La reproducibilidad bit a bit no garantiza exactitud; un error sistemático se reproduce igual.
- **Fuente.** [C].

### 6.8 Recálculo incremental de sensibilidades
**Tipo:** Nueva
- **Hipótesis.** Al cambiar un solo exposición, el recálculo incremental de la pérdida y de las sensibilidades es más rápido que recalcular todo el portafolio.
- **Método.** Actualizar sumas parciales de pérdida y de sensibilidades por exposición afectada; verificación contra el cálculo completo.
- **Validación.** Igualdad con el cálculo completo dentro de tolerancia y tiempo de cómputo frente al total.
- **Refutación.** Cuando la correlación cambia para muchas exposiciones a la vez, la ganancia desaparece.
- **Fuente.** [C].

### 6.9 Error de redondeo con precisión mixta
**Tipo:** Nueva
- **Hipótesis.** Usar precisión simple en la simulación y doble en la acumulación de pérdida reduce el costo sin degradar la cola de pérdida.
- **Método.** Comparar el error de la cola al 99,9 % con precisión mixta frente a precisión doble completa.
- **Validación.** Error relativo del cuantil frente a la referencia de precisión doble.
- **Refutación.** En portafolios con exposiciones muy desiguales, la precisión simple puede perder masa de cola (el riesgo de underflow ya documentado en el repositorio).
- **Fuente.** [C] (análisis de error de punto flotante, Higham, 2002).

---

## 07 · Riesgo financiero y de construcción (`07-financial-and-construction-risk-lab`)

### 7.1 Simulación de cronograma y costo con dependencia por cópula

**Tipo:** Extensión de `07-financial-and-construction-risk-lab/02-construction-enterprise-risk/02-schedule-cost-overrun`
- **Hipótesis.** Modelar las duraciones de actividades con dependencia por cópula, y no como independientes, cambia la distribución del retraso total y del costo.
- **Método.** Red de actividades con duraciones correlacionadas por cópula gaussiana o t; ruta crítica en cada simulación.
- **Validación.** Diferencia entre el retraso con independencia y con dependencia; sensibilidad a la correlación.
- **Refutación.** La correlación entre actividades se estima con juicio de expertos, no con datos; el resultado puede ser un artefacto del supuesto.
- **Fuente.** [C].

### 7.2 Regresión de cuantiles con bosques para costos de proyecto

**Tipo:** Nueva
- **Hipótesis.** Los bosques de cuantiles estiman el costo final con intervalos calibrados mejor que un modelo lineal con varianza constante.
- **Método.** Bosques de regresión por cuantiles (Meinshausen, 2006) [C].
- **Validación.** Cobertura de los intervalos por tipo de proyecto y ancho medio.
- **Refutación.** Con pocos proyectos completados, el modelo aprende muy poco; los bosques no extrapolan fuera del rango de entrenamiento.
- **Fuente.** [C].

### 7.3 Modelo de factores dinámicos para índices de costo de materiales

**Tipo:** Extensión de `07-financial-and-construction-risk-lab/03-research-in-progress/04-bayesian-construction-nowcasting`
- **Hipótesis.** Un modelo de factores dinámicos con datos mensuales de precios de insumos mejora el pronóstico de inflación de costos de construcción.
- **Método.** Factores dinámicos (Giannone et al., 2008, para nowcasting) con datos mensuales y rezagos mixtos (MIDAS).
- **Validación.** Error de pronóstico fuera de muestra frente a un modelo univariado y a un paseo aleatorio.
- **Refutación.** Los precios de insumos colombianos pueden tener baja frecuencia o cambios de base; el resultado depende de la calidad del índice.
- **Fuente.** [C].

### 7.4 Alerta temprana de sobrecostos con regla de parada en línea

**Tipo:** Extensión del método CUSUM de `01-credit-risk/fraud-and-anomaly-research/04-origination-process-anomalies`, aplicado a construcción
- **Hipótesis.** Una regla de parada secuencial (CUSUM) detecta el sobrecosto antes que el control mensual de avance.
- **Método.** CUSUM sobre la diferencia entre costo real y costo planeado ajustado por avance; calibrar la alarma con ARL.
- **Validación.** ARL₀ y ARL₁ frente a sobrecostos inyectados.
- **Refutación.** La varianza de costos es heterocedástica; un CUSUM con varianza constante genera alarmas falsas en fases de alto gasto.
- **Fuente.** [C].

### 7.5 Impacto de la liquidez del promotor sobre el riesgo de construcción

**Tipo:** Extensión de `07-financial-and-construction-risk-lab/03-research-in-progress/05-network-contagion-contractors`
- **Hipótesis.** La probabilidad de incumplimiento del contratista depende de la liquidez del promotor. Ese vínculo se cuantifica con un modelo de contagio entre contratista y promotor.
- **Método.** Modelo de dos nodos con choques correlacionados y transferencia de pérdida por exposición; la estimación se hace con datos de pagos.
- **Validación.** Pérdida conjunta en simulación frente al caso sin contagio.
- **Refutación.** Los datos de exposición entre promotor y contratista suelen ser privados; el resultado depende de supuestos fuertes de exposición.
- **Fuente.** [C].

### 7.6 Valor de la flexibilidad (opciones reales) con aprendizaje por regresión

**Tipo:** Extensión de `07-financial-and-construction-risk-lab/03-research-in-progress/07-real-options-staged-development`
- **Hipótesis.** El valor de la opción de etapificar un proyecto se estima con la regresión de Longstaff-Schwartz (2001) con un error de aproximación menor que el de la cota inferior simple.
- **Método.** Método de mínimos cuadrados de Monte Carlo para la opción de posponer o abandonar; comparar con árbol binomial.
- **Validación.** Convergencia con el número de trayectorias y comparación con el árbol.
- **Refutación.** Los parámetros del proceso de demanda son el principal motor del valor, y suelen tener muy poca identificación.
- **Fuente.** Longstaff & Schwartz (2001) [C].

### 7.7 Asignación de cuadrillas con aprendizaje por refuerzo profundo
**Tipo:** Nueva
- **Hipótesis.** Una política aprendida por refuerzo profundo asigna cuadrillas bajo retrasos inesperados y reduce el atraso total frente a una regla fija.
- **Método.** Entorno de simulación de obra con retrasos estocásticos; política de asignación con aprendizaje por refuerzo profundo.
- **Validación.** Atraso total frente a una regla fija de prioridad en escenarios fuera de entrenamiento.
- **Refutación.** La política puede especializarse en el simulador; sin validación en escenarios no vistos el resultado no se transfiere.
- **Fuente.** Asignación de mano de obra con aprendizaje por refuerzo profundo en construcción, Universidad de Birmingham [V, lead de búsqueda].

### 7.8 Detección de sobrecostos con transformadores sobre registros de obra
**Tipo:** Nueva
- **Hipótesis.** Un modelo de secuencia sobre registros diarios de obra anticipa sobrecostos mejor que un modelo sobre indicadores mensuales.
- **Método.** Entrada: secuencia diaria de avance, costo y eventos; salida: probabilidad de sobrecosto a 60 días.
- **Validación.** Validación por proyecto (no por fecha) para evitar fuga entre registros del mismo proyecto.
- **Refutación.** Con pocos proyectos completados la red sobreajusta; la validación por proyecto puede dejar muy pocas muestras.
- **Fuente.** [C].

### 7.9 Detección de fraude en precios unitarios de obra
**Tipo:** Nueva
- **Hipótesis.** Los precios unitarios que se alejan de la distribución condicional por tipo de obra y región señalan sobrefacturación.
- **Método.** Regresión cuantílica del precio unitario sobre tipo de obra y región; marcar valores por encima del cuantil 99.
- **Validación.** Tasa de alarmas frente a una auditoría de muestra; sensibilidad al cuantil elegido.
- **Refutación.** Un precio alto puede ser legítimo (ubicación, especificación); las alarmas requieren revisión humana.
- **Fuente.** [C] (regresión cuantílica, Koenker y Bassett, 1978).

### 7.10 Penalidades en contratos de obra con teoría de juegos
**Tipo:** Nueva
- **Hipótesis.** La penalidad óptima por retraso equilibra el incentivo del contratista con la cobertura del promotor.
- **Método.** Modelo principal-agente con esfuerzo no observable y penalidad lineal o por tramos; equilibrio de Nash en el contrato.
- **Validación.** Comparación de penalidades óptimas frente a penalidades fijas en simulación.
- **Refutación.** La penalidad óptima puede ser impracticable legalmente; el modelo ignora la posibilidad de litigio.
- **Fuente.** Holmström y Milgrom (1991), principal-agente multitarea [C].

### 7.11 Rotación de mano de obra con modelo de Markov
**Tipo:** Nueva
- **Hipótesis.** La rotación de la mano de obra sigue una cadena de Markov con tasa dependiente de la etapa de la obra; su costo se estima con la matriz de transición.
- **Método.** Estimar la matriz de transición mensual entre estados (activo, rotado, fuera) y el costo esperado por reposición.
- **Validación.** Error de predicción de la plantilla frente a registros de nómina.
- **Refutación.** La rotación depende de factores externos (mercado laboral) que la cadena no incorpora.
- **Fuente.** [C].

---

## Notas de verificación y limitaciones

- **Fuentes primarias verificadas en esta búsqueda:** carta SR 26-2 de la Reserva Federal (17-abr-2026, reemplaza SR 11-7 y SR 21-8). Para aplicarla fuera de EE. UU. se necesita revisar el anexo técnico completo, que no se leyó aquí.
- **Fuentes secundarias encontradas:** los artículos de arXiv citados (2607.17381, 2607.16970, 2509.05922, 2508.02183, 2309.12384) y el de Davidov et al. (ICLR 2025). Se leyeron los resúmenes, no los textos completos. Antes de usar cualquier resultado cuantitativo, hay que leer el artículo completo.
- **Búsqueda sobre la SFC:** no encontré documentación regulatoria reciente y específica para modelos de pérdida esperada en Colombia. Esa búsqueda debe repetirse con términos más precisos (circulares externas, Capítulo XXXI de la Circular Básica Contable y Financiera).
- **Tratamiento de la literatura clásica:** las referencias marcadas [C] son conocidas pero no se verificaron en esta sesión. Deben citarse con su fuente original antes de cualquier uso formal.
- **Prioridad sugerida:** 1.1 (conformal ECL), 2.2 (validación de IA bajo SR 26-2), 3.1 (regiones de insolvencia), 4.1 (bosques causales) y 6.3 (importancia para cola). Son las de mayor impacto por esfuerzo y las de mejor respaldo en la literatura reciente.

---

## Revisión de solapamientos con el repositorio

**Criterio:** Nueva = no hay trabajo equivalente en el repositorio. Extensión = la idea se solapa con un proyecto existente y se presenta como extensión de ese proyecto, no como proyecto aparte.

**Resumen:** de la primera revisión, 12 nuevas y 30 extensiones de proyectos existentes. Las 30 ideas añadidas (1.7–7.11) se diseñaron para no solaparse con el repositorio y no están en esta tabla. Las extensiones se identifican en cada idea con la ruta del proyecto que amplían.

| # | Idea | Tipo | Referencia en el repositorio |
|---|---|---|---|
| 1.1 | Conformal survival para ECL | Nueva | El conformal solo aparece en KYC (`channel-conformal-audit`) |
| 1.2 | BOCPD para cosechas | Extensión | CUSUM en `fraud-and-anomaly-research/04-origination-process-anomalies` |
| 1.3 | PD con Lévy-OU | Nueva | Sin referencias |
| 1.4 | Cópulas t/Clayton y Wasserstein | Extensión | `credit-portfolio-strategy/copula-gaussiana-perdidas` |
| 1.5 | Semi-Markov en roll rates | Extensión | `credit-risk-products/matrices-de-transicion-roll-rates` (Markov) |
| 1.6 | Monotonía en GBM y equidad | Extensión | `scorecard-logistico-woe` ya fuerza monotonía en WoE; sin equidad |
| 2.1 | Backtesting de ES (Acerbi–Székely) | Extensión (gap declarado) | `weighted-expected-shortfall-audit`: "no se ejecuta backtesting Acerbi–Szekely" |
| 2.2 | Validación de IA generativa (SR 26-2) | Extensión | `05/04-cyber-ai/ai-governance`; el repositorio no cita SR 11-7 ni SR 26-2 |
| 2.3 | Escenarios con modelos generativos | Nueva | Sin referencias |
| 2.4 | VaR con cobertura adaptativa | Nueva | Sin referencias |
| 2.5 | Riesgo de modelo entre familias GARCH | Extensión | `garch-volatilidad-y-var` (solo GARCH(1,1)) |
| 2.6 | Bootstrap de diferencial de Gini | Extensión | `validacion-de-modelo-psi-gini` |
| 3.1 | Regiones de insolvencia con HJB | Nueva | `03_LIQUIDEZ_ESTOCASTICA.md` discute déficit, sin control óptimo |
| 3.2 | LVaR con impacto | Extensión | `05_OPTIMIZACION_LIQUIDEZ.md` tiene costo de liquidación |
| 3.3 | Hawkes en margin calls | Nueva | `04_ESPIRALES_LIQUIDEZ.md` usa impacto lineal sin autoexcitación |
| 3.4 | Resiliencia del libro de órdenes | Nueva | Sin referencias |
| 3.5 | CVaR con DRO | Extensión | `05_OPTIMIZACION_LIQUIDEZ.md` (CVaR con costos); DRO es nuevo |
| 3.6 | ML causal para valles de mercado | Nueva | Sin referencias en mercado |
| 4.1 | Bosques causales para aprobación | Extensión | `04-advanced-research/01-causal-origination-policy` |
| 4.2 | HMM para regímenes | Extensión | `04-advanced-research/02-nonstationary-credit-digital-twin` (método alternativo) |
| 4.3 | RL offline para cobranza | Extensión | `04-advanced-research/03-collections-dynamic-treatment-regimes` (mismo marco) |
| 4.4 | SICR con conformal | Extensión | `04-advanced-research/04-ifrs9-forward-looking-ecl` |
| 4.5 | Eisenberg–Noe | Extensión | `03/04_ESPIRALES_LIQUIDEZ.md` la menciona; `04-advanced-research/05-siar` |
| 4.6 | Control con CMDP y Lagrange | Extensión | `04-advanced-research/07-capital-constrained-portfolio-control` |
| 5.1 | Brecha de MRM frente a SR 26-2 | Extensión | `04-cyber-ai/ai-governance`; sin SR 11-7 en el repositorio |
| 5.2 | Umbral bayesiano en POT | Extensión | `03-operational-resilience/operational-extreme-tail` (sin prior sobre el umbral) |
| 5.3 | XVA con aprendizaje diferencial | Extensión | `07-valuation-counterparty/xva` (sin diferencial) |
| 5.4 | LLM para incidentes operacionales | Extensión | `fraud-and-anomaly-research/ai-enabled-fraud-defense` (LLM en fraude) |
| 5.5 | Control continuo con conformal | Extensión | `08-assurance-risk-data/continuous-controls` |
| 5.6 | Alertas AML con costo asimétrico | Extensión (verificar) | `05-financial-crime/aml-alert-prioritization` (verificar contenido) |
| 6.1 | Proyección de Higham a PSD | Extensión (gap declarado) | README del motor: "no certifica que C sea PSD" |
| 6.2 | Monte Carlo multinivel | Nueva | Sin referencias |
| 6.3 | Muestreo por importancia | Extensión | `discrete-credit-tail-audit` (verificar implementación) |
| 6.4 | Sobol con aleatorización de Owen | Nueva | Sin referencias |
| 6.5 | Pruebas de propiedades y paridad | Extensión | `weighted-tail-underflow-guard/tests` |
| 6.6 | Diferenciación automática | Nueva | Sin referencias |
| 7.1 | Cronograma con cópula | Extensión | `02-construction-enterprise-risk/02-schedule-cost-overrun` |
| 7.2 | Bosques de cuantiles para costos | Nueva | Sin referencias en construcción |
| 7.3 | Factores dinámicos y MIDAS | Extensión | `03-research-in-progress/04-bayesian-construction-nowcasting`; `06-materials-inflation` |
| 7.4 | CUSUM para sobrecostos | Extensión | CUSUM solo en fraude; no en construcción |
| 7.5 | Contagio promotor-contratista | Extensión | `03-research-in-progress/05-network-contagion-contractors`, `06-construction-network-contagion`, `02/04-contractor-counterparty-risk` |
| 7.6 | Opciones reales con LSM | Extensión | `03-research-in-progress/07-real-options-staged-development` |

### Prioridad sugerida tras la revisión
1. **2.1 (backtesting de ES):** gap declarado por el propio repositorio, con literatura conocida.
2. **6.1 (proyección PSD):** el README del motor pide justamente esta verificación.
3. **1.1 (conformal survival para ECL):** nueva y de alto impacto para IFRS 9.
4. **3.3 (Hawkes en margin calls):** complementa directamente `04_ESPIRALES_LIQUIDEZ.md`.
5. **2.4 (VaR conformal adaptativo):** nueva y verificable con los backtests existentes.

### Límites de esta revisión
- Se revisaron títulos, README y palabras clave, no el código ni los resultados de cada subcarpeta. Las marcas "verificar" necesitan una lectura de código.
- Las coincidencias por palabra clave pueden ser falsos positivos. Por eso, cada entrada de la tabla se contrastó con el texto del archivo referido cuando fue posible.
