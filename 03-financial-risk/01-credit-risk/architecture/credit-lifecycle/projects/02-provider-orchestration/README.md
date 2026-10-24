# Orquestación de proveedores, costo y resiliencia

**Estado S1 · formulación, sin prototipo implementado. Prioridad P1.** Corte 23 de octubre de 2026, Colombia. Esta carpeta es un proyecto propio con tres hipótesis y contrato de ejemplo; sus resultados están pendientes. No hereda automáticamente la madurez de los componentes que reutiliza.

## Pregunta y frontera

¿Qué verificación conviene consultar a continuación cuando hay costo, latencia, fallos compartidos y evidencia incompleta?

Posee plan de consultas, cobertura y política de degradación. Reutiliza el experimento de dependencia/colas y no copia modelos propietarios ni el MILP de acciones antifraude.

**Unidad de análisis:** Caso y etapa de consulta; historia de respuestas disponibles y recursos restantes.

## Baseline y alternativa

| Elemento | Diseño propuesto |
|---|---|
| Baseline | Consultar secuencia fija de fuentes con timeout y ruta pendiente explícita. |
| Challenger | Plan adaptativo por costo esperado/valor de información con escenarios de dependencia y presupuesto; sin presuponer independencia. |
| Salida | QueryPlan/ProviderOutcome: fuente, deadline, idempotency_key, estado, cobertura y motivo de siguiente acción. |

## Formulación y supuestos

\[
V(h,b)=\min\{C_{stop}(h),\min_{a\in Q(h,b)}[c_a+\mathbb E V(h\oplus Y_a,b-r_a)]\}.
\]

h es historia de evidencia disponible; b presupuesto; Q consultas admisibles; Y respuesta, incluyendo unavailable; r_a>0 consumo. C_stop(h) es el costo mínimo esperado de una acción terminal admisible. Si Q está vacío, V=C_stop. Presupuesto finito y consumo mínimo positivo acotan el número de consultas; las distribuciones/costos son supuestos hasta estimación.

La fórmula organiza el experimento; no constituye una prueba de eficacia, una metodología regulatoria aprobada ni una estimación sobre clientes reales.

## Datos y contrato

- Plan y cobertura de cada fuente por producto/canal
- Respuestas sintéticas con latencia, versión, timeout y dependencia
- Costos por intento/reintento y capacidad de revisión supuestos

[contracts/example.json](contracts/example.json) contiene un caso totalmente sintético de interfaz propuesta. **No es un JSON Schema, una API implementada ni una respuesta comercial.** Separar contrato, validación de sintaxis y veracidad de la evidencia. El dueño del dato define moneda/unidades, timestamps, estados, acceso, conservación y habilitación antes de una integración real.

## Arquitectura e integración

[Vínculo a la vista por capas](../../diagrams/03-event-workflow.svg) · [Archivo draw.io de las nueve vistas](../../diagrams/credit-lifecycle.drawio).

Las vistas son las mismas fuentes compartidas del ciclo de crédito. El proyecto posee una pregunta de investigación, no un microservicio obligatorio ni otra copia de esos diagramas.

Reutilizar:

- [notebook.ipynb](../../../../fraud-and-anomaly-research/ai-enabled-fraud-defense/notebook.ipynb)
- [innovation-evsi-gate](../../../../../../06-strategy-innovation-and-leadership/20-ai-innovation-productivity-leadership/innovation-evsi-gate)

Contratos a acordar con:

- [09-purpose-bound-signal-governance](../09-purpose-bound-signal-governance/README.md)

Las dependencias son acuerdos de interfaz y evidencia; no obligan a implementar todos los proyectos antes del primer laboratorio. El [mapa del programa](../README.md) define la secuencia.

## Riesgos y revisión adversarial

- Un adaptador interoperable no vuelve intercambiables scores o coberturas.
- Un proveedor caído puede compartir infraestructura o fuente con el fallback.

[SECURITY_REVIEW.md](SECURITY_REVIEW.md) contiene cuatro escenarios específicos, fronteras de confianza, controles y fixtures defensivos. Cada una de las tres ideas de [EXPERIMENTS.md](EXPERIMENTS.md) se vincula a dos de esos escenarios. La revisión no equivale a pentest ejecutado ni a que la arquitectura resista ataques reales.

## Ruta de S1 a S2

1. Fijar población, horizonte, contrato y supuestos; resolver campos ambiguos y casos sin cobertura.
2. Construir un generador o corpus sintético versionado y un baseline pequeño con semilla y oráculo cuando corresponda.
3. Ejecutar las tres ideas en [EXPERIMENTS.md](EXPERIMENTS.md), incluidas ablaciones y casos adversariales; guardar salidas, errores y costo.
4. Añadir notebook con ecuaciones, gráficos y conclusiones basadas en outputs reales; verificar desde un proceso/kernel nuevo.
5. Incorporar invariantes y benchmark del comportamiento relevante. S2 requiere código/datos reproducibles y evidencia; esta carpeta permanece S1 hasta entonces.

## Base y procedencia

Fuentes de contexto ya registradas en [sources.json](../../sources.json): S:seon, S:persona, S:provenir. Las hipótesis, contratos y pruebas de esta carpeta son propuestas propias; los proveedores no las han validado. Revisar el alcance del componente existente antes de atribuirle capacidades nuevas.
