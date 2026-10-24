# Ciclo completo de crédito: arquitecturas, flujos y señales

Corte **23 de octubre de 2026, Colombia**. Extensión del [mapa de referencia](../README.md) y de las [cuatro arquitecturas defensivas de fraude](../../fraud-and-anomaly-research/ai-enabled-fraud-defense/diagrams/README.md). El mapa base contiene **nueve diagramas editables**: tres variantes de plataforma y seis vistas de proceso/datos. Se organiza ahora en [diez proyectos y treinta ideas](projects/README.md), con [ocho capas defensivas adicionales](defense-layers/README.md) y cuatro overlays editables. Con las cuatro vistas previas de fraude, quedan **17 vistas complementarias en tres archivos draw.io**, no 17 servicios ni plataformas implementadas.

Las arquitecturas nuevas son **S1: diseño de referencia**. El repositorio sigue limitado a ejemplos y datos sintéticos; no conectar PII ni ejecutar autorizaciones reales. La profundidad se mide por decisiones, contratos y fallos cubiertos, no por número de cajas.

| Lectura | Contenido |
|---|---|
| [Diez proyectos](projects/README.md) | Carpetas propias, 30 ideas, contratos sintéticos y ruta S1 → S2 |
| [Revisión adversarial](projects/THREAT_MODEL.md) | 40 escenarios propuestos; teléfono, documento, fuentes, roles y efectos |
| [Ocho capas defensivas](defense-layers/README.md) | 16 estudios transversales y cuatro vistas nuevas |
| [Capas y variantes](ARCHITECTURES.md) | 15 responsabilidades y tres alternativas de despliegue con criterios para elegir |
| [Proceso completo](PROCESS_FLOWS.md) | Ocho flujos con caminos alternativos, responsables y controles |
| [Qué información puede captar un banco](DATA_SIGNALS.md) | IP, geolocalización, dispositivo, identidad, ingresos, crédito, pagos y comportamiento |
| [Catálogo de señales](signal_catalog.csv) | 35 señales con fuente, finalidad, limitación y condición de captura |
| [Proveedores concretos](PROVIDERS.md) | 24 candidatos y productos, cobertura documentada y preguntas pendientes |
| [Colombia: uso de datos](COLOMBIA_DATA_USE.md) | Separación entre acceso técnico, tratamiento autorizado y decisión admisible |
| [Modelos y decisiones](MODELS_AND_DECISIONS.md) | Qué motor actúa en cada etapa, ecuaciones y distinción fraude/crédito |
| [Diagramas draw.io y SVG](diagrams/README.md) | Nueve páginas nuevas, más enlace a las cuatro previas |
| [Evidencia de revisión](evidence/qa.json) | Validación estructural, regeneración y alcance de inspección |

## Respuesta práctica: IP y geolocalización

**Sí pueden ser señales de seguridad**, bajo el análisis de finalidad y habilitación aplicable. IP observada, geolocalización derivada de IP y ubicación facilitada por el dispositivo son tres datos diferentes. Ninguno demuestra por sí solo identidad, fraude ni capacidad de pago. El diseño propone usarlos primero para verificar contexto, detectar cambios y decidir verificación adicional; cualquier uso en underwriting exige justificación y validación específicas.

La selección inicial sugerida es reducida: IP/contexto de sesión, identificador de instalación de alcance limitado, eventos de formulario sin contenido secreto, verificación documental y de ingresos, historia crediticia autorizada, cuenta destino y resultados de pago. La ubicación precisa no es un requisito universal; incluirla solo si existe una necesidad demostrada y una ruta alternativa. La matriz detalla lo que se observa directamente, lo que se estima y lo que requiere permiso o una fuente contratada.

## Cómo encajan las piezas

El LOS conserva solicitud y expediente. El motor de decisión aplica reglas/modelos/política congelada. El LMS/core administra la obligación y su ledger. El sistema de pagos ejecuta efectos autorizados y concilia. La plataforma de datos conserva snapshots y etiquetas. El sistema de cobranza propone tratamientos dentro de canales y límites aplicables. Ningún score de fraude sustituye esas responsabilidades.

Reutilizar [contratos](../../contracts/README.md), [modelo relacional](../../database/README.md), [productos de crédito](../../credit-risk-products/), [estrategia de cartera](../../credit-portfolio-strategy/) y [motor de pérdida por fraude](../../fraud-and-anomaly-research/loss-minimization-engine/README.md). No se copia el motor dentro de esta documentación ni se cambia su madurez.

**Criterio de entrega:** los diagramas muestran una arquitectura propuesta, no conexiones contratadas. Las capacidades de proveedores provienen de fuentes propias, sin evaluación comparativa, precios o garantía de operación en Colombia. Las fuentes legales sirven para diseñar controles; la implantación requiere revisión del caso por las áreas competentes.
