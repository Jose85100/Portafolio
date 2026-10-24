# Jurisprudencia y precedente

Estado: **M0 — diseño**, sin implementación ni evaluación empírica. Fecha: 2026-10-24.

## Pregunta y usuario

¿Qué decisiones apoyan o contradicen una tesis y por qué son comparables? Usuario objetivo: profesional jurídico o equipo que trabaja bajo su revisión.

## Diseño de investigación

- Fuentes candidatas: Relatorías de Corte Constitucional, Corte Suprema y Consejo de Estado. Verificar acceso, cobertura, permisos y vigencia antes de ingestión.
- Método propuesto: Grafo de citas, extracción de hechos y separación de ratio, obiter, resolutiva y salvamentos.
- Hipótesis: el diseño reduce el error descrito abajo respecto de una búsqueda semántica sin filtros; puede refutarse si empeora cobertura o no reduce falsos aceptados.
- Error crítico: Tratar una similitud semántica o un salvamento como regla vinculante.
- Experimento: Abogado etiqueta comparabilidad y función del pasaje; medir nDCG y confusión de tipos de fragmento.

## Entregable y criterio de avance

Paquete de evidencia con consulta, fecha de corte, filtros, documentos, pasajes, hashes, afirmaciones y pendientes. Aplicar [contratos](../../docs/CONTRACTS.md) y [validaciones](../../docs/VALIDATION.md).

Para avanzar a M1: corpus con permiso y versiones, baseline reproducible, casos etiquetados, código ejecutable y resultados reales de la corrida. Para M2: pruebas, contratos y revisión técnica. No asignar madurez por volumen de documentación.

Separar conjunto de desarrollo y prueba por documento y familia de casos; fijar snapshot antes de evaluar. Reportar denominadores, incertidumbre, abstenciones y errores por dominio. La aceptación jurídica requiere revisión profesional; una puntuación de similitud no prueba aplicabilidad.
