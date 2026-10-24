# Laboral y seguridad social

Estado: **M0 — diseño**, sin implementación ni evaluación empírica. Fecha: 2026-10-24.

## Pregunta y usuario

¿Qué régimen y evidencia deben examinarse antes de responder? Usuario objetivo: profesional jurídico o equipo que trabaja bajo su revisión.

## Diseño de investigación

- Fuentes candidatas: Normas y jurisprudencia oficiales más documentos autorizados. Verificar acceso, cobertura, permisos y vigencia antes de ingestión.
- Método propuesto: Router por vínculo, régimen, fecha y hechos; recuperación de excepciones.
- Hipótesis: el diseño reduce el error descrito abajo respecto de una búsqueda semántica sin filtros; puede refutarse si empeora cobertura o no reduce falsos aceptados.
- Error crítico: Trasladar reglas de empleo privado a un servidor público sin análisis.
- Experimento: Pares mínimos con igual pregunta y distinto régimen; medir abstención y errores de régimen.

## Entregable y criterio de avance

Paquete de evidencia con consulta, fecha de corte, filtros, documentos, pasajes, hashes, afirmaciones y pendientes. Aplicar [contratos](../../docs/CONTRACTS.md) y [validaciones](../../docs/VALIDATION.md).

Para avanzar a M1: corpus con permiso y versiones, baseline reproducible, casos etiquetados, código ejecutable y resultados reales de la corrida. Para M2: pruebas, contratos y revisión técnica. No asignar madurez por volumen de documentación.

Separar conjunto de desarrollo y prueba por documento y familia de casos; fijar snapshot antes de evaluar. Reportar denominadores, incertidumbre, abstenciones y errores por dominio. La aceptación jurídica requiere revisión profesional; una puntuación de similitud no prueba aplicabilidad.
