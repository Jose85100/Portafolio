# Experimentos propuestos · Workflow durable de originación y excepciones

Tres ideas de investigación; **ninguna ejecutada en esta entrega**. Registro estructurado en [projects.json](../projects.json). Criterios y tolerancias se fijarán antes del test de cada prototipo; no se inventan resultados o porcentajes de mejora. Las referencias adversariales apuntan a [SECURITY_REVIEW.md](SECURITY_REVIEW.md).

## WF-01 · Callbacks fuera de orden y duplicados

**Hipótesis falsable:** Un guard de versión evita avanzar por eventos ya consumidos o semánticamente obsoletos.

**Estimando, objetivo o invariante:**

\[
T(T(s,e),e)=T(s,e)\quad\text{para evento idempotente}
\]

**Diseño y comparador:** Enumerar permutaciones pequeñas de verificación, rechazo técnico, callback y expiración; usar una máquina de estados de referencia independiente.

**Métricas e incertidumbre:** Transiciones inválidas, resultados finales divergentes, duplicados consumidos y eventos pendientes.

**Qué refuta la propuesta:** Descartar si un orden admitido permite oferta sin evidencia vigente o efecto duplicado.

**Revisión adversarial:** escenarios WF-A1, WF-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Tabla de transición y corpus de permutaciones para un prototipo futuro.

## WF-02 · Fallo entre estado y publicación

**Hipótesis falsable:** Registrar estado sin evento, o evento sin estado, puede dejar el proceso inconsistente.

**Estimando, objetivo o invariante:**

\[
commit(state,outbox)\in\{both,neither\}
\]

**Diseño y comparador:** Inyectar fallos antes/después del commit y de la publicación; comparar publicación directa con outbox transaccional e idempotencia del consumidor.

**Métricas e incertidumbre:** Eventos perdidos, duplicados inocuos, recuperación y decisiones sin registro de causa.

**Qué refuta la propuesta:** No aceptar el diseño si requiere que dos commits remotos sean atómicos por suposición.

**Revisión adversarial:** escenarios WF-A2, WF-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Matriz de puntos de caída y replay de recuperación.

## WF-03 · Revisión humana con evidencia nueva

**Hipótesis falsable:** Una excepción solo es reproducible si conserva evidencia, atribución y vigencia.

**Estimando, objetivo o invariante:**

\[
valid\_override=authorized\land evidence\_linked\land version\_current
\]

**Diseño y comparador:** Escenarios con analista autorizado/no autorizado, oferta modificada, evidencia posterior y tarea vencida; separar nuevas decisiones de reescritura del historial.

**Métricas e incertidumbre:** Overrides explicables, bloqueos correctos, latencia de tareas y estados abandonados.

**Qué refuta la propuesta:** Cualquier override sin autoridad o sobre términos no aceptados invalida el flujo.

**Revisión adversarial:** escenarios WF-A3, WF-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Contrato de tarea humana y reporte de trazabilidad de excepciones.

## Disciplina de evaluación

Separar desarrollo/test por el tiempo y la entidad apropiada; elegir denominadores y reglas de faltantes antes de evaluar. Guardar configuración, semilla, versión de generador, hashes y entorno. Mantener la misma población, menú, presupuesto y costos cuando se compare una política. Reportar estados desconocidos y resultados negativos. La capacidad de reproducir un ataque sintético no demuestra prevalencia ni vulnerabilidad de un proveedor real.

Si se usa un experimento anterior como baseline, citar su evidencia, conservar sus límites y medir la extensión por separado. La autorrevisión documentada no es validación independiente ni aprobación operacional.
