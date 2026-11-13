# Experimentos propuestos · Orquestación de proveedores, costo y resiliencia

Tres ideas de investigación; **ninguna ejecutada en esta entrega**. Registro estructurado en [projects.json](../projects.json). Criterios y tolerancias se fijarán antes del test de cada prototipo; no se inventan resultados o porcentajes de mejora. Las referencias adversariales apuntan a [SECURITY_REVIEW.md](SECURITY_REVIEW.md).

## PROV-01 · Orden de consulta por información incremental

**Hipótesis falsable:** Una segunda consulta puede no compensar si repite evidencia ya disponible.

**Estimando, objetivo o invariante:**

\[
VOI_a=C_{sin\ consulta}-\mathbb E[C_{con\ Y_a}]-c_a
\]

**Diseño y comparador:** Problema pequeño de dos/tres fuentes con probabilidades conocidas en laboratorio; enumerar políticas admisibles como oráculo y comparar orden fijo/adaptativo al mismo costo, latencia y menú terminal.

**Métricas e incertidumbre:** Costo esperado, regret frente al oráculo, consultas por caso y uso de revisión.

**Qué refuta la propuesta:** Descartar ventaja si depende de probabilidades oráculo incompatibles con la población o de excluir los casos sin cobertura.

**Revisión adversarial:** escenarios PROV-A1, PROV-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Prototipo futuro con enumeración pequeña y curvas de sensibilidad a probabilidades mal especificadas.

## PROV-02 · Dependencia y caída compartida

**Hipótesis falsable:** Dos fuentes comercialmente distintas pueden aportar menos resiliencia de la que su disponibilidad marginal sugiere.

**Estimando, objetivo o invariante:**

\[
P(U_A,U_B)=P(U_A)P(U_B\mid U_A)
\]

**Diseño y comparador:** Extender el notebook existente con un factor de caída compartida, límite de reintentos y costos de espera; conservar solicitudes entre políticas y reportar pendientes manuales y externos.

**Métricas e incertidumbre:** Cobertura efectiva, pérdida/costo bajo supuestos, picos de cola, espera y llamadas facturables.

**Qué refuta la propuesta:** No llamar robusta a una ruta que solo funciona con capacidad manual o llamadas ilimitadas.

**Revisión adversarial:** escenarios PROV-A2, PROV-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Matriz de escenarios y replay de fallos controlados; datos sintéticos.

## PROV-03 · Cambio silencioso de versión/cobertura

**Hipótesis falsable:** El comportamiento del proveedor puede cambiar aunque el esquema de API no cambie.

**Estimando, objetivo o invariante:**

\[
\Delta_c=P(covered\mid version_2,c)-P(covered\mid version_1,c)
\]

**Diseño y comparador:** Replay pareado de un corpus congelado con dos versiones simuladas y poblaciones distintas; comparar cobertura, razones, semántica del score y calibración sin usar test para reajustar.

**Métricas e incertidumbre:** Diferencia por canal, calidad de razones, costo incremental y casos no reproducibles.

**Qué refuta la propuesta:** Bloquear una conclusión de mejora si las poblaciones o el concepto de score dejaron de ser comparables.

**Revisión adversarial:** escenarios PROV-A3, PROV-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Ficha de aceptación de versión y reporte de shadow por cohortes.

## Disciplina de evaluación

Separar desarrollo/test por el tiempo y la entidad apropiada; elegir denominadores y reglas de faltantes antes de evaluar. Guardar configuración, semilla, versión de generador, hashes y entorno. Mantener la misma población, menú, presupuesto y costos cuando se compare una política. Reportar estados desconocidos y resultados negativos. La capacidad de reproducir un ataque sintético no demuestra prevalencia ni vulnerabilidad de un proveedor real.

Si se usa un experimento anterior como baseline, citar su evidencia, conservar sus límites y medir la extensión por separado. La autorrevisión documentada no es validación independiente ni aprobación operacional.
