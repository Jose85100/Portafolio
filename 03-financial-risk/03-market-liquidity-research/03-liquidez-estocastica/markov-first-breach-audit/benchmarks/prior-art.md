# Selección de aporte y revisión focal — 27 de octubre de 2026

| Idea | Ventaja | Límite para este ciclo |
|---|---|---|
| Referencia adaptativa de integración de factor común | Continúa la falsación de rho alto del ciclo26 | Dependería del PR87, todavía abierto; no se supone integrado |
| Cota de cuantización de pesos de crédito | Complementa el DP25 | Mantiene el foco reciente en crédito y requiere separar error de VaR en átomos |
| Primer agotamiento de caja con regímenes persistentes | Rota a liquidez, admite oráculo exhaustivo y evidencia pequeña | Se selecciona un modelo discreto sintético, no calibración operacional |

Se inspeccionaron main e0cb173, README de liquidez, laboratorio Python y risk.hpp. El motor C++ ya detecta primera ruptura de cada trayectoria correctamente: este trabajo NO corrige un supuesto bug de ese motor. Añade un oráculo probabilístico finito con persistencia de régimen, comparación de marginales idénticos y reserva mínima. La comparación terminal es una ablación deliberadamente insuficiente, no una atribución de ese error al código existente.

Fuentes primarias verificadas27oct: página Dartmouth de Grinstead/Snell (capítulos Markov/random walk); Springer de Asmussen (metadatos y contenido, no libro completo); arXiv Ivanovs (primera pasada/extremos de procesos aditivos); página del autor Brunnermeier en Princeton (funding vs market liquidity); BIS bcbs144 (principios2008). NBER12939 dio403 al abrir y se sustituyó por la página del autor. Cinco entradas reales en referencias.bib; revisión focal, no exhaustiva.

Grinstead/Snell y Asmussen sustentan cadenas/absorción; Ivanovs ofrece un marco más amplio, no replicamos sus factorizaciones. Brunnermeier/Pedersen estudian interacción endógena, ausente en este MVP. BIS es contexto conceptual y NO se utiliza para inferir requerimientos actuales de Colombia, LCR, NSFR o reservas normativas. No se reivindica nueva teoría ni se inventan resultados de literatura.
