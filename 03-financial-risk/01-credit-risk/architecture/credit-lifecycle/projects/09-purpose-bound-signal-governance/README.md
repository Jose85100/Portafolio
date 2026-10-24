# Contratos de señales vinculadas a finalidad

**Estado S1 · formulación, sin prototipo implementado. Prioridad P1.** Corte 23 de octubre de 2026, Colombia. Esta carpeta es un proyecto propio con tres hipótesis y contrato de ejemplo; sus resultados están pendientes. No hereda automáticamente la madurez de los componentes que reutiliza.

## Pregunta y frontera

¿Cómo impedir que una señal disponible para seguridad se use automáticamente en otra decisión sin habilitación y evaluación?

Posee contrato técnico de finalidad/uso, minimización y referencias de evidencia. La determinación jurídica procede del área competente; no la inventa el motor ni se implementa aquí una ley en código.

**Unidad de análisis:** Señal, propósito, consumidor, versión de política y fecha de evaluación.

## Baseline y alternativa

| Elemento | Diseño propuesto |
|---|---|
| Baseline | Lista explícita de usos permitidos y estados de captación/permiso. |
| Challenger | Puerta de uso por fuente/consumidor/retención con linaje de variables derivadas y auditoría. |
| Salida | SignalUseDecision: permitido/denegado/inconcluso con razón y política; no presume que denegado signifique fraude. |

## Formulación y supuestos

\[
allow(s,u,t)=purpose\_allowed(s,u)\land authority\_valid(s,t)\land quality\_valid(s,t).
\]

Es un predicado de diseño propio. authority_valid referencia una evaluación institucional vigente; un permiso del SO no equivale por sí solo a autorización jurídica ni legitimidad de la finalidad.

La fórmula organiza el experimento; no constituye una prueba de eficacia, una metodología regulatoria aprobada ni una estimación sobre clientes reales.

## Datos y contrato

- Catálogo de señales, estados y lista de usos aprobados
- Referencias de habilitación/permiso, fuente y política de conservación
- Consumidor, finalidad de consulta y linaje de variables derivadas

[contracts/example.json](contracts/example.json) contiene un caso totalmente sintético de interfaz propuesta. **No es un JSON Schema, una API implementada ni una respuesta comercial.** Separar contrato, validación de sintaxis y veracidad de la evidencia. El dueño del dato define moneda/unidades, timestamps, estados, acceso, conservación y habilitación antes de una integración real.

## Arquitectura e integración

[Vínculo a la vista por capas](../../diagrams/05-signal-capture.svg) · [Archivo draw.io de las nueve vistas](../../diagrams/credit-lifecycle.drawio).

Las vistas son las mismas fuentes compartidas del ciclo de crédito. El proyecto posee una pregunta de investigación, no un microservicio obligatorio ni otra copia de esos diagramas.

Reutilizar:

- [contracts](../../../../contracts)
- [COLOMBIA_DATA_USE.md](../../COLOMBIA_DATA_USE.md)

Contratos a acordar con:

Sin dependencia de otro proyecto nuevo; acordar primero las reglas con los responsables institucionales.

Las dependencias son acuerdos de interfaz y evidencia; no obligan a implementar todos los proyectos antes del primer laboratorio. El [mapa del programa](../README.md) define la secuencia.

## Riesgos y revisión adversarial

- Una variable derivada puede conservar información que se pretendía excluir al borrar solo el campo bruto.
- Las reglas de acceso no reemplazan el análisis de necesidad, daño, alternativa y habilitación por caso.

[SECURITY_REVIEW.md](SECURITY_REVIEW.md) contiene cuatro escenarios específicos, fronteras de confianza, controles y fixtures defensivos. Cada una de las tres ideas de [EXPERIMENTS.md](EXPERIMENTS.md) se vincula a dos de esos escenarios. La revisión no equivale a pentest ejecutado ni a que la arquitectura resista ataques reales.

## Ruta de S1 a S2

1. Fijar población, horizonte, contrato y supuestos; resolver campos ambiguos y casos sin cobertura.
2. Construir un generador o corpus sintético versionado y un baseline pequeño con semilla y oráculo cuando corresponda.
3. Ejecutar las tres ideas en [EXPERIMENTS.md](EXPERIMENTS.md), incluidas ablaciones y casos adversariales; guardar salidas, errores y costo.
4. Añadir notebook con ecuaciones, gráficos y conclusiones basadas en outputs reales; verificar desde un proceso/kernel nuevo.
5. Incorporar invariantes y benchmark del comportamiento relevante. S2 requiere código/datos reproducibles y evidencia; esta carpeta permanece S1 hasta entonces.

## Base y procedencia

Fuentes de contexto ya registradas en [sources.json](../../sources.json): S:law1581, S:law1266, S:sic-ai, S:w3c. Las hipótesis, contratos y pruebas de esta carpeta son propuestas propias; los proveedores no las han validado. Revisar el alcance del componente existente antes de atribuirle capacidades nuevas.
