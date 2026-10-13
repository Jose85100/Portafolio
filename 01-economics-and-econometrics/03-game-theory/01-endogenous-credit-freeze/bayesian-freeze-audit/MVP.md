# Contrato de MVP

**Qué es:** auditor de completitud y selección de equilibrio puro en un juego bayesiano
finito de renovación crediticia con complementariedad.

**Cómo corre:** desde raíz, `bash 01-economics-and-econometrics/03-game-theory/01-endogenous-credit-freeze/bayesian-freeze-audit/reproduce.sh`.

**Qué produce:** conjuntos de equilibrios, regret, crédito promedio, payoff de prestamistas,
límites de P(ningún prestamista renueva | fundamental bueno), matriz de sensibilidad,
oracle racional, costos, figura, notebook ejecutado y tests.

**Qué NO cubre:** tipos continuos, equilibrios mixtos, continuum de agentes, elección de
equilibrio estimada, dinámica macroeconómica, datos reales, causalidad ni política óptima.

**Madurez:** componente finito S1 → S2. Programa global completo sigue parcialmente S1.
No se afirma S3/S4 ni prioridad científica.

## Checklist de cierre

- [x] Código ejecutable real en src/.
- [x] Comando único de instalación/reproducción.
- [x] Tests pasando, con cobertura medida.
- [x] Baseline del repo con números.
- [x] CSV/JSON/figura verificados.
- [x] README, informe, referencias y MVP.
- [x] Carpeta del programa original en 03-game-theory.
- [x] Madurez y reducción de alcance explícitas.
