# Selección y revisión focal — 28 de octubre de 2026

| Idea | Valor | Decisión |
|---|---|---|
| Cuadratura adaptativa de factor de crédito | Responde al fallo numérico26 | Más dependencia y tiempo; se pospone |
| Línea de crédito y política contingente de caja | Modela fondeo operativo | Requiere coste/capacidad y una política, excede MVP pequeño |
| Intervalos de transición de liquidez | Cierra un límite explícito27 | Seleccionada: Bellman pequeño y oráculo nominal ya auditado |

Se inspeccionó main5b7d30e, PR abiertos[] al inicio, README de liquidez y contratoMVP27. Se reutiliza el forwardDP27 sin editarlo y se registra SHA256. No se modifica motorC++ ni archivos globales. El nuevo alcance es incertidumbre de matriz, no repetir el experimento de persistencia con matriz conocida.

Cinco fuentes primarias abiertas28oct: Iyengar2005INFORMS (rectangularidad); Nilim/ElGhaoui2005páginaautorBerkeley (recursiónrobusta); Wiesemann/Kuhn/Rustem2013Imperial (incertidumbre de parámetros); Grinstead/SnellDartmouth (cadenas); BCBS2008BIS (contexto de liquidez). Se verificaron metadatos y resúmenes, no se afirma revisión exhaustiva o lectura completa de libros/artículos cerrados.

La rectangularidad permite a naturaleza escoger por tiempo/caja/régimen. NO equivale automáticamente a una única matriz fija desconocida. No implementamos las regiones de confianza o programas cónicos de Wiesemann. Nuestros intervalos son stress hipotético y NO tienen cobertura estadística. BCBS es contexto2008, sin inferencia de obligaciónLCR/NSFR/SFC actual. Novedad incremental local, no teoría nueva.
