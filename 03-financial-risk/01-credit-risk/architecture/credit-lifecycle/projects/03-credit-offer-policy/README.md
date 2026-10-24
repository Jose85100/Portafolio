# Ofertas de crédito bajo capacidad y exposición

**Estado S1 · formulación, sin prototipo implementado. Prioridad P2.** Corte 23 de octubre de 2026, Colombia. Esta carpeta es un proyecto propio con tres hipótesis y contrato de ejemplo; sus resultados están pendientes. No hereda automáticamente la madurez de los componentes que reutiliza.

## Pregunta y frontera

¿Cómo elegir monto, plazo y condiciones entre ofertas admisibles considerando flujo de pago, incertidumbre y exposición concurrente?

Posee selección de oferta y restricciones de cartera por caso. Reutiliza scorecard/PD y límites existentes; no crea un score de fraude ni implementa normativa de tasas o capital.

**Unidad de análisis:** Solicitud y menú discreto de ofertas con horizonte/moneda homogéneos.

## Baseline y alternativa

| Elemento | Diseño propuesto |
|---|---|
| Baseline | Reglas de elegibilidad, capacidad y un menú fijo de ofertas. |
| Challenger | Optimización de valor/costo sobre el mismo menú con escenarios de ingreso, PD/severidad y límites reservados. |
| Salida | OfferDecision: oferta o revisión, restricciones vinculantes, versión y fecha de vencimiento; distinta de autorización de desembolso. |

## Formulación y supuestos

\[
\max_x\sum_{i,a}NPV_{ia}x_{ia},\quad\sum_a x_{ia}\le1,\quad\sum_{i,a}EAD_{ia}x_{ia}\le B,\quad x_{ia}\in\{0,1\}.
\]

i caso, a oferta admisible, B presupuesto de exposición. La opción sin oferta debe definirse con sus consecuencias y estados; NPV requiere costos y flujos coherentes, sin doble restar pérdidas ya incluidas.

La fórmula organiza el experimento; no constituye una prueba de eficacia, una metodología regulatoria aprobada ni una estimación sobre clientes reales.

## Datos y contrato

- Ingreso/deuda verificados y calidad del respaldo
- Predicciones temporales versionadas y límites por producto
- Menú de ofertas, precios supuestos, escenarios y reserva vigente

[contracts/example.json](contracts/example.json) contiene un caso totalmente sintético de interfaz propuesta. **No es un JSON Schema, una API implementada ni una respuesta comercial.** Separar contrato, validación de sintaxis y veracidad de la evidencia. El dueño del dato define moneda/unidades, timestamps, estados, acceso, conservación y habilitación antes de una integración real.

## Arquitectura e integración

[Vínculo a la vista por capas](../../diagrams/06-credit-decision.svg) · [Archivo draw.io de las nueve vistas](../../diagrams/credit-lifecycle.drawio).

Las vistas son las mismas fuentes compartidas del ciclo de crédito. El proyecto posee una pregunta de investigación, no un microservicio obligatorio ni otra copia de esos diagramas.

Reutilizar:

- [scorecard-logistico-woe](../../../../credit-risk-products/scorecard-logistico-woe)
- [monitor-de-limites-de-apetito](../../../../credit-portfolio-strategy/monitor-de-limites-de-apetito)

Contratos a acordar con:

- [06-servicing-ledger-quality](../06-servicing-ledger-quality/README.md)
- [09-purpose-bound-signal-governance](../09-purpose-bound-signal-governance/README.md)

Las dependencias son acuerdos de interfaz y evidencia; no obligan a implementar todos los proyectos antes del primer laboratorio. El [mapa del programa](../README.md) define la secuencia.

## Riesgos y revisión adversarial

- Datos de aprobados no identifican directamente resultados de todos los solicitantes rechazados.
- Precio, elegibilidad y límites requieren reglas institucionales; el optimum del laboratorio no aprueba una oferta real.

[SECURITY_REVIEW.md](SECURITY_REVIEW.md) contiene cuatro escenarios específicos, fronteras de confianza, controles y fixtures defensivos. Cada una de las tres ideas de [EXPERIMENTS.md](EXPERIMENTS.md) se vincula a dos de esos escenarios. La revisión no equivale a pentest ejecutado ni a que la arquitectura resista ataques reales.

## Ruta de S1 a S2

1. Fijar población, horizonte, contrato y supuestos; resolver campos ambiguos y casos sin cobertura.
2. Construir un generador o corpus sintético versionado y un baseline pequeño con semilla y oráculo cuando corresponda.
3. Ejecutar las tres ideas en [EXPERIMENTS.md](EXPERIMENTS.md), incluidas ablaciones y casos adversariales; guardar salidas, errores y costo.
4. Añadir notebook con ecuaciones, gráficos y conclusiones basadas en outputs reales; verificar desde un proceso/kernel nuevo.
5. Incorporar invariantes y benchmark del comportamiento relevante. S2 requiere código/datos reproducibles y evidencia; esta carpeta permanece S1 hasta entonces.

## Base y procedencia

Fuentes de contexto ya registradas en [sources.json](../../sources.json): S:fico, S:provenir, S:tu, S:experian. Las hipótesis, contratos y pruebas de esta carpeta son propuestas propias; los proveedores no las han validado. Revisar el alcance del componente existente antes de atribuirle capacidades nuevas.
