# Arquitectura de las capas defensivas adicionales

Cuatro vistas conectan ocho responsabilidades con los diez proyectos. Son overlays lógicos de la arquitectura de crédito, no una segunda decisión de crédito ni una promesa de protección completa. [Capas y dueños](README.md), [diagramas](diagrams/README.md), [escenarios de los proyectos](../projects/THREAT_MODEL.md).

| Vista | Capas principales | Frontera y precondición a proteger |
|---|---|---|
| Evidencia: teléfono/documento/sujeto/efecto | 01 Integridad, con 05 controles humanos | Un pase conserva su hecho y alcance; no se reutiliza para otro sujeto, sesión, oferta o efecto |
| Inteligencia y coordinación | 02 Inteligencia, 06 redes | Indicador y asociación generan hipótesis con procedencia, no culpa propagada ni label confirmado |
| Evaluación/modelo/personas | 03 Adversarial, 04 sondeo, 05 intervención humana | Prueba de cadena y de fallback, integridad de entradas/roles y explicación fiel |
| Vigilancia y respuesta | 07 Aseguramiento continuo, 08 incidentes | Cambio de semántica o control omitido abre diagnóstico; contención conserva efectos y evidencia |

## Datos y estado

El contrato de cada verificación contiene sujeto/caso/sesión, tipo de hecho, fuente, versión, event_time, available_time, vigencia, estado, razones y finalidad. Los ejemplos de proyectos representan un subconjunto de interfaz y no un schema completo implementado. La evidencia original se referencia con acceso restringido; los scores y logs no sustituyen su procedencia.

Estados del hecho: no observado, inconcluso, verificado dentro de alcance, discrepancia, fuente no disponible y obsoleto según la política correspondiente. Estados del proceso: pendiente, revisión, transición admisible o rechazada por precondición. Sospecha es un estado de investigación, no sinónimo de discrepancia técnica ni de fraude adjudicado.

## Tres condiciones que un overlay no puede eludir

1. Una verificación solo satisface el hecho, sujeto y tiempo que cubre. Un canal controlado no prueba voluntad, ni un hash prueba emisor.
2. La ruta de excepción conserva autoridad, condición de evidencia y presupuesto de recursos. Una caída no produce un pase silencioso.
3. Un efecto financiero se consulta y concilia; una alerta posterior o un replay no borran el pasado ni autorizan un efecto nuevo sin condición.

## Contrastes legítimos

Línea compartida, cambio legítimo de móvil, accesibilidad, documentos no soportados y error de proveedor acompañan los casos adversariales. El control no se evalúa solo por bloquear ataques hipotéticos: requiere cobertura, fricción, revisión y resultados de genuinos medidos bajo población/horizonte definidos.

## Alcance de la entrega

Cuatro páginas draw.io nativas y cuatro SVG comparten geometría/contenido. Se inspeccionan las vistas SVG renderizadas; el round-trip en draw.io y las pruebas operativas siguen pendientes. Los estudios están formulados, no ejecutados; no hay pentest ni vulnerabilidad de un proveedor confirmada. Integración/uso requiere contratos, autorización del ambiente, evaluación institucional y evidencia propia.
