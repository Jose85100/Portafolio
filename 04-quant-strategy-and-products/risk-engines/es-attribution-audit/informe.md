# Atribución Euler de ES sobre escenarios finitos

**Nota de investigación de 14 puntos.** Corte: 10 de noviembre de 2026. Base: `4684267` (`origin/main`). Alcance: MVP cuantitativo, no dictamen regulatorio ni recomendación de límites.

## 1. Decisión de producto

Se recomienda continuar solo como prototipo de analítica de contribuciones. La medida responde a “qué componentes explican la cola del portafolio simulado” cuando ya existe una distribución de escenarios. No estima por sí misma cómo se comportará el portafolio futuro.

## 2. Hueco de la base

La revisión de `risk-engines` muestra los motores existentes de crédito, mercado, liquidez, ES ponderado y auditorías de backtesting/flujo descontado. El ES agregado se puede calcular; una interfaz de contribución por componente a ese ES, incluyendo átomo fraccionario de VaR, no apareció en las rutas revisadas. Los paquetes de 03 cubren GARCH, EVT, backtesting, datos observados/proxies y liquidez. Evitamos repetir la estimación de ES y resolvemos solamente la atribución sobre escenarios provistos.

## 3. Alternativas comparadas

Se compararon tres ideas. Un generador multiactivo con correlación sería útil, pero repite el generador de risk-engines y la historia TRM no basta para calibrar activos. FHS/GARCH/EVT tiene solapamiento directo con investigación de mercado existente y depende de validación histórica. Atribución ES Euler utiliza el resultado existente como funcional de cola y permite una prueba verificable sin acceso a Drive; fue seleccionada.

## 4. Fuentes y disciplina de datos

La SFC publicó la Circular Básica Financiera CE 004/2026 y un índice con administración de riesgos; su versión fue modificada el 8 de octubre de 2026. Basilea MAR33 define ES unilateral 97,5% y un ajuste de horizontes de liquidez para el IMA. BanRep define metodología TRM con base en Resolución Externa 1/2018, art. 40, y documenta su fuente estadística. Estas referencias informan límites y futuro linaje de datos; **el experimento no descargó ni usó datos empíricos**. No se atribuye conformidad SFC, Basilea, LCR/NSFR o IFRS 9.

## 5. Modelo y derivación

Sean (x_{si}) las pérdidas del componente (i) en escenario (s), (L_s=\sum_i x_{si}), pesos positivos (p_s) y masa total (P=\sum_s p_s). La cuantila es (q_\alpha=\inf\{x:F_L(x)\ge\alpha\}). Para una medida discreta, ES se expresa por masa de cola superior fraccionando el átomo de cuantila:

\[
ES_\alpha(L)=\frac{\sum_s p_s(L_s>q_\alpha)L_s+
\left[(1-\alpha)P-\sum_s p_s(L_s>q_\alpha)\right]q_\alpha}{(1-\alpha)P}.
\]

Equivalentemente, cada escenario recibe peso de cola (a_s\ge0), con suma uno; los escenarios por encima de (q_\alpha) conservan su peso proporcional y el faltante se distribuye entre empates en (q_\alpha) en proporción a (p_s). La contribución es (C_i=\sum_s a_sx_{si}). Por linealidad, (\sum_i C_i=ES_\alpha(L)). Para pérdidas lineales y distribución fija, esto coincide con la derivada Euler (C_i=w_i\partial ES(L(w))/\partial w_i) en puntos diferenciables; con empates, la selección de subgradiente queda fijada por reparto proporcional. El algoritmo ordena escenarios, costo (O(n\log n+nk)), memoria (O(nk)).

## 6. Interpretación de unidades

Las contribuciones usan las mismas unidades que `component_losses`; en el experimento son unidades de pérdida proxy sin moneda. La suma de columnas de cada escenario forma pérdida de cartera. Cambiar moneda requeriría convertir antes de simular, no etiquetar a posteriori. Pesos son multiplicadores relativos de probabilidad, estrictamente positivos; su escala común no altera el resultado. El alfa no tiene unidad.

