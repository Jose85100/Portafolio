# Prior art focalizado — 2026-10-15

## Extensión de búsqueda 2026-10-16

Pregunta nueva: preservar decisiones y rechazo en el consumidor y JSON.
Verificadas fuentes primarias Python 3.12 json/Fraction, BIS BCBS239, NIST y
Acerbi–Tasche arXiv cond-mat/0104295. Consultas focalizadas SSRN sobre precisión
y ECB sobre ES devolvieron modelos predictivos, no contratos de transporte;
no se atribuye a esos artículos soporte de nuestro algoritmo. BIS es contexto
de integridad de datos, NO certificación regulatoria. La búsqueda parcial de
Semantic Scholar/Papers with Code/revistas no justifica ausencia ni prioridad.
Los métodos racionales y serialización son conocidos: novedad local de
integración, decisión antes del redondeo y rechazo explícito auditado.

Consultas ejecutadas: Python Fraction exact float; NumPy errstate/seterr underflow (documentación 2.1 verificada); NIST numerical reproducibility; Acerbi–Tasche ES; SSRN expected shortfall numerical precision; Semantic Scholar expected shortfall implementation; ECB ES working papers; Papers with Code ES. Se contrastó con los PR #32/#35 integrados y sus fuentes actuales.

Selección de ocho referencias en referencias.bib. Fractions, errstate, aritmética racional, representación hinge y ES por masa de cola son métodos existentes. El aporte es el guard concreto, su política/presupuesto y su evidencia sobre el código del portafolio. No se afirma prioridad científica ni búsqueda exhaustiva.

SSRN/ECB devolvieron investigación sobre precisión estadística, error de estimación y dinámica de colas. Esos problemas no equivalen a underflow aritmético y no se usan para respaldar una mejora de pronóstico. Semantic Scholar/Papers with Code no aportaron una implementación primaria decisiva en los resultados recibidos: cobertura parcial, no prueba de ausencia.

NIST y la documentación oficial apoyan tratar por separado precisión, representabilidad y estado de error. No se extrapola este guard a todos los errores IEEE ni a todas las bibliotecas/arquitecturas. BIS se usa solo como contexto general en los aportes previos: este ciclo no implementa requisitos regulatorios.
