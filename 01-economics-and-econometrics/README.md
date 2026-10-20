# Economics & Econometrics — Laboratorio de investigación económica

Economía teórica, econometría avanzada y simulación computacional con énfasis en **interacción estratégica, identificación causal y dinámica no lineal**. Los proyectos se organizan por pregunta económica, no por algoritmo.

## Cinco disciplinas

- [Macroeconomía](01-macroeconomics/) — 2 programas
- [Microeconomía](02-microeconomics/) — 2 programas
- [Teoría de juegos](03-game-theory/) — 4 programas
- [Econometría](04-econometrics/) — 2 programas
- [Macrofinanzas](05-macrofinance/) — 2 programas

**Total: 12 programas de investigación: nueve en S1 y tres con componentes en S2.** Los documentos describen hipótesis, modelos, identificación, fuentes potenciales, validación y límites. Real-Time Causal Nowcasting, Endogenous Credit Freeze y Sovereign–Bank Strategic Nexus incluyen prototipos sintéticos ejecutables; no hay resultados empíricos de esos programas. Los componentes dinámicos/empíricos no implementados siguen S1.

## Infraestructura compartida

- [Computational Economics](computational-economics/) — arquitectura de juegos bayesianos, juegos estocásticos, juegos de campo medio, mecanismos, solvers y estimación estructural.
- [Research Standards](RESEARCH_STANDARDS.md) — madurez S0–S4, replicabilidad, falsación y gobierno científico.

## Prioridad inicial

1. **Endogenous Credit Freeze:** juego global, umbrales y contrafactuales de liquidez.
2. **Algorithmic Market Equilibria:** aprendizaje multiagente y pruebas de desviación.
3. **Strategic Monetary Transmission:** equilibrio dinámico, heterogeneidad y shocks identificados.
4. **Real-Time Causal Nowcasting:** datos vintage, evaluación pseudo-real-time y sesgo de revisión.
5. **Mechanism Design for Financial Inclusion:** contratos IC/IR, selección y bienestar.

## Regla de originalidad

La originalidad debe establecerse frente a la literatura existente. Cada programa requiere una revisión sistemática antes de afirmar contribuciones inéditas. Se distingue explícitamente teoría, simulación y evidencia observacional.

Véase [arquitectura general](../RESEARCH_ARCHITECTURE.md).


## Laboratorios reproducibles — expansión

Se incorporan **35 proyectos adicionales** (siete por área) con 35 notebooks de Python, README con ecuaciones, diseños de identificación y validación; y siete módulos de economía computacional con un núcleo común de utilidades y pruebas unitarias. El alcance computacional inicial es un baseline estadístico sintético, **no** 35 estimadores estructurales completos ni experimentos con datos reales.

- [Macroeconomía](01-macroeconomics/ADDITIONAL_RESEARCH_LABS.md)
- [Microeconomía](02-microeconomics/ADDITIONAL_RESEARCH_LABS.md)
- [Teoría de juegos](03-game-theory/ADDITIONAL_RESEARCH_LABS.md)
- [Econometría](04-econometrics/ADDITIONAL_RESEARCH_LABS.md)
- [Macrofinanzas](05-macrofinance/ADDITIONAL_RESEARCH_LABS.md)
- [Economía computacional](computational-economics/)

### Ejecución de tests
```bash
python3 -m unittest discover -s 01-economics-and-econometrics/computational-economics/tests -v
```

## Ciclo diario 2026-10-12

[Vintage Audit](04-econometrics/01-real-time-causal-nowcasting/vintage-audit/): auditor as-of, benchmark factorial y tests; componente S2, modelo causal completo S1.

## Ciclo diario 2026-10-13

[Bayesian Freeze Audit](03-game-theory/01-endogenous-credit-freeze/bayesian-freeze-audit/): enumeración finita de BNE, oracle racional, selección y tests; componente S2, modelo global completo S1.

## Ciclo diario 2026-10-14

[Mixed Freeze Audit](03-game-theory/01-endogenous-credit-freeze/mixed-equilibrium-audit/):
extensión S2 del juego finito a equilibrios mixtos aislados, con regret, oráculo
racional, controles de degeneración y comparación con el baseline puro.

## Ciclo diario 2026-10-15

[Polyhedral Freeze Audit](03-game-theory/01-endogenous-credit-freeze/polyhedral-freeze-audit/):
extensión S2 a familias degeneradas del juego finito, con regiones racionales,
dimensión afín, oracle LP y regresiones de los MVP anteriores.

## Ciclo diario 2026-10-16

[Strategic Form Audit](03-game-theory/01-endogenous-credit-freeze/strategic-form-audit/):
exportación estratégica racional y contraste ejecutado con Nashpy externo; diagnóstico
de degeneración y control negativo del regret ex ante en tipos raros. Componente S2,
Endogenous Credit Freeze sigue S2 parcial; no hay nueva validación empírica.

## Ciclo diario 2026-10-17

[Rational Family Audit](03-game-theory/01-endogenous-credit-freeze/rational-family-audit/):
parser y solver racional Gambit ejecutados, reconstrucción local de familias por
compatibilidad y comparación exacta con los poliedros del repo. Extensión S2 del
componente finito, sin elevar el programa completo a S3.

## Ciclo diario 2026-10-18

[Sovereign Clearing Audit](05-macrofinance/01-sovereign-bank-strategic-nexus/sovereign-clearing-audit/):
componente estático S1→S2 del programa soberano-bancario, con dos cotas, LP, oráculo
racional, regresión contra el notebook semanal y separación de impagos brutos de
pérdidas a acreedores externos. Programa S2 parcial; doom loop dinámico sigue S1.


## Profundización metodológica — octubre de 2026

La auditoría detectó README breves en varios laboratorios frente al volumen de notebooks existentes. Se inició una refactorización por **mecanismo económico e identificación**, no por longitud artificial: [guía de métodos y núcleo OLS/IV](research-methods/), [multiplicadores fiscales](01-macroeconomics/04-fiscal-multipliers-local-projections/) y [elasticidad de crédito](02-microeconomics/03-consumer-credit-demand-elasticity/). Los ejemplos siguen siendo sintéticos. El resto de proyectos requiere una revisión individual antes de declarar cerrada la brecha documental y científica.

## Ciclo diario 2026-10-19

[Fire-Sale Price Audit](05-macrofinance/01-sovereign-bank-strategic-nexus/fire-sale-price-audit/):
extensión S2 del mercado de un activo con precio endógeno, enumeración por
regímenes, estabilidad de Picard y contraejemplos a unicidad por convergencia.
No acopla todavía pagos interbancarios/precios ni implementa feedback fiscal.
Sovereign–Bank Strategic Nexus permanece S2 parcial; inventario9 S1+3 S2 parciales.

## Ciclo diario 2026-10-20

[Coupled Clearing Audit](05-macrofinance/01-sovereign-bank-strategic-nexus/coupled-clearing-audit/):
extensión S2 que acopla pagos interbancarios y precio de liquidación de un activo
para1–4 bancos. Enumera regímenes y muestra cuándo congelar cobros nominales
produce balances no factibles. Programa S2 parcial; no evidencia empírica ni
promoción a S3. Conserva las regresiones de los componentes anteriores.
