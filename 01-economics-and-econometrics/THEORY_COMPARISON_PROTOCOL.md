# Protocolo de confrontación de escuelas económicas

La comparación debe hacerse por **predicciones condicionales**, no por preferencias doctrinales. Una escuela puede ofrecer una explicación útil en cierto horizonte o fricción y fallar en otros. El objetivo es identificar qué observaciones podrían discriminar mecanismos.

| Disciplina | Mecanismo A | Mecanismo B | Predicción discriminante | Amenaza de identificación |
|---|---|---|---|---|
| Macroeconomía | Nueva síntesis neoclásica: expectativas racionales y rigideces nominales | Información rígida / expectativas adaptativas | Persistencia y velocidad de incorporación de noticias en inflación | Shocks de oferta y endogeneidad monetaria |
| Microeconomía | Elección racional y preferencias estables | Atención limitada y sesgos conductuales | Cambios de elección ante encuadre con incentivos constantes | Selección y preferencias no observadas |
| Teoría de juegos | Equilibrio de Nash estático | Aprendizaje adaptativo / dinámica evolutiva | Trayectoria y dependencia del historial, no solo estado final | Equilibrios múltiples y reglas de actualización |
| Econometría | Tendencias paralelas en DiD | Tendencias diferenciales / selección dinámica | Divergencia de resultados bajo placebos y controles alternativos | Pretrends con baja potencia |
| Macrofinanzas | Defaults independientes condicionalmente | Factor común y contagio | Frecuencia de pérdidas conjuntas extremas | Observación escasa de colas |

## Ficha obligatoria para cada teoría
1. **Afirmación precisa** con cuantificadores y dominio.
2. **Supuestos** necesarios y suficientes, si se conocen.
3. **Derivación** y límites de existencia/unicidad.
4. **Vertientes** y qué supuesto modifica cada una.
5. **Contraejemplo** dentro de los supuestos (refuta la proposición) o fuera de ellos (delimita alcance).
6. **Diseño de identificación** y predicciones observables.
7. **Experimento computacional** con parámetros, semillas, benchmark y tolerancias.
8. **Falsaciones** y pruebas de robustez.
9. **Implicaciones de bienestar y riesgo** con intervalos de incertidumbre.
10. **Estado de evidencia**: teórico, simulado, empírico o validado independientemente.

### Ejemplo: neutralidad monetaria
La neutralidad a largo plazo no implica neutralidad a corto plazo. Un modelo de precios flexibles con expectativas racionales y uno con rigideces nominales generan respuestas reales diferentes ante shocks monetarios transitorios. El contraste exige identificación de shocks exógenos, no correlaciones entre oferta monetaria y producto. Con inflación fiscal, restricciones financieras o no linealidades, las predicciones dependen de supuestos adicionales.

### Ejemplo: selección adversa en crédito
Un aumento del tipo de interés puede modificar la composición de solicitantes, no solo reducir demanda. Comparar modelos de información simétrica, racionamiento por selección adversa y modelos con scoring observable. Observar una elasticidad negativa no identifica cuál mecanismo opera.

### Referencias de partida (verificar edición y alcance al citar)
Keynes, *The General Theory*; Lucas (1972), *Expectations and the Neutrality of Money*; Kydland & Prescott (1982), *Time to Build and Aggregate Fluctuations*; Woodford (2003), *Interest and Prices*; Galí (2015), *Monetary Policy, Inflation, and the Business Cycle*; Stiglitz & Weiss (1981), *Credit Rationing in Markets with Imperfect Information*; Kahneman & Tversky (1979), *Prospect Theory*; Angrist & Pischke (2009), *Mostly Harmless Econometrics*; Callaway & Sant'Anna (2021), *Difference-in-Differences with Multiple Time Periods*.
