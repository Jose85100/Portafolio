# Contexto geográfico y dispositivo bajo incertidumbre

**Estado S1 · formulación, sin prototipo implementado. Prioridad P1.** Corte 23 de octubre de 2026, Colombia. Esta carpeta es un proyecto propio con tres hipótesis y contrato de ejemplo; sus resultados están pendientes. No hereda automáticamente la madurez de los componentes que reutiliza.

## Pregunta y frontera

¿Cuándo una discrepancia de ubicación añade información verificable y cuándo solo refleja la imprecisión de la red?

Posee calidad, incertidumbre y estabilidad de geoseñales. No implementa otra prueba de vida, otra identidad civil ni el clasificador de fraude existente.

**Unidad de análisis:** Par de eventos de una sesión/persona sintética, con método y fechas de disponibilidad.

## Baseline y alternativa

| Elemento | Diseño propuesto |
|---|---|
| Baseline | Regla de distancia entre centros con abstención por faltantes. |
| Challenger | Comparación que incorpora radios, método, antigüedad y tipo de red; score contextual separado de la probabilidad de fraude. |
| Salida | ContextAssessment: comparable/inconclusive, discrepancia, razones, antigüedad y fuentes; nunca fraude confirmado. |

## Formulación y supuestos

\[
d_{min}=\max(0,d-r_1-r_2),\qquad v_{min}=d_{min}/\Delta t,\quad \Delta t>0.
\]

d es distancia geodésica en km, r son radios en km y el tiempo se mide en horas. Es una heurística geométrica; el radio de proveedor no es una cota física garantizada.

La fórmula organiza el experimento; no constituye una prueba de eficacia, una metodología regulatoria aprobada ni una estimación sobre clientes reales.

## Datos y contrato

- IP/contexto de red sintéticos y versión de enriquecimiento
- Posiciones generadas con errores controlados, método y radio
- Resultado de permiso, antigüedad de evidencia e ID de instalación con alcance

[contracts/example.json](contracts/example.json) contiene un caso totalmente sintético de interfaz propuesta. **No es un JSON Schema, una API implementada ni una respuesta comercial.** Separar contrato, validación de sintaxis y veracidad de la evidencia. El dueño del dato define moneda/unidades, timestamps, estados, acceso, conservación y habilitación antes de una integración real.

## Arquitectura e integración

[Vínculo a la vista por capas](../../diagrams/05-signal-capture.svg) · [Archivo draw.io de las nueve vistas](../../diagrams/credit-lifecycle.drawio).

Las vistas son las mismas fuentes compartidas del ciclo de crédito. El proyecto posee una pregunta de investigación, no un microservicio obligatorio ni otra copia de esos diagramas.

Reutilizar:

- [ai-enabled-fraud-defense](../../../../fraud-and-anomaly-research/ai-enabled-fraud-defense)
- [02-temporal-application-graphs](../../../../fraud-and-anomaly-research/02-temporal-application-graphs)

Contratos a acordar con:

- [09-purpose-bound-signal-governance](../09-purpose-bound-signal-governance/README.md)

Las dependencias son acuerdos de interfaz y evidencia; no obligan a implementar todos los proyectos antes del primer laboratorio. El [mapa del programa](../README.md) define la secuencia.

## Riesgos y revisión adversarial

- IP compartida o cambiante: agrupar evaluación por red y persona, no por evento aislado.
- La ausencia de permiso o radio produce estado explícito; no coordenada cero ni etiqueta adversa.

[SECURITY_REVIEW.md](SECURITY_REVIEW.md) contiene cuatro escenarios específicos, fronteras de confianza, controles y fixtures defensivos. Cada una de las tres ideas de [EXPERIMENTS.md](EXPERIMENTS.md) se vincula a dos de esos escenarios. La revisión no equivale a pentest ejecutado ni a que la arquitectura resista ataques reales.

## Ruta de S1 a S2

1. Fijar población, horizonte, contrato y supuestos; resolver campos ambiguos y casos sin cobertura.
2. Construir un generador o corpus sintético versionado y un baseline pequeño con semilla y oráculo cuando corresponda.
3. Ejecutar las tres ideas en [EXPERIMENTS.md](EXPERIMENTS.md), incluidas ablaciones y casos adversariales; guardar salidas, errores y costo.
4. Añadir notebook con ecuaciones, gráficos y conclusiones basadas en outputs reales; verificar desde un proceso/kernel nuevo.
5. Incorporar invariantes y benchmark del comportamiento relevante. S2 requiere código/datos reproducibles y evidencia; esta carpeta permanece S1 hasta entonces.

## Base y procedencia

Fuentes de contexto ya registradas en [sources.json](../../sources.json): S:maxmind, S:maxmind-vpn, S:fingerprint, S:w3c. Las hipótesis, contratos y pruebas de esta carpeta son propuestas propias; los proveedores no las han validado. Revisar el alcance del componente existente antes de atribuirle capacidades nuevas.
