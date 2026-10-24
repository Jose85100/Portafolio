# Formalización y condiciones precedentes

**Estado S1 · formulación, sin prototipo implementado. Prioridad P2.** Corte 23 de octubre de 2026, Colombia. Esta carpeta es un proyecto propio con tres hipótesis y contrato de ejemplo; sus resultados están pendientes. No hereda automáticamente la madurez de los componentes que reutiliza.

## Pregunta y frontera

¿Cómo demostrar que la aceptación, el instrumento, la garantía y el desembolso corresponden a la misma oferta vigente?

Posee coherencia/versionado del paquete previo al efecto. Reutiliza extracción documental y servicios de firma; no certifica exigibilidad jurídica ni reconstruye plataformas de pagarés.

**Unidad de análisis:** Oferta, versión aceptada, evidencias/instrumentos y autorización de efecto.

## Baseline y alternativa

| Elemento | Diseño propuesto |
|---|---|
| Baseline | Checklist versionado de condiciones, huellas de documento y revisión de discrepancias. |
| Challenger | Grafo de evidencias y condiciones por producto, vigencia y cambios de términos. |
| Salida | FormalizationReadiness: lista de condiciones cumplidas/pendientes y referencias exactas antes del desembolso. |

## Formulación y supuestos

\[
ready=accepted(offer_v)\land terms\_match\land instrument\_ready\land conditions\_met\land valid\_at(t).
\]

Cada predicado requiere evidencia y autoridad definida. Un hash verifica integridad respecto a bytes conservados; no autentica por sí solo emisor, voluntad o validez jurídica.

La fórmula organiza el experimento; no constituye una prueba de eficacia, una metodología regulatoria aprobada ni una estimación sobre clientes reales.

## Datos y contrato

- Oferta/aceptación con versiones y vigencia
- Contrato/instrumento/garantía con referencias y estado validado por responsable
- Cambios de términos, documentos y condiciones precedentes

[contracts/example.json](contracts/example.json) contiene un caso totalmente sintético de interfaz propuesta. **No es un JSON Schema, una API implementada ni una respuesta comercial.** Separar contrato, validación de sintaxis y veracidad de la evidencia. El dueño del dato define moneda/unidades, timestamps, estados, acceso, conservación y habilitación antes de una integración real.

## Arquitectura e integración

[Vínculo a la vista por capas](../../diagrams/07-disbursement.svg) · [Archivo draw.io de las nueve vistas](../../diagrams/credit-lifecycle.drawio).

Las vistas son las mismas fuentes compartidas del ciclo de crédito. El proyecto posee una pregunta de investigación, no un microservicio obligatorio ni otra copia de esos diagramas.

Reutilizar:

- [02-evidence-preserving-document-pipeline](../../../../../../05-artificial-intelligence-and-computational-systems/03-deep-learning-and-foundation-models/structured-decision-architectures/02-evidence-preserving-document-pipeline)
- [contracts](../../../../contracts)

Contratos a acordar con:

- [09-purpose-bound-signal-governance](../09-purpose-bound-signal-governance/README.md)

Las dependencias son acuerdos de interfaz y evidencia; no obligan a implementar todos los proyectos antes del primer laboratorio. El [mapa del programa](../README.md) define la secuencia.

## Riesgos y revisión adversarial

- Una firma válida de un documento puede no corresponder a la oferta que se pretende ejecutar.
- Condiciones de garantía e instrumento se validan por producto; no se asigna estado jurídico desde un OCR.

[SECURITY_REVIEW.md](SECURITY_REVIEW.md) contiene cuatro escenarios específicos, fronteras de confianza, controles y fixtures defensivos. Cada una de las tres ideas de [EXPERIMENTS.md](EXPERIMENTS.md) se vincula a dos de esos escenarios. La revisión no equivale a pentest ejecutado ni a que la arquitectura resista ataques reales.

## Ruta de S1 a S2

1. Fijar población, horizonte, contrato y supuestos; resolver campos ambiguos y casos sin cobertura.
2. Construir un generador o corpus sintético versionado y un baseline pequeño con semilla y oráculo cuando corresponda.
3. Ejecutar las tres ideas en [EXPERIMENTS.md](EXPERIMENTS.md), incluidas ablaciones y casos adversariales; guardar salidas, errores y costo.
4. Añadir notebook con ecuaciones, gráficos y conclusiones basadas en outputs reales; verificar desde un proceso/kernel nuevo.
5. Incorporar invariantes y benchmark del comportamiento relevante. S2 requiere código/datos reproducibles y evidencia; esta carpeta permanece S1 hasta entonces.

## Base y procedencia

Fuentes de contexto ya registradas en [sources.json](../../sources.json): S:certicamara, S:deceval. Las hipótesis, contratos y pruebas de esta carpeta son propuestas propias; los proveedores no las han validado. Revisar el alcance del componente existente antes de atribuirle capacidades nuevas.
