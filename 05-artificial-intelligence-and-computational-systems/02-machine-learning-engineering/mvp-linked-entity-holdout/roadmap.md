# Roadmap acumulativo

|Orden|Ruta|Pregunta/criterio|Estado|
|---|---|---|---|
|1|src/balancing.py + tests/test_balancing.py|Óptimo por masa con0 cortes, oracle exhaustivo|Ejecutado30, revisor independiente reprodujo pipeline y núcleo sin bloqueantes|
|2|tests/test_balancing.py|Vínculos falsos/faltantes adjudicados, medir errores del grafo y grupos gigantes|Pendiente; no medir sobre el mismo grafo como verdad externa|
|3|src/splitter.py|Snapshot temporal sin enlaces conocidos después del corte|Pendiente definición del contrato temporal|
|4|src/balancing_experiment.py|Más de60 grupos; presupuestos y reconstrucción más eficiente|Pendiente; sin claim escalable|

Continuar si0 cortes del grafo declarado y déficit tolerable; ajustar si grupo gigante impide presupuesto; cerrar cualquier despliegue si origen de links o fecha no auditables. El umbral de utilidad de negocio necesita dueño y datos reales.

## Actualización31

Hito2 cerrado solo en diseño sintético: src/graph_audit.py + notebook_graph_audit.ipynb diagnostican falsos merges/faltantes contra verdad explícita; pendientes adjudicación real y temporal. Siguiente: contrato de fuente adjudicada con fecha y cobertura, sin inferir verdad del grafo auditado. Hito: rechazar links conocidos después del corte y producir manifiesto completo. Alternativa: adjudicación parcial con abstención y cota honesta, sin extrapolar a no adjudicados. Mantener optimización de DP como prioridad posterior; coste científico de ignorar calidad del grafo supera su balance en los negativos31.

## Actualización2026-11-01

Hito parcial ejecutado: src/partial_audit.py y notebook_partial_audit.ipynb recuperan caso31 y devuelven extremos exactos bajo equivalencia parcial completa;5508 verificaciones exhaustivas,480 escenarios. No resuelve adjudicación real ni su fecha. Continuar con contrato de disponibilidad temporal/procedencia (validar timestamps y origen de cannot-links); criterio: rechazar información posterior al corte y separar diagnóstico retrospectivo. Ajustar si solo existen enlaces positivos: actual supuesto no aplica, mantener abstención/conjunto más amplio. Cerrar uso si alguien interpreta conditional-zero como garantía empírica sin adjudicación auditada. DP eficiente permanece pendiente, sin claim de escalabilidad del splitter por medir solo auditor.
