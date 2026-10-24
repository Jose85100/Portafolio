# Experimentos propuestos · Contratos de señales vinculadas a finalidad

Tres ideas de investigación; **ninguna ejecutada en esta entrega**. Registro estructurado en [projects.json](../projects.json). Criterios y tolerancias se fijarán antes del test de cada prototipo; no se inventan resultados o porcentajes de mejora. Las referencias adversariales apuntan a [SECURITY_REVIEW.md](SECURITY_REVIEW.md).

## PUR-01 · Separación seguridad/underwriting

**Hipótesis falsable:** Una lista de usos explícita reduce reutilización accidental entre features de fraude y PD.

**Estimando, objetivo o invariante:**

\[
violation=1[use\notin permitted\_uses]
\]

**Diseño y comparador:** Solicitudes sintéticas de consumidores autorizados/no autorizados y políticas versionadas; comparar autorización solo por rol con rol+finalidad+referencia vigente.

**Métricas e incertidumbre:** Usos indebidos permitidos, usos legítimos bloqueados y decisiones auditables.

**Qué refuta la propuesta:** Descartar una puerta que acepte declarar una finalidad arbitraria desde el cliente sin validación del servicio consumidor.

**Revisión adversarial:** escenarios PUR-A1, PUR-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Matriz de accesos y contratos tipados para un prototipo posterior.

## PUR-02 · Linaje de una señal retirada

**Hipótesis falsable:** Bloquear el dato bruto no basta si un agregado o caché sigue exponiendo su información.

**Estimando, objetivo o invariante:**

\[
derived\_allowed(f,u)=\bigwedge_{s\in lineage(f)}allowed(s,u)
\]

**Diseño y comparador:** Grafo pequeño de variables y cachés con reglas de conservación/excepciones configuradas por institución; retirar una fuente y observar usos descendientes. Evitar afirmar que toda revocación elimina deberes legales de conservación.

**Métricas e incertidumbre:** Dependencias alcanzadas, datos derivados residuales y bloqueos incorrectos.

**Qué refuta la propuesta:** No considerar completado el control si se pierde la trazabilidad o quedan consumidores que operan sobre copias no inventariadas.

**Revisión adversarial:** escenarios PUR-A2, PUR-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Grafo de linaje de laboratorio y reporte de propagación de restricciones.

## PUR-03 · Minimización y valor de la señal

**Hipótesis falsable:** Mayor precisión o más atributos pueden aumentar fricción/exposición sin mejorar la acción.

**Estimando, objetivo o invariante:**

\[
\Delta U=U_{senal\ amplia}-U_{senal\ minima}
\]

**Diseño y comparador:** Comparar señales mínimas, región aproximada y precisión adicional sobre el mismo problema sintético; medir valor y daño definidos previamente, sin colectar ubicación real.

**Métricas e incertidumbre:** Beneficio incremental, cobertura, acceso a datos brutos y fricción por alternativa.

**Qué refuta la propuesta:** No justificar captura adicional si su utilidad desaparece bajo incertidumbre de medición o no supera la alternativa menos intrusiva.

**Revisión adversarial:** escenarios PUR-A3, PUR-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Ablación de granularidad y ficha de justificación de necesidad.

## Disciplina de evaluación

Separar desarrollo/test por el tiempo y la entidad apropiada; elegir denominadores y reglas de faltantes antes de evaluar. Guardar configuración, semilla, versión de generador, hashes y entorno. Mantener la misma población, menú, presupuesto y costos cuando se compare una política. Reportar estados desconocidos y resultados negativos. La capacidad de reproducir un ataque sintético no demuestra prevalencia ni vulnerabilidad de un proveedor real.

Si se usa un experimento anterior como baseline, citar su evidencia, conservar sus límites y medir la extensión por separado. La autorrevisión documentada no es validación independiente ni aprobación operacional.
