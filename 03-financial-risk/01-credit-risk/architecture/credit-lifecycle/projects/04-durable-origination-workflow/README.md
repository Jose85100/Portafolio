# Workflow durable de originación y excepciones

**Estado S1 · formulación, sin prototipo implementado. Prioridad P1.** Corte 23 de octubre de 2026, Colombia. Esta carpeta es un proyecto propio con tres hipótesis y contrato de ejemplo; sus resultados están pendientes. No hereda automáticamente la madurez de los componentes que reutiliza.

## Pregunta y frontera

¿Cómo conservar un estado de solicitud correcto ante callbacks duplicados, evidencia tardía, vencimientos y decisiones humanas?

Posee estados/transiciones de solicitud y precondiciones de etapa. Reutiliza runtime/checkpoints de IA; no duplica el LOS como producto ni mezcla estados de solicitud y pago.

**Unidad de análisis:** Agregado solicitud con versión y comandos autorizados.

## Baseline y alternativa

| Elemento | Diseño propuesto |
|---|---|
| Baseline | Máquina de estados explícita con registro de eventos e idempotencia de comando. |
| Challenger | Workflow durable con outbox, historial de transición, deadlines y tareas humanas versionadas. |
| Salida | TransitionRecord: estado previo/nuevo, precondiciones, actor, evento, versión y resultado del comando. |

## Formulación y supuestos

\[
s_{t+1}=T(s_t,e_t)\quad\text{si}\quad allowed(s_t,e_t,authority,version,cutoff).
\]

s es estado; e evento; T transición parcial. Una transición inválida queda rechazada o en revisión, sin avanzar implícitamente. No se promete exactamente una entrega entre organizaciones.

La fórmula organiza el experimento; no constituye una prueba de eficacia, una metodología regulatoria aprobada ni una estimación sobre clientes reales.

## Datos y contrato

- Estado/versionado de solicitud, oferta y condiciones
- Eventos con event_id, disponibilidad y autoridad
- Callbacks, comandos, decisiones humanas y plazos sintéticos

[contracts/example.json](contracts/example.json) contiene un caso totalmente sintético de interfaz propuesta. **No es un JSON Schema, una API implementada ni una respuesta comercial.** Separar contrato, validación de sintaxis y veracidad de la evidencia. El dueño del dato define moneda/unidades, timestamps, estados, acceso, conservación y habilitación antes de una integración real.

## Arquitectura e integración

[Vínculo a la vista por capas](../../diagrams/03-event-workflow.svg) · [Archivo draw.io de las nueve vistas](../../diagrams/credit-lifecycle.drawio).

Las vistas son las mismas fuentes compartidas del ciclo de crédito. El proyecto posee una pregunta de investigación, no un microservicio obligatorio ni otra copia de esos diagramas.

Reutilizar:

- [mvp-durable-checkpoints](../../../../../../05-artificial-intelligence-and-computational-systems/10-ai-orchestration-engineering/06-fault-tolerant-ai-execution-recovery/mvp-durable-checkpoints)
- [agent-runtime-reliability](../../../../../../05-artificial-intelligence-and-computational-systems/04-agentic-ai-and-multi-agent-systems/agent-runtime-reliability)

Contratos a acordar con:

- [09-purpose-bound-signal-governance](../09-purpose-bound-signal-governance/README.md)
- [10-formalization-collateral](../10-formalization-collateral/README.md)

Las dependencias son acuerdos de interfaz y evidencia; no obligan a implementar todos los proyectos antes del primer laboratorio. El [mapa del programa](../README.md) define la secuencia.

## Riesgos y revisión adversarial

- Un callback legítimo puede llegar tarde y no habilitar una oferta vencida.
- Una intervención humana necesita atribución y evidencia; no un cambio manual opaco en la base.

[SECURITY_REVIEW.md](SECURITY_REVIEW.md) contiene cuatro escenarios específicos, fronteras de confianza, controles y fixtures defensivos. Cada una de las tres ideas de [EXPERIMENTS.md](EXPERIMENTS.md) se vincula a dos de esos escenarios. La revisión no equivale a pentest ejecutado ni a que la arquitectura resista ataques reales.

## Ruta de S1 a S2

1. Fijar población, horizonte, contrato y supuestos; resolver campos ambiguos y casos sin cobertura.
2. Construir un generador o corpus sintético versionado y un baseline pequeño con semilla y oráculo cuando corresponda.
3. Ejecutar las tres ideas en [EXPERIMENTS.md](EXPERIMENTS.md), incluidas ablaciones y casos adversariales; guardar salidas, errores y costo.
4. Añadir notebook con ecuaciones, gráficos y conclusiones basadas en outputs reales; verificar desde un proceso/kernel nuevo.
5. Incorporar invariantes y benchmark del comportamiento relevante. S2 requiere código/datos reproducibles y evidencia; esta carpeta permanece S1 hasta entonces.

## Base y procedencia

Fuentes de contexto ya registradas en [sources.json](../../sources.json): S:persona, S:provenir. Las hipótesis, contratos y pruebas de esta carpeta son propuestas propias; los proveedores no las han validado. Revisar el alcance del componente existente antes de atribuirle capacidades nuevas.
