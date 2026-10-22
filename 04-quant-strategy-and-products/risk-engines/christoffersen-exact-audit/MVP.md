# MVP

## Qué es

Un oracle C++17 por enumeración completa para el p-valor condicional del estadístico de independencia de
Christoffersen, comparado numéricamente con un estimador Monte Carlo reproducible.

## Cómo se corre

`./run.sh`

## Qué produce

Binarios compilados, tests, sanitizers, cobertura, JSON crudo, métricas de tiempo/memoria y figura PNG.

## Qué no cubre

Muestras regulatorias grandes, riesgo de estimación del VaR, cobertura incondicional, Expected Shortfall, datos
reales o certificación de cumplimiento. La enumeración crece combinatoriamente y se rechaza sobre el presupuesto.
