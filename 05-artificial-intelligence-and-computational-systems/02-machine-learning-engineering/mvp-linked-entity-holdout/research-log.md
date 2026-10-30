# Research log acumulativo

- 2026-10-29 / PR102: cero cortes transitivos en corpus de grupos iguales. Negativo reconocido: no mide masas desiguales, ni calidad de links ni tiempo. No alterar esas salidas históricas.
- 2026-10-30: se comparan3 extensiones en config_balancing.json. Elegida masa desigual porque deriva directamente del negativo29 y permite oracle exhaustivo sin dataset inventado.
- Hipótesis previa: DP no empeora desviación respecto baseline factible y conserva0 cortes. Umbral:25/25 no inferiores y0 cortes.
- Ejecución: resultados reales en results/balancing30;20 mejoras,5 empates,0 empeoramientos. Negativo: grupo30/33 deja13.5 filas de desviación aun con óptimo. Más coste del DP; escalabilidad solo medida hasta60 grupos/291filas.
- Decisión: continuar investigación de fixtures desiguales; ajustar política si tolerancia de desviación insuficiente; cerrar uso si única componente o vínculos futuros/no fiables. No producción.
- Siguiente revisión: validar links y temporalidad, sin prometer mejora AUC ni seleccionar split según rendimiento test.
