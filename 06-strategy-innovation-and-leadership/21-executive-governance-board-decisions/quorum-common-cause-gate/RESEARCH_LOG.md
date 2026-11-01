# Research log — línea de disponibilidad del comité

## 29oct2026 — baseline acumulado, PR103
- Pregunta: ¿producto de asistencia marginal representa disponibilidad con una ausencia común?
- Evento: mínimo fijo3 y rol0presente; comitébase4 con hasta2reservas autorizadas.
- Resultado: independencia marginal0,8512frente mezcla0,76;2reservas independientes0,9dan0,9139.
- Negativos:1reserva no ayuda durante shock; peso shock0,8, meta0,97 o mínimo4 hacen inviable el menú.
- Supuesto pendiente registrado en roadmap: reservas también pueden sufrir el mismo incidente.
- Evidencia local:5tests, oracles binomial/cerrado y notebook. ComponenteS2, no programa operacional.

## 30oct2026 — relajar el supuesto pendiente
- Base inspeccionada: main0b2e582; no PRabiertos al inicio.
- Tres extensiones consideradas: (1) quórum proporcional, requiere reglas de elegibilidad distintas; (2) calidad del voto, sin datos; (3) marginales de reservas durante shock y dependencia desconocida, elegida por continuidad directa.
- Conservado: mismo evento, mínimo3, rol0, grupo principal por régimen, suite29 y móduloexact original.
- Nuevo: q1/q2condicionales durante disrupción y p11dentro de límites Fréchet; independencia del rol obligatorio frente al par sigue siendo supuesto.
- Ablations separadas: originalq0,9nominal0,9139/lower0,912; marginalesq0,7nominal0,8531; iguales marginales peor0,836; positiva perfecta0,893.
- Decisión: menú A(q0,7,costo2),B(q0,8,costo3),C(q0,9,costo4). NominaleligeA; robustoeligeBconlower0,874. Prima de protección1unidad abstracta.
- Hipótesis falsable: plan nominal barato puede fallar con un acoplamiento válido; confirmado por tabla de4estados y LP independiente.
- Negativo importante: dependencia positiva delpar mejora el eventoAND; no toda correlación empeora disponibilidad.
- Evidencia:10tests totales,100%133statements núcleo, reconstrucción exacta del29 y notebook17celdas/6code/2PNG con derivaciónLaTeX.
- Clasificación: adaptación de cota conocida al instrumento ejecutivo existente; no teoría nueva ni calibración empírica.
- Pendiente: dependencia del rol obligatorio, error de marginales y autorización real de reservas.


## 31 de octubre de2026 — Dependencia conjunta del rol y las reservas
Pregunta central: ¿qué disponibilidad puede certificarse con supuestos auditables, separada de la calidad decisional?

| Idea candidata | Brecha y relevancia | Diferencia y valor como herramienta | Viabilidad y evidencia necesaria | Decisión |
|---|---|---|---|---|
| Dependencia conjunta R/B1/B2 | La garantía30 excluía el fallo correlacionado del rol; relevante para resiliencia | LP de ocho masas y cotas conocidas que cubren esa brecha | Alta: derivación, oráculo, testigos extremos y frontera de decisión | Elegida por el pendiente explícito30 y contraste verificable |
| Marginales intervalares | Parámetros estimados con error; crítica para garantías reales | Robustez paramétrica y futura integración de datos autorizados | Técnica viable; cobertura estadística requiere muestras inexistentes | Próximo hito; no inventar intervalos calibrados |
| Quórum proporcional y elegibilidad | Mínimo fijo3 no representa necesariamente una regla real | Generalizar evento y autorización | Requiere reglas adicionales y validación del responsable | Pospuesta para preservar el contrato del mismo evento |

Mapa acumulado: causa común de principales29 → dependencia entre reservas30 → dependencia conjunta del rol31. Clasificación: adaptación de ingeniería y auditoría de supuestos, no nuevo método disciplinar. H31: ampliar el conjunto factible nunca eleva la cota y puede cambiar la decisión en la brecha; umbral de precisión1e-10 frente al LP. Negativos: meta0,85 no cambia, r=1 recupera30 y meta0,97 es inviable. El umbral adicional0,872 es un benchmark diseñado, no evidencia empírica ni ajuste oculto. Resultados y revisión en informe-2026-10-31.md.


## 1 de noviembre de2026 — Incertidumbre de las marginales

Pregunta central: certificar disponibilidad con supuestos auditables, separada de eficacia de gobierno. Se leyeron informe, código, fórmulas, notebook, negativos y roadmap31. Base `fff631e`; cero PR abiertos al inicio, ciclos anteriores integrados.

| Candidata | Brecha y relevancia | Diferencia frente a lo existente y valor | Viabilidad y evidencia necesaria | Decisión |
|---|---|---|---|---|
| Cajas marginales y del peso de shock |31 aún suponía parámetros conocidos; importa para robustez ejecutiva | Certificado condicionado a intervalos, recuperación puntual y costo de protección | Alta: derivación por monotonía, LP independiente, testigos y sensibilidad; no exige inventar datos | Elegida por pendiente explícito y cierre verificable |
| Asociación positiva restringida | Cotas amplias pueden ser conservadoras | Reducir ambigüedad de dependencia con restricciones observadas | Falta evidencia para excluir acoplamientos; riesgo de confianza falsa | Pospuesta hasta contar con restricciones justificadas |
| Quórum proporcional y elegibilidad | Evento numérico no sustituye reglas reales | Motor de reglas y validación por responsables | Requiere especificación autorizada; cambiaría el evento actual | Pospuesta para mantener comparación justa |

Mapa: causa común29 → reservas dependientes30 → rol conjunto31 → incertidumbre paramétrica01nov. Clasificación: adaptación de ingeniería y auditoría, no fórmula disciplinar original. H: un certificado puntual puede fallar con perturbaciones admisibles; la envolvente coincide con LP dentro de1e-10 y recupera puntos dentro de1e-12. Resultado: B pasa de0,870 a0,8476; C logra0,8896 al mismo umbral0,85 y cuesta una unidad adicional. Negativos: caja puntual no cambia31; certeza total da1; meta0,97 es inviable. Los intervalos son supuestos, sin afirmación de cobertura estadística. Informe y dictamen distinguen ejecución, revisión y publicación.
