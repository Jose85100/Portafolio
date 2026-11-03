# Incremento temporal de revisiones completas (3 nov 2026)

## Pregunta, brecha e hipótesis

¿Puede el orden de filtros sobre una historia de adjudicaciones completas de identidad reactivar una revisión antigua al consultar un instante histórico? La extensión del 2 nov solo valida `effective_at` y `available_at` del snapshot; no define selección entre revisiones reemplazantes. Hipótesis de ingeniería H1: dado un cutoff `a` y un instante del hecho `t`, seleccionar la revisión más nueva disponible a `a` y después probar su intervalo válido da exactamente la decisión de una referencia independiente, y evita admisiones de versiones antiguas que una ablación filtrar-validar-primero puede resucitar.

## Notación, fórmula y condiciones

Para identidad `i`, historia `R_i={(r_j, a_j, e_j, u_j, x_j)}`, donde `a` es disponibilidad/sistema, `e` inicio válido, `u` fin válido (opcional, exclusivo), `x` el contenido completo. Para cutoff de conocimiento `A`:

\[
r^*(i,A)=\arg\max_{r_j\in R_i:a_j\le A} a_j.
\]

La respuesta para instante de identidad `T` es elegible si y solo si:

\[
e(r^*)\le T < u(r^*) \quad (u=+\infty\text{ si no hay fin}).
\]

La regla implementada es `latest(available_at <= A) THEN valid_interval(T)`. Las fechas se normalizan a UTC, intervalos son semiabiertos `[e,u)`, y empates de `available_at` más reciente se rechazan porque no hay regla de desempate probada. Sólo aplica a eventos de reemplazo completo con reloj de disponibilidad confiable. No es semántica universal de bases bitemporales ni permite rollback a la revisión previa.

La ablación que se intenta refutar aplica `valid_interval(T)` antes del `argmax`. Con `r0` abierto y `r1` disponible antes de `A` pero efectivo después de `T`, la ablación escoge `r0`; la regla completa escoge `r1`, detecta que `T` cae fuera de su intervalo y abstiene. Bajo semántica de reemplazo completo, la ausencia/retiro de vigencia es información, no permiso para restaurar una versión pasada. Esta interpretación se debe cambiar si el productor almacena deltas o conserva explícitamente intervalos superpuestos.

## Fórmula original, adaptación y propiedades

Original temporal: bitemporalidad distingue tiempo válido (cuándo es cierto en el mundo modelado) y tiempo transaccional/disponibilidad (cuándo consta en el sistema). Esta implementación adapta el orden a la interfaz de historial de identidad en esta cartera: first select by transaction/availability time, then test valid time. No propone una ley estadística ni un nuevo modelo temporal. Conserva corte prospectivo, intervalos UTC y abstención; añade que las filas son *full replacement*. Pierde aplicabilidad a logs incrementales, múltiples fuentes con autoridad distinta, correcciones concurrentes/ties y referencias bitemporales con varias afirmaciones vigentes. La propiedad verificada es concordancia con un oracle independiente sobre fixtures diseñadas; no hay demostración de correctitud para cualquier política de negocio ni validación de un sistema externo.

## Tres ideas candidatas

1. **Seleccionar latest-known y luego validar**: ataca directamente el hueco entre snapshot gate y versiones históricas; bajo costo; requiere contrato de reemplazo completo. Seleccionada.
2. **Materializar intervalos no superpuestos y consultar point-in-time**: correcta si el sistema asegura intervalos y retiene cada evento, pero requiere migrar almacenamiento compartido; descartada por alcance y contrato actual.
3. **Añadir firma/cadena de custodia a timestamps**: útil ante fechas falsas, pero el repo no tiene identidad de emisor, claves ni servicio de atestación; fuera del MVP.

Clasificación: adaptación de ingeniería y auditoría adversarial de orden temporal; no extensión metodológica original ni novedad científica. Los conceptos bitemporales y evitar filtración temporal son prior art. Diferencia concreta frente al propio repo: formaliza el comportamiento de full-replacement history, y conserva contraejemplo reproducible a una consulta filter-first.

## Experimento y configuración

`config_temporal1103.json` fija generador sintético (seed declarativa 1103; los enteros son una grilla determinista), 36 historiales, 10 cortes y 3 instantes de hecho: 1,080 consultas y 6 políticas comparadas. Oracle independiente: ordenar por `available_at` y validar el primero sin llamar al módulo productivo. El benchmark registra tiempo y peak de asignaciones Python, medidos con `perf_counter_ns`/`tracemalloc`; el coste incluye construcción/validación en proceso, excluye instalación, disco y base de datos. La figura de sensibilidad distingue disponibilidad de objetivo válido. Sin datos personales, empíricos ni entrenamiento.

## Interpretación y resultados

El comando `bash run_temporal_revisions.sh` ejecuta toda la suite acumulada, lint, mypy, matriz, costes y notebook narrativo. `results/temporal1103/summary.json` es la fuente exacta para cifras; `raw.csv` conserva cada consulta/política; `counterexample.json` conserva el fallo de la ablación. H1 de conformidad pasa si la política coincide con el oracle y no tiene falsos admitidos; esto solo prueba la grilla implementada. El mecanismo del contraejemplo es negativo y sí aparece en los casos donde una versión reemplazante más nueva ya está disponible pero no vigente en `T`. El baseline seguro `abstain_all` tiene cero falsos admitidos y falsos rechazos para medir el costo de abstención; no es un competidor predictivo. No se mide AUC, calidad de entity resolution ni fuga final de un modelo.

## Límites y siguientes pruebas

Confiamos en semántica de reemplazo, reloj UTC declarado y orden total de disponibilidades; no autenticamos esos datos. Datos de adjudicación incorrectos aún pueden pasar. Un empate es error explícito, no resolución automática. El ledger es in-memory O(m log m) por identidad si ordenar externamente; esta implementación escanea O(m) por llamada, no indexa historia y no mide escalabilidad de producción. La siguiente validación requiere fuente real con historial completo/retención verificable, cobertura de intervalos y revisión de si retiros tienen vigencia propia. No clamar seguridad point-in-time de todo el feature pipeline.
