# Informe ejecutivo: EVSI con costo de demora

Fecha de corte: 10 de noviembre de 2026. Caso ilustrativo sintético, unidades abstractas.

---

## Página 1 — Decisión ejecutiva

La decisión que aborda el gate es si la dirección debe actuar ahora con la alternativa de precio de mayor valor esperado o invertir en un piloto que retrasa la captura de contribución. El EVSI estándar cuantifica el valor de poder cambiar la decisión después de observar datos, pero un experimento toma tiempo. Al acortar el horizonte comercial disponible, el piloto puede perder frente a una decisión inmediata aun si su EVSI antes del costo es positivo.

La recomendación analítica es usar el gate con horizonte finito para discusiones de CEO, y tratar el EVSI estático como referencia/ablación. El valor se calcula exactamente para dos brazos conjugados Beta-Binomial, bajo supuestos transparentes. Ninguna cifra de esta carpeta representa ventas, conversiones, precios observados ni costos de una empresa.

## Página 2 — Contexto heredado y pregunta

El programa previo `pricing-pilot-evsi-gate` resolvía una pregunta estrecha: cuánto valor esperado de decisión produce una muestra aleatoria de dos precios, descontando costo del piloto. Su sensibilidad del 5 de noviembre encontró dependencia material de la concentración del prior y dejó explícitamente pendiente el costo contractual de demora. Este incremento toma esa brecha como problema de dirección: al pedir evidencia, la empresa posterga una decisión comercial y posiblemente renuncia a parte del horizonte.

La pregunta ahora es: dado un horizonte H, demora d, muestra n y costo c, ¿la expectativa de mayor calidad decisional compensa la pérdida de periodos de contribución?

## Página 3 — Opciones comparadas

Se compararon tres reglas. La primera elige hoy el mejor margen esperado del prior y conserva todo el horizonte. Es simple y representa el costo de oportunidad de esperar. La segunda ejecuta piloto cuando EVSI estático supera el costo; es la regla anterior, pero ignora que los datos llegan después. La tercera compara el valor neto del piloto demorado contra el valor de lanzar hoy.

La tercera es preferible para gobernanza ejecutiva porque usa un mismo horizonte en ambas opciones. La segunda se conserva como ablación negativa: muestra el riesgo específico de omitir demora. No se propone automatizar ni ejecutar un piloto a clientes reales con estos parámetros.

## Página 4 — Modelo de incertidumbre

Para cada brazo j, la tasa latente de conversión p_j tiene una distribución Beta(α_j, β_j). Con n oportunidades expuestas, el número de conversiones K_j es Beta-Binomial. Tras k conversiones, el valor esperado por periodo es el margen unitario condicionado a conversión, multiplicado por la media posterior (α_j+k)/(α_j+β_j+n).

El prior y el margen son parámetros sintéticos configurables. El margen no es el precio nominal: representa una contribución por conversión elegida en unidades abstractas. El precio como cifra separada se excluye de esta extensión porque no entra en la utilidad definida.

## Página 5 — Cálculo preposterior

La herramienta enumera las (n+1)² combinaciones posibles de conversiones de ambos brazos. Para cada combinación calcula la probabilidad predictiva conjunta y el valor posterior de la mejor alternativa. La suma produce q, el margen esperado por periodo después del piloto. No hay ruido de Monte Carlo en la cifra central.

Se usa log-beta con lgamma para evitar factoriales grandes. La suma de masas se informa para revelar deriva numérica. En `results/monte_carlo_check.json` una simulación independiente de prior y datos contrasta la media exacta; su error estándar ayuda a interpretar el desacuerdo finito.

## Página 6 — Derivación del gate

Sea m0 el mejor margen esperado hoy, H el horizonte en periodos, d la demora y c el costo del estudio. La decisión inmediata vale V0=H*m0. El piloto vale V1=(H−d)*q−c: durante d no se captura contribución y luego se elige el mejor brazo con posterior.

La ganancia comparativa es Δ=V1−V0. Seguir con piloto cuando Δ>0; empate favorece acción inmediata. Para q>0, el punto de indiferencia contra lanzar hoy es d*=H−(H*m0+c)/q. Es distinto del delay que hace el valor absoluto del piloto cero. El código reporta el primero, que responde la decisión CEO.

## Página 7 — Lectura del escenario base

El fixture usa priors Beta(11,9) y Beta(9,11), márgenes 10 y 12, n=10 por brazo, H=100 y c=2, todo sintético. Los resultados exactos se guardan en `results/summary.json` y la curva en `results/delay_frontier.png`.

La tabla por demora recorre 0, 2, 5, 10, 15, 20, 30, 50 y 100 periodos. El valor del piloto cae linealmente con d a pendiente −q, dado que q es positivo. La decisión cambia al cruzar d*. No debe interpretarse la escala temporal como días ni periodos reales.

## Página 8 — Ablación negativa y contrafactual

La ablación corre el programa anterior con costo cero para aislar el término de demora: la regla EVSI estática elige pilotear porque cualquier EVSI positivo supera costo cero. Con diez periodos de demora y H=100, el gate nuevo compara el piloto con la alternativa inmediata y revierte esa recomendación. `results/ablation.json` registra decisión y valores de ambas reglas.

