# Validador de citas jurídicas

Estado: **M0 — diseño**, sin implementación ni evaluación empírica. Fecha: 2026-10-24.

## Pregunta y usuario

¿Existe la referencia y respalda exactamente la afirmación? Usuario objetivo: profesional jurídico o equipo que trabaja bajo su revisión.

## Diseño de investigación

- Fuentes candidatas: Documentos oficiales preservados con hash y localizador. Verificar acceso, cobertura, permisos y vigencia antes de ingestión.
- Método propuesto: Resolución de identificadores, cotejo literal y evaluación de soporte contextual.
- Hipótesis: el diseño reduce el error descrito abajo respecto de una búsqueda semántica sin filtros; puede refutarse si empeora cobertura o no reduce falsos aceptados.
- Error crítico: Sentencia existente citada para una conclusión que no contiene.
- Experimento: Inyectar identificadores falsos, citas truncadas y atribuciones erróneas; medir falsos aceptados por separado.

## Entregable y criterio de avance

Paquete de evidencia con consulta, fecha de corte, filtros, documentos, pasajes, hashes, afirmaciones y pendientes. Aplicar [contratos](../../docs/CONTRACTS.md) y [validaciones](../../docs/VALIDATION.md).

Para avanzar a M1: corpus con permiso y versiones, baseline reproducible, casos etiquetados, código ejecutable y resultados reales de la corrida. Para M2: pruebas, contratos y revisión técnica. No asignar madurez por volumen de documentación.

Separar conjunto de desarrollo y prueba por documento y familia de casos; fijar snapshot antes de evaluar. Reportar denominadores, incertidumbre, abstenciones y errores por dominio. La aceptación jurídica requiere revisión profesional; una puntuación de similitud no prueba aplicabilidad.
