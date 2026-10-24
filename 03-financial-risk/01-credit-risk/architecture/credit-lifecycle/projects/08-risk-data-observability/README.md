# Observabilidad de datos, etiquetas y modelos

**Estado S1 · formulación, sin prototipo implementado. Prioridad P2.** Corte 23 de octubre de 2026, Colombia. Esta carpeta es un proyecto propio con tres hipótesis y contrato de ejemplo; sus resultados están pendientes. No hereda automáticamente la madurez de los componentes que reutiliza.

## Pregunta y frontera

¿Cómo distinguir deterioro de riesgo de cambios de fuente, cobertura, maduración de etiquetas o errores del pipeline?

Posee trazabilidad/diagnóstico entre eventos, variables y evaluación. Reutiliza plataforma/feature store; no implementa otro lago de datos ni reentrenamiento automático.

**Unidad de análisis:** Snapshot de modelo por cohorte, versión de fuente y horizonte de label.

## Baseline y alternativa

| Elemento | Diseño propuesto |
|---|---|
| Baseline | Controles de esquema, cobertura y ventanas maduras con reportes estratificados. |
| Challenger | Descomposición por fuente/versión, replay al corte y alarmas conjuntas de horizonte evaluado. |
| Salida | MonitoringAssessment: calidad/cobertura/madurez, métricas válidas y estado de investigación; sin liberar modelos por una alerta. |

## Formulación y supuestos

\[
coverage_c=P(signal\ usable\mid cohort=c),\quad maturity_c=P(label\ available\mid cohort=c,t_{cutoff}).
\]

Ambas son tasas sobre denominadores definidos. Un label desconocido no se codifica como no evento. Drift de variables no demuestra caída de capacidad predictiva.

La fórmula organiza el experimento; no constituye una prueba de eficacia, una metodología regulatoria aprobada ni una estimación sobre clientes reales.

## Datos y contrato

- Eventos con doble fecha, contratos y versiones de proveedor/modelo
- Snapshot y predicciones congeladas antes de desenlaces
- Labels disponibles/adjudicadas, correcciones y exposición

[contracts/example.json](contracts/example.json) contiene un caso totalmente sintético de interfaz propuesta. **No es un JSON Schema, una API implementada ni una respuesta comercial.** Separar contrato, validación de sintaxis y veracidad de la evidencia. El dueño del dato define moneda/unidades, timestamps, estados, acceso, conservación y habilitación antes de una integración real.

## Arquitectura e integración

[Vínculo a la vista por capas](../../diagrams/09-risk-data-models.svg) · [Archivo draw.io de las nueve vistas](../../diagrams/credit-lifecycle.drawio).

Las vistas son las mismas fuentes compartidas del ciclo de crédito. El proyecto posee una pregunta de investigación, no un microservicio obligatorio ni otra copia de esos diagramas.

Reutilizar:

- [credit-feature-store](../../../../../../05-artificial-intelligence-and-computational-systems/data-engineering/credit-feature-store)
- [channel-conformal-audit](../../../../fraud-and-anomaly-research/01-identity-kyc-consistency/channel-conformal-audit)

Contratos a acordar con:

- [06-servicing-ledger-quality](../06-servicing-ledger-quality/README.md)
- [09-purpose-bound-signal-governance](../09-purpose-bound-signal-governance/README.md)

Las dependencias son acuerdos de interfaz y evidencia; no obligan a implementar todos los proyectos antes del primer laboratorio. El [mapa del programa](../README.md) define la secuencia.

## Riesgos y revisión adversarial

- Versiones comparadas sobre mezclas diferentes pueden aparentar una mejora inexistente.
- La revisión repetida de muchos canales cambia la frecuencia de falsas alarmas.

[SECURITY_REVIEW.md](SECURITY_REVIEW.md) contiene cuatro escenarios específicos, fronteras de confianza, controles y fixtures defensivos. Cada una de las tres ideas de [EXPERIMENTS.md](EXPERIMENTS.md) se vincula a dos de esos escenarios. La revisión no equivale a pentest ejecutado ni a que la arquitectura resista ataques reales.

## Ruta de S1 a S2

1. Fijar población, horizonte, contrato y supuestos; resolver campos ambiguos y casos sin cobertura.
2. Construir un generador o corpus sintético versionado y un baseline pequeño con semilla y oráculo cuando corresponda.
3. Ejecutar las tres ideas en [EXPERIMENTS.md](EXPERIMENTS.md), incluidas ablaciones y casos adversariales; guardar salidas, errores y costo.
4. Añadir notebook con ecuaciones, gráficos y conclusiones basadas en outputs reales; verificar desde un proceso/kernel nuevo.
5. Incorporar invariantes y benchmark del comportamiento relevante. S2 requiere código/datos reproducibles y evidencia; esta carpeta permanece S1 hasta entonces.

## Base y procedencia

Fuentes de contexto ya registradas en [sources.json](../../sources.json): S:fico, S:provenir. Las hipótesis, contratos y pruebas de esta carpeta son propuestas propias; los proveedores no las han validado. Revisar el alcance del componente existente antes de atribuirle capacidades nuevas.
