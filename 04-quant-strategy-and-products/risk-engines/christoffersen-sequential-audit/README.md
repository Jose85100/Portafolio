# Auditoría secuencial de Christoffersen

MVP C++17 que compara Monte Carlo fijo (999 réplicas) con una decisión secuencial
ternaria para el test de independencia de Christoffersen. La política solo rechaza o
no rechaza cuando un intervalo de Hoeffding con gasto de error queda completamente a
un lado de `alpha=5%`; en otro caso devuelve `undecided`.

## Reproducción en un comando

```bash
bash run.sh
```

El comando crea el entorno, compila, ejecuta CTest, ASan/UBSan, cobertura, benchmark,
`ruff` y `mypy`. Produce `results/run.json`, `results/trials.csv`,
`results/summary.csv`, `results/performance.json` y `results/sequential-audit.png`.

Requisitos del host: Python 3.10+ y `g++`. Alternativa aislada:
`docker build -t sequential-audit . && docker run --rm sequential-audit`.

## Configuración

- Serie sintética condicional: 30 días, exactamente 4 excepciones; se enumeran los
  27.405 ordenamientos posibles para obtener la verdad de referencia.
- Semillas: 1..200 por escenario.
- Baseline: p-value corregido `(b+1)/(B+1)`, `B=999`.
- Secuencial: looks geométricos 256..65.536, `delta=1%` total.
- Escenarios: p exacto próximo a 0,1%, 5% y 50%.

La garantía es sobre el riesgo de una decisión secuencial incorrecta bajo muestras
Bernoulli independientes; `undecided` no se contabiliza como acierto ni como error.
