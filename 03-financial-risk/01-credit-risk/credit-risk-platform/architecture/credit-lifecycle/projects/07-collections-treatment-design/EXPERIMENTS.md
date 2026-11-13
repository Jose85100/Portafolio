# Experimentos propuestos · Tratamientos de cobranza y recuperación sostenible

Tres ideas de investigación; **ninguna ejecutada en esta entrega**. Registro estructurado en [projects.json](../projects.json). Criterios y tolerancias se fijarán antes del test de cada prototipo; no se inventan resultados o porcentajes de mejora. Las referencias adversariales apuntan a [SECURITY_REVIEW.md](SECURITY_REVIEW.md).

## COLL-01 · Sesgo de selección del contacto

**Hipótesis falsable:** Comparar solo contactados puede atribuir eficacia a una selección de clientes más fáciles.

**Estimando, objetivo o invariante:**

\[
\hat V_{IPW}(\pi)=N^{-1}\sum_i R_i1[A_i=\pi(X_i)]/p(A_i\mid X_i)
\]

**Diseño y comparador:** Laboratorio con política de asignación conocida, confusión observada y un caso sin positividad; comparar naïve, ponderación y verdad generada. No extrapolar el estimador a datos reales sin supuestos.

**Métricas e incertidumbre:** Sesgo, varianza, pesos extremos, soporte y recuperación neta estimada.

**Qué refuta la propuesta:** Declarar no identificable cuando falte soporte o haya confusión no controlada; no rellenar valor con cero.

**Revisión adversarial:** escenarios COLL-A1, COLL-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Notebook futuro de selección/positividad y ficha de diseño causal.

## COLL-02 · Elegibilidad concurrente de campañas

**Hipótesis falsable:** Un control central puede impedir que campañas individualmente válidas excedan límites compartidos.

**Estimando, objetivo o invariante:**

\[
admissible(a,t)=channel\_allowed\land limit\_available\land balance\_valid
\]

**Diseño y comparador:** Intercalar campañas internas/tercerizadas con intentos, contacto efectivo y cambios de preferencia; usar reglas parametrizadas y verificadas antes de despliegue.

**Métricas e incertidumbre:** Contactos indebidos, restricciones respetadas, duplicados y oportunidad de atención.

**Qué refuta la propuesta:** Cualquier contacto que viole el contrato vigente invalida el plan, aunque mejore recaudo simulado.

**Revisión adversarial:** escenarios COLL-A2, COLL-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Modelo de referencia de elegibilidad y eventos entre campañas.

## COLL-03 · Acuerdo frente a cura sostenible

**Hipótesis falsable:** Contar acuerdos como éxito puede mejorar la métrica sin mejorar recuperación sostenida.

**Estimando, objetivo o invariante:**

\[
net\_recovery=\sum_t CF_t/(1+r)^t-cost
\]

**Diseño y comparador:** Cohortes sintéticas con promesas, pagos parciales, recaída y costos de gestión; comparar conteo de acuerdos, flujo neto y estado de cura en horizonte fijado.

**Métricas e incertidumbre:** Cumplimiento, recaída, recuperación neta, costo y reclamaciones.

**Qué refuta la propuesta:** Descartar un criterio que favorezca acuerdos nominales sin pagos o que compare horizontes incompatibles.

**Revisión adversarial:** escenarios COLL-A3, COLL-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Definiciones de outcome y reporte por cohortes maduras.

## Disciplina de evaluación

Separar desarrollo/test por el tiempo y la entidad apropiada; elegir denominadores y reglas de faltantes antes de evaluar. Guardar configuración, semilla, versión de generador, hashes y entorno. Mantener la misma población, menú, presupuesto y costos cuando se compare una política. Reportar estados desconocidos y resultados negativos. La capacidad de reproducir un ataque sintético no demuestra prevalencia ni vulnerabilidad de un proveedor real.

Si se usa un experimento anterior como baseline, citar su evidencia, conservar sus límites y medir la extensión por separado. La autorrevisión documentada no es validación independiente ni aprobación operacional.
