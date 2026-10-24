# Experimentos propuestos · Contexto geográfico y dispositivo bajo incertidumbre

Tres ideas de investigación; **ninguna ejecutada en esta entrega**. Registro estructurado en [projects.json](../projects.json). Criterios y tolerancias se fijarán antes del test de cada prototipo; no se inventan resultados o porcentajes de mejora. Las referencias adversariales apuntan a [SECURITY_REVIEW.md](SECURITY_REVIEW.md).

## GEO-01 · Radios frente a distancia ingenua

**Hipótesis falsable:** Incorporar precisión reduce alertas espurias en traslados legítimos sin borrar discrepancias grandes.

**Estimando, objetivo o invariante:**

\[
\Delta FPR=FPR_{centros}-FPR_{radios}
\]

**Diseño y comparador:** Generar trayectorias legítimas y eventos incompatibles en un plano/geodesia conocido; variar error, método, radio y muestreo. Comparar a igual presupuesto de verificación, conservando familias de trayectorias fuera de desarrollo.

**Métricas e incertidumbre:** Falsas alertas, poder por tipo de discrepancia, abstención y costo por caso; bootstrap por trayectoria.

**Qué refuta la propuesta:** Descartar si la mejora desaparece al mismo presupuesto o si la regla solo se beneficia de radios artificialmente correctos.

**Revisión adversarial:** escenarios GEO-A1, GEO-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Notebook futuro con generador, curvas de error y contraejemplos de radios mal especificados.

## GEO-02 · Antigüedad y cambio de método

**Hipótesis falsable:** Mezclar ubicaciones viejas o métodos heterogéneos puede explicar una discrepancia antes que un desplazamiento real.

**Estimando, objetivo o invariante:**

\[
age=t_{cutoff}-t_{medicion}
\]

**Diseño y comparador:** Factorial de antigüedad, cambio IP/API y fuente actualizada. Fijar un criterio de vigencia por finalidad antes de test; introducir retrasos de disponibilidad y comparar con regla sin caducidad.

**Métricas e incertidumbre:** Errores por cohorte de edad/método, fracción comparable y volumen de nueva evidencia requerida.

**Qué refuta la propuesta:** No promover la regla si necesita un umbral elegido con el test o trata un radio desconocido como cero.

**Revisión adversarial:** escenarios GEO-A2, GEO-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Tabla de estados y benchmark de caducidad con timestamps sintéticos.

## GEO-03 · Dispositivo compartido y restablecido

**Hipótesis falsable:** Un modelo de continuidad explícita evita atribuir a una misma persona todos los eventos de un equipo.

**Estimando, objetivo o invariante:**

\[
N_e(t)=\sum_j1[e\in caso_j,\ event_j<t,\ available_j\le t]
\]

**Diseño y comparador:** Simular hogares, oficinas, equipos restablecidos y granjas controladas; deduplicar solicitudes. Comparar IP sola, instalación sola y combinación con tipos de red, con partición por componente y tiempo.

**Métricas e incertidumbre:** Falsos vínculos, vínculos perdidos, carga de revisión y efecto incremental de cada señal.

**Qué refuta la propuesta:** Descartar continuidad como identidad si pequeños resets o redes compartidas producen asociaciones masivas equivocadas.

**Revisión adversarial:** escenarios GEO-A3, GEO-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Corpus de eventos y evaluación de vinculación; sin rastreo de personas reales.

## Disciplina de evaluación

Separar desarrollo/test por el tiempo y la entidad apropiada; elegir denominadores y reglas de faltantes antes de evaluar. Guardar configuración, semilla, versión de generador, hashes y entorno. Mantener la misma población, menú, presupuesto y costos cuando se compare una política. Reportar estados desconocidos y resultados negativos. La capacidad de reproducir un ataque sintético no demuestra prevalencia ni vulnerabilidad de un proveedor real.

Si se usa un experimento anterior como baseline, citar su evidencia, conservar sus límites y medir la extensión por separado. La autorrevisión documentada no es validación independiente ni aprobación operacional.
