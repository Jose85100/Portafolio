# Contrato de MVP

**Qué es:** extensión exacta del auditor aislado a regiones factibles degeneradas
del mismo juego crediticio. Representa celdas mediante H-restricciones y V-vértices.

**Cómo corre**, desde raíz:

```bash
bash 01-economics-and-econometrics/03-game-theory/01-endogenous-credit-freeze/polyhedral-freeze-audit/reproduce.sh
```

**Qué produce:** celdas racionales JSON, dimensión exacta, comparación con solver
aislado, muestras convexas con regret exacto, oracle LP, costos, figura y notebook.

**Qué NO cubre:** solver poliédrico genérico, componentes conexas generales,
equilibrio global continuo, datos reales, estimación de selección, inferencia causal,
balances o política óptima. No convierte dimensión paramétrica en mecanismos distintos.

**Madurez:** extensión S2 del componente finito Endogenous Credit Freeze. Programa
global parcialmente S1. No declaración S3/S4 ni prioridad científica.

## Checklist de cierre

- [x] Código modular real y tipado en src/.
- [x] Comando único instala y reproduce.
- [x] Tests nuevos y regresiones pasan; cobertura medida.
- [x] Baseline previo comparado con números y rechazos explícitos.
- [x] CSV/JSON/figura y notebook ejecutado.
- [x] README, informe, referencias y MVP.
- [x] Subcarpeta original de 03-game-theory.
- [x] Madurez y reducción de alcance declaradas.

El cierre verifica existencia, resultados, hashes y salidas; no basta este checklist.
