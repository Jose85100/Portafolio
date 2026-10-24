# RAG normativo temporal

Estado: **M0 — diseño**, sin implementación ni evaluación empírica. Fecha: 2026-10-24.

## Pregunta y usuario

¿Qué disposición era aplicable a una fecha y territorio determinados? Usuario objetivo: profesional jurídico o equipo que trabaja bajo su revisión.

## Diseño de investigación

- Fuentes candidatas: SUIN, Diario Oficial y portales de autoridades emisoras. Verificar acceso, cobertura, permisos y vigencia antes de ingestión.
- Método propuesto: Búsqueda híbrida con filtro temporal previo y grafo de modificaciones por artículo.
- Hipótesis: el diseño reduce el error descrito abajo respecto de una búsqueda semántica sin filtros; puede refutarse si empeora cobertura o no reduce falsos aceptados.
- Error crítico: Texto consolidado actual recuperado para una pregunta histórica.
- Experimento: Comparar BM25 sin fechas frente a recuperación temporal; medir artículos aplicables recuperados y respuestas con vigencia sin verificar.

## Entregable y criterio de avance

Paquete de evidencia con consulta, fecha de corte, filtros, documentos, pasajes, hashes, afirmaciones y pendientes. Aplicar [contratos](../../docs/CONTRACTS.md) y [validaciones](../../docs/VALIDATION.md).

Para avanzar a M1: corpus con permiso y versiones, baseline reproducible, casos etiquetados, código ejecutable y resultados reales de la corrida. Para M2: pruebas, contratos y revisión técnica. No asignar madurez por volumen de documentación.

Separar conjunto de desarrollo y prueba por documento y familia de casos; fijar snapshot antes de evaluar. Reportar denominadores, incertidumbre, abstenciones y errores por dominio. La aceptación jurídica requiere revisión profesional; una puntuación de similitud no prueba aplicabilidad.
