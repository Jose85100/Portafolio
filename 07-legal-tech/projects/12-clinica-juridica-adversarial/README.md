# Clínica jurídica adversarial

Estado: **M0 — diseño**, sin implementación ni evaluación empírica. Fecha: 2026-10-24.

## Pregunta y usuario

¿Resiste la respuesta contraargumentos, excepciones y fuentes contradictorias? Usuario objetivo: profesional jurídico o equipo que trabaja bajo su revisión.

## Diseño de investigación

- Fuentes candidatas: Paquetes de evidencia de los otros proyectos. Verificar acceso, cobertura, permisos y vigencia antes de ingestión.
- Método propuesto: Agente proponente, contradictor y revisor con expediente común trazable.
- Hipótesis: el diseño reduce el error descrito abajo respecto de una búsqueda semántica sin filtros; puede refutarse si empeora cobertura o no reduce falsos aceptados.
- Error crítico: Consenso entre agentes que comparten una fuente falsa.
- Experimento: Comparar un agente con revisión adversarial; medir errores detectados, errores nuevos y costo por caso.

## Entregable y criterio de avance

Paquete de evidencia con consulta, fecha de corte, filtros, documentos, pasajes, hashes, afirmaciones y pendientes. Aplicar [contratos](../../docs/CONTRACTS.md) y [validaciones](../../docs/VALIDATION.md).

Para avanzar a M1: corpus con permiso y versiones, baseline reproducible, casos etiquetados, código ejecutable y resultados reales de la corrida. Para M2: pruebas, contratos y revisión técnica. No asignar madurez por volumen de documentación.

Separar conjunto de desarrollo y prueba por documento y familia de casos; fijar snapshot antes de evaluar. Reportar denominadores, incertidumbre, abstenciones y errores por dominio. La aceptación jurídica requiere revisión profesional; una puntuación de similitud no prueba aplicabilidad.