## 7. Datos, proxy y observación

Las cinco mil filas son simulaciones sintéticas (semilla 20261110), no observaciones, proxy empírico o datos proporcionados por SFC/BanRep. Una crisis común Bernoulli al 2,5% induce dependencia y cola superior. La intensidad, la correlación y la frecuencia son parámetros didácticos, no estimados. Se guardan las realizaciones exactas en CSV para inspección y regeneración.

## 8. Resultado principal y baseline

En el corte alfa .975, ES es 9.4097 unidades y VaR 4.2892. Las contribuciones Euler de FX, tasa y equity son 3.4198, 3.2481 y 2.7418; suman ES con error cero en el cálculo binary64 de esta corrida. La comparación prorrata de ES standalone produce 3.1685, 3.0235 y 3.2177: es una regla de asignación alternativa, no un oráculo para atribución marginal. La ablación de promedio total simple produce importes cercanos a cero y no responde la pregunta de cola.

## 9. Sensibilidad

`results/sensitivity.csv` cambia alfa de 90%, 95%, 97.5% y 99% sobre la misma muestra, y escala shocks del régimen de crisis por 0, 0.5, 1 y 1.5 manteniendo eventos y aleatorios fijos. Son sensibilidades de diseño, no intervalos de confianza. Al borrar el régimen de crisis (ablación adversa), ES cae de 9.4097 a 4.7701, evidencia que la salida depende materialmente del escenario extremo sintético. Esto no estima la severidad de eventos reales.

## 10. Pruebas y oráculo

Las pruebas incluyen caso analítico con masa fraccionaria, traslación por adición componente a componente, homogeneidad positiva, permutación de escenarios, pesos equivalentes a replicación entera (100 realizaciones deterministas aleatorias) e invalidaciones. Ese oráculo de replicación independiente contrasta cálculo ponderado con expansión explícita. No es Hypothesis con shrinker; la semilla de prueba fija hace reproducible la propiedad.

## 11. Riesgo numérico y casos extremos

El cálculo usa `float` binario; no reivindica exactitud decimal. Se rechazan alfas fuera de (0,1), pérdidas no finitas, matrices irregulares y pesos no positivos/no finitos. La tolerancia de cruce de cuantil es `1e-14`; por tanto, pesos extremadamente dispares cercanos a epsilon pueden afectar selección de átomo. Producción precisaría escalado robusto, acumulación compensada, pruebas de pesos subnormales y contrato de tolerancia específico.

## 12. Límites prudenciales

La CBF colombiana establece gestión de riesgo de mercado y metodologías determinadas según entidad/caso. Basel MAR33 requiere más que ES aislado: 97,5%, reglas de escenarios, horizontes de liquidez y componentes adicionales para requerimiento de capital. Esta herramienta no implementa dichos requisitos, agregación de factores ni metodología estándar SFC; tampoco calcula LCR/NSFR, ECL o etapa IFRS 9. Uso recomendado: investigación fuera de línea con etiqueta prototipo.

## 13. Madurez, controles y riesgo operativo

Madurez aproximada TRL 2–3. Antes de cualquier piloto se necesitan adapter a shocks observados con provenance, catálogo de instrumentos/factores, transformación de P&L, calendario/horizonte, tratamiento de divisas, control de cambios de pesos, registro reproducible, reconciliación independiente y validación de modelos. La atribución puede ser engañosa si las columnas no suman exactamente al P&L total o si sus nombres/posiciones cambian.

## 14. Falsación y roadmap

El MVP falla si deja de reconciliar contribuciones a ES, si difiere del oráculo de replicación más allá de tolerancia o si los insumos no son aditivos. Próxima etapa: integrar una serie diaria autorizada (TRM como solo un factor), definir escenarios de P&L multiactivo y ventana out-of-sample, comparar impactos por factor bajo horizontes explícitos y obtener revisión independiente. Solo luego evaluar conexión con informes internos y requisitos SFC. No se propone usarlo para capital regulatorio antes de determinar alcance legal y metodología aplicable.
