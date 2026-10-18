# Financial and Construction Risk Lab

**Inventario actual:** 45 carpetas de proyecto preservadas (10 corporativas, 21 de construcción, 14 de investigación). Hay temas solapados y numeración histórica repetida; no representan 45 modelos distintos implementados. Véase [inventario verificable](PROJECT_INVENTORY.csv).

## Domains
1. Corporate financial risk: liquidity, rates/FX, refinancing, ALM, CVA.
2. Construction enterprise risk: project cashflows, schedule/cost, presales, counterparties, project finance, materials inflation, inventory, permits, concentration, safety, climate.
3. Research in progress: digital twin, systemic stress, Bayesian early warning, causal delays, robust capital allocation, network contagion.

## Executable baselines
Python: cashflow Monte Carlo; VaR/ES; DSCR/LLCR; critical path and schedule simulation; one-factor credit portfolio losses.
C++17: deterministic cashflow, liquidity shortfall, empirical VaR/ES. See [model catalog](MODEL_CATALOG.md) for execution and maturity details.

All numerical outputs require independent calibration, validation, stress testing and governance before business use. Synthetic examples are not empirical evidence.


## Experimentos y revisión técnica

El [notebook ejecutado](notebook.ipynb) conecta caja, ruta crítica, DSCR/LLCR y dependencia de pérdidas. El [catálogo](MODEL_CATALOG.md) diferencia la implementación compartida y el alcance completo de cada diseño.

### Cambio de contrato de cola
Python y C++ usan VaR de rango más cercano e integran exactamente masa 1−α para ES. Para pérdidas [1,2,3,4,5] y α=0.8, ES ahora es 5; el antiguo promedio desde el rango VaR devolvía 4.5 y representaba otra convención. Las [100 fixtures](tests/fixtures/tail_contract.csv) tienen referencia racional hinge y se comparten entre Python, C++ y mercado-liquidez. Los checks C++ permanecen activos en Release.

Se rechazan entradas no finitas en caja, cronograma, deuda y colas; un período sin servicio de deuda conserva DSCR indefinido (`None`). El cero de caja y el piso de liquidez son fronteras explícitas, no defaults regulatorios.