Este contrafactual identifica una omisión de modelo, no un efecto causal medido. Con un costo c=2, la implementación previa en esta unidad concreta puede ya rechazar el piloto por EVSI inferior a costo; por eso el test de flip usa c=0 y evita atribuir a la demora una reversión que en realidad causaría el costo fijo. En el escenario base con c=2 el cambio aparece entre d=5 y d=10.

## Página 9 — Sensibilidad del prior y la demora

La concentración de cada Beta se multiplica manteniendo fija su media. A mayor concentración, el prior afirma más certeza y usualmente reduce la utilidad de aprender; el patrón se evalúa numéricamente en la grilla declarada, no como teorema universal para toda grilla ni toda estructura de pagos. La salida `prior_sensitivity.csv` deja todos los casos inspeccionables.

La sensibilidad a demora incluye una grilla con horizonte fijo y también fórmula de break-even. La tasa de contribución posterior y el valor presente de ese periodo se mantienen constantes: solo se quitan d periodos. Descuento, obsolescencia y demanda de calendario no se estiman.

## Página 10 — Precisión numérica y controles

Las probabilidades se evalúan en escala logarítmica y las sumas de valor usan `math.fsum`. Se registra la masa de la predictiva y residuo EVSI. En la auditoría de concentración 1000×, la masa computada es 0.9999999999694 y la EVSI cruda −3.36e−8 aunque teóricamente no puede ser negativa. El flag la clasifica dentro de la tolerancia proporcional declarada 1e−10×max(1,|V_now|); el residual se conserva y no se trunca. Esto demuestra una limitación de doble precisión en una zona de EVSI casi cero.

La tabla `numerical_audit.json` aumenta concentración hasta mil veces para observar masa y residuales bajo precisión doble. Esta exploración no constituye una cota de error formal ni precisión arbitraria. En caso de que residuo supere tolerancia, el usuario debe investigar antes de usar la cifra.

## Página 11 — Implicación de estrategia

El modelo disciplina una pregunta de asignación de atención: qué evidencia vale la espera. Si el negocio pierde oportunidad rápidamente, los pilotos deben ser pequeños, secuenciales o diseñados con decisiones intermedias; si la oportunidad persiste y un error de precio es costoso, una prueba larga puede valer la pena. Esas alternativas requieren modelar ingresos durante muestra, paradas tempranas, interferencia y costos reales, que esta versión no incluye.

Para un comité, el output útil no es un “precio ganador” sino el costo de oportunidad asumido al exigir información adicional y el supuesto temporal que cambia la recomendación.

## Página 12 — Gobernanza y criterio seguir/ajustar/cerrar

**Seguir** con el piloto solo si el margen neto del piloto supera acción inmediata en escenarios centrales y la decisión posterior puede cambiar la acción. **Ajustar** tamaño o duración si el piloto conserva valor en escenarios plausibles pero la demora domina en el caso base; comparar muestras secuenciales y decisión temprana antes de comprometer la versión larga. **Cerrar** el piloto si la acción inmediata domina en un rango razonable de prior, costo y demora, o si la muestra no puede mover la decisión.

La función codificada hoy contrasta solo “piloto” con “acción inmediata”; las etiquetas seguir/ajustar/cerrar son criterios de gobierno que requieren escenarios alternativos, no automatización completa. Registrar propietario, unidades, población y versión del prior antes de decidir.

## Página 13 — Límites y riesgos de interpretación

Supuestos restrictivos: dos brazos, prior Beta independiente, asignación igual, población fija, conversión binaria, margen constante, riesgo neutral, aprendizaje al final, ausencia de ventas durante piloto, sin descuento y horizonte conocido. No se representa elasticidad cruzada, canibalización, stock, retención, selección, estrategia competitiva ni costo de ejecución.

En pricing real, contribución y demanda suelen depender del precio de forma conjunta; asumir tasas independientes puede ser inadecuado. Tampoco se estima el costo de demora con datos. Las unidades son contribución abstracta y no COP. El informe no constituye asesoría sobre decisión comercial ni evidencia de causalidad.

## Página 14 — Evidencia, madurez y próximos pasos

El paquete incluye fórmula, derivación, config, código tipado, tests, notebook con salidas ejecutadas, CSV/JSON y figura, referencias con enlaces, benchmark Monte Carlo y ablation. Reproducción: `bash run.sh`. El contrato es M1: ejecución reproducible sobre parámetros sintéticos. Las pruebas verifican mecánica matemática, no validez externa. No se declara M2 independiente ni M3 productivo.

Siguiente gate para elevar madurez: reconstruir contribución y demora con datos autorizados; incorporar ingresos durante experimento y costo de oportunidad estimado por calendario; probar decisión secuencial; someter supuestos y código a revisión independiente; acordar monitorización y owners. Antecedentes de VOI, delay y opciones reales se comparan en `prior-art.md` y documentan contexto, no validación del escenario.
