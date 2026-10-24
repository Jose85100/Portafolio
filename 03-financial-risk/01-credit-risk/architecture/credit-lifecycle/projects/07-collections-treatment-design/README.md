# Tratamientos de cobranza y recuperación sostenible

**Estado S1 · formulación, sin prototipo implementado. Prioridad P3.** Corte 23 de octubre de 2026, Colombia. Esta carpeta es un proyecto propio con tres hipótesis y contrato de ejemplo; sus resultados están pendientes. No hereda automáticamente la madurez de los componentes que reutiliza.

## Pregunta y frontera

¿Qué acción admisible aporta recuperación incremental sin confundir facilidad de contacto con eficacia causal?

Posee decisión de tratamiento y medición de su efecto bajo restricciones. Reutiliza saldos del LMS y el programa causal; no crea acceso irrestricto a contactos ni localización del deudor.

**Unidad de análisis:** Cliente/obligación elegible, acción de tratamiento y horizonte de resultado.

## Baseline y alternativa

| Elemento | Diseño propuesto |
|---|---|
| Baseline | Segmentación transparente y reglas de contacto aplicables con costos explícitos. |
| Challenger | Estimación incremental de tratamientos con identificación justificada y optimización dentro del conjunto admisible. |
| Salida | TreatmentProposal: elegibilidad, acción/abstención, fundamento, límite y horizonte; resultado pago separado de promesa. |

## Formulación y supuestos

\[
a_i^*=\arg\max_{a\in\mathcal A_i}\{\mathbb E[R_i\mid do(a)]-C_i(a)\}.
\]

R es recuperación neta en horizonte común, C costo no incluido en R y A acciones admisibles. El operador causal formula el objetivo, no demuestra identificación ni efecto positivo.

La fórmula organiza el experimento; no constituye una prueba de eficacia, una metodología regulatoria aprobada ni una estimación sobre clientes reales.

## Datos y contrato

- Saldo/estado conciliado y capacidad del cliente según evidencia habilitada
- Elegibilidad de contacto, intentos concurrentes, acción y probabilidad de asignación
- Acuerdos, pagos confirmados, costos, reclamaciones y tiempo

[contracts/example.json](contracts/example.json) contiene un caso totalmente sintético de interfaz propuesta. **No es un JSON Schema, una API implementada ni una respuesta comercial.** Separar contrato, validación de sintaxis y veracidad de la evidencia. El dueño del dato define moneda/unidades, timestamps, estados, acceso, conservación y habilitación antes de una integración real.

## Arquitectura e integración

[Vínculo a la vista por capas](../../diagrams/08-servicing-collections.svg) · [Archivo draw.io de las nueve vistas](../../diagrams/credit-lifecycle.drawio).

Las vistas son las mismas fuentes compartidas del ciclo de crédito. El proyecto posee una pregunta de investigación, no un microservicio obligatorio ni otra copia de esos diagramas.

Reutilizar:

- [01-off-policy-policy-evaluation](../../../../../../05-artificial-intelligence-and-computational-systems/05-causal-ai-and-decision-intelligence/01-off-policy-policy-evaluation)
- [matrices-de-transicion-roll-rates](../../../../credit-risk-products/matrices-de-transicion-roll-rates)

Contratos a acordar con:

- [06-servicing-ledger-quality](../06-servicing-ledger-quality/README.md)
- [09-purpose-bound-signal-governance](../09-purpose-bound-signal-governance/README.md)

Las dependencias son acuerdos de interfaz y evidencia; no obligan a implementar todos los proyectos antes del primer laboratorio. El [mapa del programa](../README.md) define la secuencia.

## Riesgos y revisión adversarial

- No asignar tratamiento inválido para ganar una comparación; la admisibilidad es una restricción previa.
- La promesa de pago y el contacto efectivo no sustituyen el flujo recuperado confirmado.

[SECURITY_REVIEW.md](SECURITY_REVIEW.md) contiene cuatro escenarios específicos, fronteras de confianza, controles y fixtures defensivos. Cada una de las tres ideas de [EXPERIMENTS.md](EXPERIMENTS.md) se vincula a dos de esos escenarios. La revisión no equivale a pentest ejecutado ni a que la arquitectura resista ataques reales.

## Ruta de S1 a S2

1. Fijar población, horizonte, contrato y supuestos; resolver campos ambiguos y casos sin cobertura.
2. Construir un generador o corpus sintético versionado y un baseline pequeño con semilla y oráculo cuando corresponda.
3. Ejecutar las tres ideas en [EXPERIMENTS.md](EXPERIMENTS.md), incluidas ablaciones y casos adversariales; guardar salidas, errores y costo.
4. Añadir notebook con ecuaciones, gráficos y conclusiones basadas en outputs reales; verificar desde un proceso/kernel nuevo.
5. Incorporar invariantes y benchmark del comportamiento relevante. S2 requiere código/datos reproducibles y evidencia; esta carpeta permanece S1 hasta entonces.

## Base y procedencia

Fuentes de contexto ya registradas en [sources.json](../../sources.json): S:law2300, S:katabat, S:tu-collections. Las hipótesis, contratos y pruebas de esta carpeta son propuestas propias; los proveedores no las han validado. Revisar el alcance del componente existente antes de atribuirle capacidades nuevas.
