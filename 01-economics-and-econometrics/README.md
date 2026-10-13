# Economics & Econometrics — Laboratorio de investigación económica

Economía teórica, econometría avanzada y simulación computacional con énfasis en **interacción estratégica, identificación causal y dinámica no lineal**. Los proyectos se organizan por pregunta económica, no por algoritmo.

## Cinco disciplinas

- [Macroeconomía](01-macroeconomics/) — 2 programas
- [Microeconomía](02-microeconomics/) — 2 programas
- [Teoría de juegos](03-game-theory/) — 4 programas
- [Econometría](04-econometrics/) — 2 programas
- [Macrofinanzas](05-macrofinance/) — 2 programas

**Total: 12 programas de investigación: 10 en S1 y dos con componentes en S2.** Los documentos describen hipótesis, modelos, identificación, fuentes potenciales, validación y límites. Real-Time Causal Nowcasting y Endogenous Credit Freeze incluyen ahora prototipos sintéticos ejecutables; no hay resultados empíricos de esos programas.

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
