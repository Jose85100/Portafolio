# Contrato del MVP

## Qué es

Solver analítico por candidatos para una decisión estática de venta y préstamo colateralizado de un banco.

## Cómo correr

`bash 01-economics-and-econometrics/05-macrofinance/01-sovereign-bank-strategic-nexus/collateral-liquidity-choice/reproduce.sh`

## Qué produce

Elección, baseline de liquidación, oráculo de malla, sensibilidad, estabilidad, benchmark, CSV/JSON, PNG y notebook ejecutado.

## Qué no cubre

Red interbancaria, default, colateral múltiple, haircut endógeno, estrategia del prestamista, garantías públicas, equilibrio Nash, política óptima, bienestar, datos reales o causalidad.

## Checklist

- [x] Código modular en `src/`.
- [x] Un comando documentado.
- [x] Tests automatizados.
- [x] Baselines numéricos.
- [x] Salidas CSV/JSON/figura.
- [x] README, informe, referencias y MVP.
- [x] Subcarpeta `05-macrofinance` coherente.
- [x] S2 del componente declarado sin inflar el programa.
