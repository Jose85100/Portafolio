# Calidad del ledger y estado de la obligación

**Estado S1 · formulación, sin prototipo implementado. Prioridad P2.** Corte 23 de octubre de 2026, Colombia. Esta carpeta es un proyecto propio con tres hipótesis y contrato de ejemplo; sus resultados están pendientes. No hereda automáticamente la madurez de los componentes que reutiliza.

## Pregunta y frontera

¿Cuánta mora aparente puede explicar una discrepancia de calendario, imputación o fecha efectiva antes que un deterioro crediticio?

Posee reconciliación de estado administrativo y eventos de corrección. Reutiliza roll rates/cosechas; no entrena otro score ni reemplaza contabilidad.

**Unidad de análisis:** Obligación, evento de pago y snapshot a una fecha de corte.

## Baseline y alternativa

| Elemento | Diseño propuesto |
|---|---|
| Baseline | Reconciliación por referencia y reglas explícitas de calendario/imputación. |
| Challenger | Replay de eventos bitemporales con correcciones versionadas y diagnóstico de fuente de discrepancia. |
| Salida | LoanStateSnapshot: saldo, DPD, fuente, corte, versión y bandera de conciliación; no etiqueta automática de fraude/default. |

## Formulación y supuestos

\[
balance_t=balance_{t-1}+debits_t-credits_t+adjustments_t.
\]

La identidad aplica al ledger definido y a sus signos, moneda y período. Intereses, cargos, reversos y ajustes necesitan categorías y reglas por producto; no se fija aquí una política contable.

La fórmula organiza el experimento; no constituye una prueba de eficacia, una metodología regulatoria aprobada ni una estimación sobre clientes reales.

## Datos y contrato

- Cronograma, calendario y reglas de imputación sintéticos
- Ledger, pagos confirmados, fecha efectiva y fecha de disponibilidad
- Correcciones, reclamaciones y versiones de snapshot

[contracts/example.json](contracts/example.json) contiene un caso totalmente sintético de interfaz propuesta. **No es un JSON Schema, una API implementada ni una respuesta comercial.** Separar contrato, validación de sintaxis y veracidad de la evidencia. El dueño del dato define moneda/unidades, timestamps, estados, acceso, conservación y habilitación antes de una integración real.

## Arquitectura e integración

[Vínculo a la vista por capas](../../diagrams/08-servicing-collections.svg) · [Archivo draw.io de las nueve vistas](../../diagrams/credit-lifecycle.drawio).

Las vistas son las mismas fuentes compartidas del ciclo de crédito. El proyecto posee una pregunta de investigación, no un microservicio obligatorio ni otra copia de esos diagramas.

Reutilizar:

- [matrices-de-transicion-roll-rates](../../../../credit-risk-products/matrices-de-transicion-roll-rates)
- [analisis-de-cosechas-vintage](../../../../credit-risk-products/analisis-de-cosechas-vintage)

Contratos a acordar con:

- [05-disbursement-reconciliation](../05-disbursement-reconciliation/README.md)

Las dependencias son acuerdos de interfaz y evidencia; no obligan a implementar todos los proyectos antes del primer laboratorio. El [mapa del programa](../README.md) define la secuencia.

## Riesgos y revisión adversarial

- La corrección de un error no debe borrar la trazabilidad de la decisión anterior.
- No confundir fecha contable, fecha de pago y disponibilidad para una predicción histórica.

[SECURITY_REVIEW.md](SECURITY_REVIEW.md) contiene cuatro escenarios específicos, fronteras de confianza, controles y fixtures defensivos. Cada una de las tres ideas de [EXPERIMENTS.md](EXPERIMENTS.md) se vincula a dos de esos escenarios. La revisión no equivale a pentest ejecutado ni a que la arquitectura resista ataques reales.

## Ruta de S1 a S2

1. Fijar población, horizonte, contrato y supuestos; resolver campos ambiguos y casos sin cobertura.
2. Construir un generador o corpus sintético versionado y un baseline pequeño con semilla y oráculo cuando corresponda.
3. Ejecutar las tres ideas en [EXPERIMENTS.md](EXPERIMENTS.md), incluidas ablaciones y casos adversariales; guardar salidas, errores y costo.
4. Añadir notebook con ecuaciones, gráficos y conclusiones basadas en outputs reales; verificar desde un proceso/kernel nuevo.
5. Incorporar invariantes y benchmark del comportamiento relevante. S2 requiere código/datos reproducibles y evidencia; esta carpeta permanece S1 hasta entonces.

## Base y procedencia

Fuentes de contexto ya registradas en [sources.json](../../sources.json): S:mambu, S:temenos. Las hipótesis, contratos y pruebas de esta carpeta son propuestas propias; los proveedores no las han validado. Revisar el alcance del componente existente antes de atribuirle capacidades nuevas.
