# Proveedores: capacidad verificable y evaluación pendiente

Consulta pública al 23-10-2026. Cada fila resume lo declarado en una fuente del propio proveedor, **no una prueba independiente**. Los ocho candidatos cubren capas distintas; no son sustitutos completos entre sí. No se contactó a ninguno ni se enviaron datos. Referencias completas en [sources.json](sources.json).

| Candidato | Capacidad documentada / capa | Evaluación que falta para este proyecto | Fuente |
|---|---|---|---|
| iProov | Verificación de vida y comparación facial; declara defensas frente a presentación e inyección | Alcance del informe técnico, versión/SDK, ataques no vistos, rechazo genuino por dispositivo, baja luz y accesibilidad | S:iproov; S:iproov-injection |
| Truora | Validación de documento y comparación de rostro con documento | Tipos documentales por país, señales separadas de OCR/autenticidad, inyección y rutas de revisión; no asumir cobertura completa | S:truora |
| SEON | Enriquecimiento de email/teléfono/IP y señales de dispositivo mediante Fraud API | Rendimiento incremental, estabilidad del identificador, hogares compartidos y cobertura cuando faltan señales | S:seon |
| Socure | Sigma Synthetic Fraud para identidades sintéticas | Disponibilidad/cobertura del mercado objetivo, prevalencia, labels y calibración externa; verificar significado exacto del score | S:socure |
| BioCatch | Analítica conductual para fraude de apertura, ATO, estafas y mulas | SDK y consentimiento, cambios de habilidad/dispositivo, coerción genuina y aportación frente al baseline transaccional | S:biocatch |
| Feedzai | RiskOps integra señales de comportamiento/dispositivo y gestión de fraude | Módulos contratables, dependencias entre señales, exportación de razones, replay, latencia y recuperación | S:feedzai |
| Persona | Workflows con disparadores por eventos y estados de verificación | Semántica de reintentos, idempotencia, webhooks, orden de eventos y ruta si una verificación queda pendiente | S:persona |
| Belvo | Verificación/perfil de ingresos con datos financieros conectados | País/banco/producto, titularidad, completitud del histórico y clasificación de ingreso frente a transferencia/préstamo | S:belvo; S:belvo-doc |

## Compra, construcción e integración

Construir internamente el ledger, el snapshot temporal, la política económica, las métricas y la adjudicación. Evaluar compra de captura/biometría o inteligencia especializada cuando existan evidencia y cobertura suficientes. El proveedor entrega evidencia y scores; la entidad conserva la interpretación, la decisión de crédito y el control operacional. Usar APIs/SDK oficiales y contratos versionados, sin intentar reconstruir modelos propietarios.

Dos proveedores pueden depender de la misma fuente, dataset o señal de dispositivo. Contratarlos a ambos no garantiza independencia ni disponibilidad conjunta. Pedir trazabilidad de subprocesadores y dependencias materiales; probar apagados simultáneos y no solo cada endpoint aislado.

## Protocolo comparable de prueba

| Paso | Diseño requerido | Salida para decidir |
|---|---|---|
| 1. Congelar población | País, canal, documento, dispositivo, edad de cuenta y fecha definidos antes de evaluar | Cobertura y denominadores comparables |
| 2. Separar muestras | Desarrollo, calibración y test temporal; agrupar persona, dispositivo y componente de red cuando corresponda | Evitar contaminación entre particiones |
| 3. Etiquetar | Revisión adjudicada; diferenciar desconocido, identidad robada, sintética, coerción, ATO y crédito legítimo impagado | Matriz de confusión por amenaza y calidad de etiqueta |
| 4. Medir capa | Tasa de aceptación de ataques por familia y rechazo genuino; IC y número de intentos independientes | Fallos por versión y condiciones de captura |
| 5. Medir sistema | Misma capacidad y menú de acciones; pérdida neta, revisión, abandono, conversión y apelaciones | Beneficio incremental con incertidumbre |
| 6. Estresar | Timeouts, duplicados, respuestas tarde, firma inválida, caída compartida y nuevo modelo remoto | Ruta factible y auditada sin convertir error en aprobado |
| 7. Decidir | Umbrales de daño/fricción/costo acordados antes del test; después sombra y piloto acotado | Acta de aceptación o descarte y rollback |

Si no aparecen falsos negativos en `n` ataques independientes, el límite superior unilateral exacto al 95% para la tasa de aceptación de ataques es `1 - 0.05**(1/n)`; con 300, aproximadamente 0,994%. Repetir 300 veces el mismo video no equivale a 300 ataques independientes. Estratificar por familia y proveedor: un promedio oculta huecos graves.

## Preguntas de diligencia que no resuelve una demo

- ¿Qué score se devuelve, para qué población, bajo qué versión y qué eventos cambian su semántica? ¿Hay evidencia bruta y reason codes exportables?
- ¿Qué evidencia de laboratorio cubre presentación, inyección y medios manipulados por separado? ¿Qué falsos negativos y genuinos se midieron? No confundir ranking de comparación facial con seguridad de extremo a extremo.
- ¿Dónde se procesan biometría/PII, con qué subprocesadores y retención? ¿Cómo se atienden eliminación, apelaciones y una alternativa accesible? Confirmación con las áreas responsables del país.
- ¿Qué SLA, distribución de latencia, límites, idempotencia y costos por intento/reintento/revisión están pactados? No hay precios públicos contrastados en esta entrega.
- ¿Se puede congelar una versión, detectar cambios y reproducir una decisión histórica? ¿Qué pasa con webhooks tardíos después del desembolso?
- ¿La fuente financiera representa ingreso recurrente verificable o movimientos de dinero? ¿Qué porcentaje de la población queda sin cobertura?
