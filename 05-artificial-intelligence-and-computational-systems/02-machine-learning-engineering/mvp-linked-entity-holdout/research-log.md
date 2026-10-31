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
