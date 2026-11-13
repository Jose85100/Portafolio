# Desembolso idempotente y conciliación de efectos

**Estado S1 · formulación, sin prototipo implementado. Prioridad P1.** Corte 23 de octubre de 2026, Colombia. Esta carpeta es un proyecto propio con tres hipótesis y contrato de ejemplo; sus resultados están pendientes. No hereda automáticamente la madurez de los componentes que reutiliza.

## Pregunta y frontera

¿Cómo evitar doble desembolso y reconstruir el estado correcto cuando la respuesta del riel es incierta?

Posee intención, clave de efecto y conciliación de pago. Reutiliza las precondiciones de crédito; no implementa un riel bancario ni afirma reversibilidad de todo pago.

**Unidad de análisis:** Intención de desembolso y referencia de efecto por obligación.

## Baseline y alternativa

| Elemento | Diseño propuesto |
|---|---|
| Baseline | Registro durable de intención, clave única y consulta ante timeout. |
| Challenger | Coordinación de reserva, intención, confirmación y ledger con replay de fallos y conciliación por referencia. |
| Salida | DisbursementState: pending/unknown/confirmed/rejected/returned con referencia, reserva y evidencia; un timeout no crea otra intención. |

## Formulación y supuestos

\[
\#\{effect:\ effect.idempotency\_key=k,\ status=settled\}\le1.
\]

La invariante se exige por operación autorizada. Cumplirla requiere semántica del riel y control durable; no basta mandar un UUID sin contrato de idempotencia/consulta.

La fórmula organiza el experimento; no constituye una prueba de eficacia, una metodología regulatoria aprobada ni una estimación sobre clientes reales.

## Datos y contrato

- Autorización/condiciones vigentes y cuenta destino sintética
- Reserva, clave de intención y respuestas simuladas del riel
- Confirmación/devolución y asientos de ledger reconciliables

[contracts/example.json](contracts/example.json) contiene un caso totalmente sintético de interfaz propuesta. **No es un JSON Schema, una API implementada ni una respuesta comercial.** Separar contrato, validación de sintaxis y veracidad de la evidencia. El dueño del dato define moneda/unidades, timestamps, estados, acceso, conservación y habilitación antes de una integración real.

## Arquitectura e integración

[Vínculo a la vista por capas](../../diagrams/07-disbursement.svg) · [Archivo draw.io de las nueve vistas](../../diagrams/credit-lifecycle.drawio).

Las vistas son las mismas fuentes compartidas del ciclo de crédito. El proyecto posee una pregunta de investigación, no un microservicio obligatorio ni otra copia de esos diagramas.

Reutilizar:

- [contracts](../../../../contracts)
- [database](../../../../database)

Contratos a acordar con:

- [04-durable-origination-workflow](../04-durable-origination-workflow/README.md)
- [10-formalization-collateral](../10-formalization-collateral/README.md)

Las dependencias son acuerdos de interfaz y evidencia; no obligan a implementar todos los proyectos antes del primer laboratorio. El [mapa del programa](../README.md) define la secuencia.

## Riesgos y revisión adversarial

- El simulador debe representar liquidado aunque se pierda la respuesta; asumir que timeout es fallo elimina el caso difícil.
- No borrar asientos ni liberar exposición por un estado incierto.

[SECURITY_REVIEW.md](SECURITY_REVIEW.md) contiene cuatro escenarios específicos, fronteras de confianza, controles y fixtures defensivos. Cada una de las tres ideas de [EXPERIMENTS.md](EXPERIMENTS.md) se vincula a dos de esos escenarios. La revisión no equivale a pentest ejecutado ni a que la arquitectura resista ataques reales.

## Ruta de S1 a S2

1. Fijar población, horizonte, contrato y supuestos; resolver campos ambiguos y casos sin cobertura.
2. Construir un generador o corpus sintético versionado y un baseline pequeño con semilla y oráculo cuando corresponda.
3. Ejecutar las tres ideas en [EXPERIMENTS.md](EXPERIMENTS.md), incluidas ablaciones y casos adversariales; guardar salidas, errores y costo.
4. Añadir notebook con ecuaciones, gráficos y conclusiones basadas en outputs reales; verificar desde un proceso/kernel nuevo.
5. Incorporar invariantes y benchmark del comportamiento relevante. S2 requiere código/datos reproducibles y evidencia; esta carpeta permanece S1 hasta entonces.

## Base y procedencia

Fuentes de contexto ya registradas en [sources.json](../../sources.json): S:ach, S:mambu, S:temenos. Las hipótesis, contratos y pruebas de esta carpeta son propuestas propias; los proveedores no las han validado. Revisar el alcance del componente existente antes de atribuirle capacidades nuevas.
