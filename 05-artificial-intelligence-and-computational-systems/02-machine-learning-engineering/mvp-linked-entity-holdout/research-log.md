# Research log acumulativo

- 2026-10-29 / PR102: cero cortes transitivos en corpus de grupos iguales. Negativo reconocido: no mide masas desiguales, ni calidad de links ni tiempo. No alterar esas salidas históricas.
- 2026-10-30: se comparan3 extensiones en config_balancing.json. Elegida masa desigual porque deriva directamente del negativo29 y permite oracle exhaustivo sin dataset inventado.
- Hipótesis previa: DP no empeora desviación respecto baseline factible y conserva0 cortes. Umbral:25/25 no inferiores y0 cortes.
- Ejecución: resultados reales en results/balancing30;20 mejoras,5 empates,0 empeoramientos. Negativo: grupo30/33 deja13.5 filas de desviación aun con óptimo. Más coste del DP; escalabilidad solo medida hasta60 grupos/291filas.
- Decisión: continuar investigación de fixtures desiguales; ajustar política si tolerancia de desviación insuficiente; cerrar uso si única componente o vínculos futuros/no fiables. No producción.
- Siguiente revisión: validar links y temporalidad, sin prometer mejora AUC ni seleccionar split según rendimiento test.

## 2026-10-31 — hipótesis de garantía fuerte refutada

Pregunta persistente: ¿qué se requiere para un holdout de identidades útil y auditable?29 clausura,30 balance,31 calidad del grafo. Tres candidatas: (A) auditoría observada/adjudicada, brecha explícita30, alta relevancia y herramienta directa, viabilidad con verdad sintética y oráculo de pares; (B) vínculos temporales, alta relevancia pero falta contrato de disponibilidad y fuente adjudicada, requiere evidencia de fechas; (C) DP memoria eficiente, útil a escala pero no corrige garantía engañosa de cero cortes y ya existen algoritmos competitivos, requiere comparación de costes. Se selecciona A: cierra el negativo30 sin inventar un mecanismo nuevo. Se posponen B/C por evidencia/valor relativo, no por superioridad universal.

H31 tipo refutación: basta un caso C_O=0 y C_T>0 para negar suficiencia universal. Umbral fijado en config antes de interpretación. Resultado: contraejemplo4 filas;144 registros del diseño. Mixto balancea exactamente y expone28 filas; conservar negativo, no adaptar parámetros. Mapa: splitter29→balancing30→graph_audit31, sin duplicación de motores. Se sabe ahora separar error del grafo y del split; no se sabe prevalencia ni efecto predictivo real. Mantener validez condicional, no ascender madurez del dominio. Auditoría/adaptación, no extensión científica acreditada.

## 2026-11-01 — completar auditoría parcial sin imputar verdad

Pregunta central persistente: independencia útil y verificable del holdout de identidades. Negativo31: sin adjudicación completa el auditor se abstiene por error, y0 cortes observados no implica0 exposición real. Candidatas comparadas por seis criterios en prior_art1101.md: parcial (elegida), temporal (falta contrato/fuente), DP eficiente (menor prioridad de significado científico).

Mapa acumulativo: components29→balance30→audit_graph31→partial_audit1101. Se conserva auditor31; derivación local de extremos de filas expuestas, no cambio arbitrario de fórmula ni identidad inferida. Hipótesis técnica predefinida en config:5508 configuraciones exhaustivas coinciden con min/max de oráculo;480 escenarios contienen verdad suministrada; caso completo recupera31. Se cumple. Error inicial del literal que contaba configuraciones (5712) corregido al conteo generado5508, no fallo de extremos ni cambio de hipótesis matemática; log final conserva ejecución real.

Resultado positivo: a75% train-first anchura media15.625 vs21.395833 segura,36/48 estrictamente más estrechas. Negativos: shuffled50% no mejora anchura24, train-first50%48/48 abstenciones; adjudicación errónea puede dar[0,0] frente exposición real2, fuera del contrato. No datos reales ni intervalos inferenciales. Clasificación adaptación de ingeniería/auditoría con derivación combinatoria local, originalidad científica no acreditada. Ahora aprovechamos información parcial y cuantificamos lo que falta; no sabemos fiabilidad real de adjudicación/fechas ni impacto predictivo.
