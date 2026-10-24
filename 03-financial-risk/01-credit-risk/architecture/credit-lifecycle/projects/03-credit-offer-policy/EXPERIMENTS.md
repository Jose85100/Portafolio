# Experimentos propuestos · Ofertas de crédito bajo capacidad y exposición

Tres ideas de investigación; **ninguna ejecutada en esta entrega**. Registro estructurado en [projects.json](../projects.json). Criterios y tolerancias se fijarán antes del test de cada prototipo; no se inventan resultados o porcentajes de mejora. Las referencias adversariales apuntan a [SECURITY_REVIEW.md](SECURITY_REVIEW.md).

## OFFER-01 · Menú fijo frente a asignación bajo presupuesto

**Hipótesis falsable:** Una política optimizada puede redistribuir exposición con el mismo menú y presupuesto, aunque no mejore la aprobación.

**Estimando, objetivo o invariante:**

\[
\Delta NPV=NPV_{asignacion}-NPV_{reglas}
\]

**Diseño y comparador:** Generar lotes pequeños con ofertas y restricciones; contrastar solver futuro con enumeración independiente. Mantener el mismo presupuesto, elegibilidad y costo de revisión.

**Métricas e incertidumbre:** Factibilidad, reconciliación de objetivo, exposición, NPV supuesto y distribución de ofertas.

**Qué refuta la propuesta:** Descartar si la mejora proviene de relajar elegibilidad o comparar menús/costos diferentes.

**Revisión adversarial:** escenarios OFFER-A1, OFFER-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Oráculo de enumeración y benchmark de asignación por exposición.

## OFFER-02 · Ingreso irregular y estrés de capacidad

**Hipótesis falsable:** Una decisión basada en un solo promedio puede ser frágil ante estacionalidad o gasto esencial.

**Estimando, objetivo o invariante:**

\[
F_{libre,s}=I_s-G_s-D_{existente}-cuota_a
\]

**Diseño y comparador:** Cohortes sintéticas de ingreso estable/estacional, omisiones y deuda concurrente; comparar promedio, cuantiles y escenarios adversos con política congelada.

**Métricas e incertidumbre:** Fracción de escenarios con flujo negativo, cobertura, abstención y costo/beneficio condicionado a supuestos.

**Qué refuta la propuesta:** No presentar un cuantil de ingreso como garantía de capacidad ni elegir retrospectivamente el escenario favorable.

**Revisión adversarial:** escenarios OFFER-A2, OFFER-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Laboratorio de ofertas y tabla de sensibilidad por tipo de ingreso.

## OFFER-03 · Oferta concurrente y reserva

**Hipótesis falsable:** Dos ofertas individualmente factibles pueden sobreconsumir exposición si comparten un límite no reservado.

**Estimando, objetivo o invariante:**

\[
used+reserved+new\_reservation\le limit
\]

**Diseño y comparador:** Intercalar dos solicitudes, vencimiento y cancelación; comparar lectura sin reserva, reserva atómica y liberación tras estado de pago conocido.

**Métricas e incertidumbre:** Sobreasignación, reservas huérfanas, espera y cantidad de ofertas inconsistentes.

**Qué refuta la propuesta:** Una política queda descartada ante una secuencia admitida que exceda el límite o libere una reserva ya liquidada.

**Revisión adversarial:** escenarios OFFER-A3, OFFER-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Corpus de intercalados y especificación de invariantes de reserva.

## Disciplina de evaluación

Separar desarrollo/test por el tiempo y la entidad apropiada; elegir denominadores y reglas de faltantes antes de evaluar. Guardar configuración, semilla, versión de generador, hashes y entorno. Mantener la misma población, menú, presupuesto y costos cuando se compare una política. Reportar estados desconocidos y resultados negativos. La capacidad de reproducir un ataque sintético no demuestra prevalencia ni vulnerabilidad de un proveedor real.

Si se usa un experimento anterior como baseline, citar su evidencia, conservar sus límites y medir la extensión por separado. La autorrevisión documentada no es validación independiente ni aprobación operacional.
