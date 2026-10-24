# Experimentos propuestos · Calidad del ledger y estado de la obligación

Tres ideas de investigación; **ninguna ejecutada en esta entrega**. Registro estructurado en [projects.json](../projects.json). Criterios y tolerancias se fijarán antes del test de cada prototipo; no se inventan resultados o porcentajes de mejora. Las referencias adversariales apuntan a [SECURITY_REVIEW.md](SECURITY_REVIEW.md).

## SERV-01 · Pago no imputado frente a mora real

**Hipótesis falsable:** Conciliar pagos antes del cálculo de DPD reduce clasificación operacionalmente incorrecta.

**Estimando, objetivo o invariante:**

\[
false\_dpd=1[DPD_{observado}>0\land DPD_{referencia}=0]
\]

**Diseño y comparador:** Crear un ledger pequeño verificable con pagos puntuales, parciales, retrasados en transmisión y mal referenciados; contrastar cronograma+ledger con un oráculo manual del contrato sintético.

**Métricas e incertidumbre:** Error de saldo/DPD, casos enviados erróneamente a cobranza y tiempo de resolución.

**Qué refuta la propuesta:** Descartar si mejora mora agregada ocultando partidas sin conciliar o reclasificando pagos no confirmados como efectivos.

**Revisión adversarial:** escenarios SERV-A1, SERV-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Fixtures futuros de ledger y conciliación de DPD por obligación.

## SERV-02 · Corrección bitemporal

**Hipótesis falsable:** Una corrección conocida hoy no puede aparecer como información conocida en una decisión anterior.

**Estimando, objetivo o invariante:**

\[
known(e,t)=1[event\_time_e\le t\land available\_time_e\le t]
\]

**Diseño y comparador:** Introducir pagos retroactivos y correcciones con distintas fechas de disponibilidad; reconstruir decisiones al corte y comparar con reconstrucción contaminada por información futura.

**Métricas e incertidumbre:** Fugas detectadas, snapshots reproducibles y cambios legítimos de estado.

**Qué refuta la propuesta:** Cualquier feature histórica dependiente de una corrección aún no conocida invalida el snapshot.

**Revisión adversarial:** escenarios SERV-A2, SERV-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Benchmark de replay al corte y linaje de correcciones.

## SERV-03 · Cambios de calendario y producto

**Hipótesis falsable:** Un cambio de convención puede desplazar cohortes de mora sin cambio de conducta del cliente.

**Estimando, objetivo o invariante:**

\[
\Delta DPD_i=DPD_i(calendar_2)-DPD_i(calendar_1)
\]

**Diseño y comparador:** Mismos pagos con fines de semana, fechas límite, prepago y reestructuración; comparar políticas únicamente sobre productos/cambios expresamente definidos en laboratorio.

**Métricas e incertidumbre:** Desplazamiento de DPD, transición de bandas y efecto en alertas/acciones.

**Qué refuta la propuesta:** No atribuir a riesgo un salto explicado por convención administrativa o por una migración inconsistente.

**Revisión adversarial:** escenarios SERV-A3, SERV-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Reporte de equivalencia semántica para migración de LMS.

## Disciplina de evaluación

Separar desarrollo/test por el tiempo y la entidad apropiada; elegir denominadores y reglas de faltantes antes de evaluar. Guardar configuración, semilla, versión de generador, hashes y entorno. Mantener la misma población, menú, presupuesto y costos cuando se compare una política. Reportar estados desconocidos y resultados negativos. La capacidad de reproducir un ataque sintético no demuestra prevalencia ni vulnerabilidad de un proveedor real.

Si se usa un experimento anterior como baseline, citar su evidencia, conservar sus límites y medir la extensión por separado. La autorrevisión documentada no es validación independiente ni aprobación operacional.
