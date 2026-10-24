# Modelos y motores a lo largo del ciclo

Propuestas conectadas a [productos existentes](../../credit-risk-products/) y [fraude](../../fraud-and-anomaly-research/). Esta ficha no implementa ni declara validados todos los modelos. La separación entre señal, estimación y acción evita que una API termine decidiendo por defecto.

| Etapa | Baseline y challenger | Unidad / salida | Riesgo de mala aplicación |
|---|---|---|---|
| Captación | Embudo y reglas de elegibilidad; modelo de propensión solo con uso habilitado | Oferta/solicitud; propensión comercial | Confundir probabilidad de aceptar con capacidad de pagar |
| KYC/fraude | Reglas/logit; boosting calibrado, visión/documentos, red temporal | Solicitud/sesión; p de fraude o score explícito | Anomalía no es probabilidad ni fraude confirmado |
| Capacidad | Conciliación y flujo disponible; cuantiles/hurdle para ingresos irregulares | Persona/hogar/negocio; excedente y escenario | Abono bancario como salario, ingresos negativos/faltantes |
| PD de originación | Scorecard/logit; boosting calibrado con validación temporal | Exposición/cohorte/horizonte; probabilidad | Entrenar solo aprobados y extrapolar a rechazados |
| LGD/EAD | Segmentación y recuperaciones; modelos de dos partes/supervivencia | Exposición/default; severidad y uso esperado | Mezclar censura, horizonte y recuperación bruta con neta |
| Cupo/plazo/precio | Reglas/límites y escenarios de NPV; optimización bajo capacidad/exposición | Caso/oferta; acción factible | Maximizar aprobación sacrificando riesgo o liquidez |
| Revisión | Prioridad por costo/prevenibilidad; asignación MILP | Caso/acción/recurso; cola factible | Tratar eficacia supuesta como efecto aprendido |
| Seguimiento | Cosechas/roll rates y reglas; score conductual/supervivencia | Obligación/período; transición/alerta | Usar variable conocida después de la acción |
| Cobranza | Segmentos/árboles transparentes; uplift/causal si identificable | Cliente/tratamiento/horizonte; beneficio incremental | Respuesta observada no identifica efecto causal |
| Cartera | Concentración/escenarios; dependencia y optimización | Portafolio; exposición, pérdida y estrés | Sumar riesgos superpuestos o ignorar correlación |
| Model risk | Benchmarks, calibración y límites; drift/monitoreo | Versión/población; diagnóstico | Múltiples alarmas sin control, reentrenamiento con labels sesgadas |

## Capacidad de pago: magnitudes antes que score

Como contabilidad de flujo de referencia, con todas las magnitudes del mismo período y moneda:

\[
F_{libre}=I_{verificado}-G_{esencial}-D_{existente},\qquad
DSR=\frac{D_{existente}+cuota_{nueva}}{I_{relevante}}.
\]

No se fija un DSR universal ni se divide por ingreso cero/faltante. Ingreso relevante, gasto esencial, colchón, irregularidad y estacionalidad son definiciones de producto validadas; incorporar un escenario adverso y no un único mes favorable. Una ubicación/IP «normal» no reemplaza esta evaluación.

## Pérdida y precio: evitar contabilidad doble

En un modelo de una exposición con EAD fija y LGD esperada condicionada al default, `EL = PD × LGD × EAD` es una representación útil. En general, conservar la dependencia:

\[
EL=\mathbb E[1_D LGD\cdot EAD].
\]

Para ofertas, una alternativa es el valor presente de flujos netos esperados:

\[
NPV(a)=\sum_{t=1}^{T}\frac{\mathbb E[CF_t(a)]}{(1+r_t)^t}
-Desembolso_0(a)-Costo_{operativo}(a)-Cargo_{capital}(a).
\]

Definir `CF` después de costos/recuperaciones que se hayan incluido y qué costo representa `r`. Si `CF` ya contiene default y recuperaciones, no volver a restar EL; si el descuento ya incorpora fondeo, no duplicarlo como gasto. El costo de capital es una convención de valoración interna, no una fórmula regulatoria presupuesta. Validar también precio permitido, exposición, liquidez y necesidad del cliente.

## Fraude y recursos

Con probabilidad de fraude p, pérdida condicionada L, eficacia q de acción y costos c/fricción f:

\[
C_{ia}=p_iL_i(1-q_{ia})+c_{ia}+(1-p_i)f_{ia}.
\]

El [motor existente](../../fraud-and-anomaly-research/loss-minimization-engine/) ya evalúa asignación finita bajo capacidad sintética. No incorporar PD de default como p de fraude ni reemplazar q por «tasa de alertas». Los límites de revisión se miden en minutos/u otros recursos, no en número de cajas de arquitectura.

## Geoseñales y redes

Conteos por IP/dispositivo son variables de contexto, con ventanas al corte y exclusión de reintentos. Como motivación, no como regla productiva, `N_e(t)` cuenta casos previos únicos con entidad e y ambas fechas conocidas. Añadir contexto de red compartida, cobertura y caducidad; no propagar automáticamente culpa entre vecinos.

Para evaluar geolocalización, comparar con y sin la señal dentro del mismo test temporal y presupuesto, no solo observar AUC. Medir falsos positivos por red móvil/fija, dispositivo, accesibilidad y permiso; una fuente con precisión baja puede inducir fricción sin reducir pérdidas.

## Cobranza: optimizar una acción admisible

\[
U_i(a)=\mathbb E[Recuperacion_{neta,i}\mid do(a)]-Costo_i(a),\qquad a\in\mathcal A_i.
\]

El conjunto admisible depende de contacto autorizado, límites vigentes, estado de la obligación y protección del cliente. El operador `do` expresa una pregunta causal, no un método ya disponible. No usar resultados condicionados a contacto como efecto de la estrategia sin diseño de identificación. Si faltan datos, mantener escenarios e investigación en vez de adjudicar eficacia.

## Validación que precede a una liberación

Separar tiempo, persona y componente de red cuando corresponda; ajustar imputación/features solo con entrenamiento; calibrar en ventana posterior; congelar antes de test; esperar labels maduras. No usar rechazo inferido como verdad observada. Medir incertidumbre, estabilidad y subpoblaciones con datos apropiados. Integración real requiere validación institucional y controles de operación; este catálogo conserva S1 salvo enlaces a experimentos explícitamente ejecutados.
