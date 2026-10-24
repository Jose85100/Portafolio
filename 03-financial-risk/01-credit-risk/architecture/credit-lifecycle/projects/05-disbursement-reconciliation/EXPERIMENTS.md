# Experimentos propuestos · Desembolso idempotente y conciliación de efectos

Tres ideas de investigación; **ninguna ejecutada en esta entrega**. Registro estructurado en [projects.json](../projects.json). Criterios y tolerancias se fijarán antes del test de cada prototipo; no se inventan resultados o porcentajes de mejora. Las referencias adversariales apuntan a [SECURITY_REVIEW.md](SECURITY_REVIEW.md).

## PAY-01 · Timeout después de liquidación

**Hipótesis falsable:** Consultar la misma operación antes de reenviar reduce dobles efectos frente a reintentar como operación nueva.

**Estimando, objetivo o invariante:**

\[
double\_rate=operaciones\ con\ mas\ de\ un\ settled/operaciones
\]

**Diseño y comparador:** Emular aceptado, liquidado, respuesta perdida, callback duplicado y rechazo definitivo; comparar políticas sobre los mismos eventos y enumerar secuencias pequeñas.

**Métricas e incertidumbre:** Dobles efectos, pendientes por edad, consultas y tiempo hasta estado conciliado.

**Qué refuta la propuesta:** Cualquier doble liquidación admisible descarta la política; cero en un corpus no demuestra seguridad universal.

**Revisión adversarial:** escenarios PAY-A1, PAY-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Emulador futuro de riel y un oráculo de estado por intención.

## PAY-02 · Reserva y liberación coherentes

**Hipótesis falsable:** Liberar por timeout puede permitir que otro préstamo consuma un cupo ya usado por un pago liquidado.

**Estimando, objetivo o invariante:**

\[
reservation\_release\Rightarrow known\_terminal\_state\land applicable\_rule
\]

**Diseño y comparador:** Intercalar reserva, pago desconocido, segunda solicitud, confirmación tardía y devolución. Las reglas de retorno/corrección se mantienen separadas del primer efecto.

**Métricas e incertidumbre:** Exposición sobreasignada, reservas huérfanas y conciliación de saldo/reserva.

**Qué refuta la propuesta:** Descartar si una confirmación tardía deja exposición por encima del límite debido a una liberación previa.

**Revisión adversarial:** escenarios PAY-A2, PAY-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Modelo de referencia de reservas e intercalados adversariales.

## PAY-03 · Conciliación por referencia y valor

**Hipótesis falsable:** Conciliar solo por total agregado puede ocultar errores compensados entre operaciones.

**Estimando, objetivo o invariante:**

\[
\Delta_k=ledger_k-settlement_k
\]

**Diseño y comparador:** Inyectar duplicación, ausencia, referencia cruzada, moneda incorrecta y dos errores de signos opuestos. Comparar agregado, referencia y referencia+moneda+valor.

**Métricas e incertidumbre:** Errores ocultos, falsas discrepancias, partidas pendientes y tiempo de resolución.

**Qué refuta la propuesta:** No aceptar el agregado como evidencia suficiente si detecta total cero con partidas equivocadas.

**Revisión adversarial:** escenarios PAY-A3, PAY-A4. El experimento registra el control vulnerado/alcance de evidencia y exige un estado seguro y auditable; sin resultados observados todavía.

**Artefacto para pasar a prototipo:** Corpus conciliable y reporte de diferencias por operación, sin dinero real.

## Disciplina de evaluación

Separar desarrollo/test por el tiempo y la entidad apropiada; elegir denominadores y reglas de faltantes antes de evaluar. Guardar configuración, semilla, versión de generador, hashes y entorno. Mantener la misma población, menú, presupuesto y costos cuando se compare una política. Reportar estados desconocidos y resultados negativos. La capacidad de reproducir un ataque sintético no demuestra prevalencia ni vulnerabilidad de un proveedor real.

Si se usa un experimento anterior como baseline, citar su evidencia, conservar sus límites y medir la extensión por separado. La autorrevisión documentada no es validación independiente ni aprobación operacional.
