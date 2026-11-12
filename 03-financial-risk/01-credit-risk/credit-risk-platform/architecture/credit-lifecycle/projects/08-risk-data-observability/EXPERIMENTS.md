# Experimentos propuestos · Observabilidad de datos, etiquetas y modelos

Tres ideas de investigación; **ninguna ejecutada en esta entrega**. Registro estructurado en [projects.json](../projects.json). Criterios y tolerancias se fijarán antes del test de cada prototipo; no se inventan resultados o porcentajes de mejora. Las referencias adversariales apuntan a [SECURITY_REVIEW.md](SECURITY_REVIEW.md).

## OBS-01 · Maduración y métricas de riesgo

**Hipótesis falsable:** Tratar labels pendientes como negativos produce una falsa mejora de default/fraude.

**Estimando, objetivo o invariante:**

\[
rate_{mature}=events_{mature}/N_{mature}
\]

**Diseño y comparador:** Generar atraso de label dependiente de canal y resultado; comparar rate ingenuo, ventanas maduras y estimación explícita de censura con sus supuestos.

**Métricas e incertidumbre:** Sesgo por cohorte, tamaño evaluable y cobertura de incertidumbre.

**Qué refuta la propuesta:** No publicar una tasa como comparable si cambian la edad de cohorte o los casos observables.

**Revisión adversarial:** escenarios OBS-A1, OBS-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Generador de disponibilidad y tablero futuro de madurez.

## OBS-02 · Fuente o modelo: atribución del cambio

**Hipótesis falsable:** La caída de cobertura puede explicar un salto de score sin cambio del comportamiento económico.

**Estimando, objetivo o invariante:**

\[
\Delta=metric(version_2,population)-metric(version_1,population)
\]

**Diseño y comparador:** Diseño factorial de mezcla poblacional, versión de proveedor e imputación con corpus congelado; replay pareado para separar cambios y sin afirmar causalidad fuera del laboratorio.

**Métricas e incertidumbre:** Cobertura, score, calibración madura y costo por fuente/canal.

**Qué refuta la propuesta:** Rechazar atribución al modelo si el contraste no fija población/versión de entradas.

**Revisión adversarial:** escenarios OBS-A2, OBS-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Reporte de descomposición y reglas para abrir investigación.

## OBS-03 · Alertas múltiples por horizonte

**Hipótesis falsable:** Umbrales por canal independientes pueden generar demasiados incidentes al vigilar muchos canales.

**Estimando, objetivo o invariante:**

\[
P(\exists\ false\ alert\ en\ horizonte)
\]

**Diseño y comparador:** Simular series dependientes y referencias contaminadas; comparar umbral individual con calibración conjunta de máximo o procedimiento por lote apropiado, explicitando supuestos.

**Métricas e incertidumbre:** Falsas alarmas por horizonte, demora, poder y carga operativa.

**Qué refuta la propuesta:** No usar garantía por lote como garantía online ni mantenerla bajo deriva no modelada.

**Revisión adversarial:** escenarios OBS-A3, OBS-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Benchmark de monitoreo con escenarios nulos y cambios controlados.

## Disciplina de evaluación

Separar desarrollo/test por el tiempo y la entidad apropiada; elegir denominadores y reglas de faltantes antes de evaluar. Guardar configuración, semilla, versión de generador, hashes y entorno. Mantener la misma población, menú, presupuesto y costos cuando se compare una política. Reportar estados desconocidos y resultados negativos. La capacidad de reproducir un ataque sintético no demuestra prevalencia ni vulnerabilidad de un proveedor real.

Si se usa un experimento anterior como baseline, citar su evidencia, conservar sus límites y medir la extensión por separado. La autorrevisión documentada no es validación independiente ni aprobación operacional.
