# Riesgo de mercado y liquidez: laboratorio avanzado

Programa de investigación aplicada con seis estudios de modelación, una implementación Python reproducible y pruebas de invariantes. Los estudios de modelación siguen siendo **simulaciones didácticas**, no calibraciones ni requerimientos regulatorios. La [edición complementaria del IRL oficial de la SFC](03-liquidez-estocastica/observed-sfc-irl/) aporta un indicador prudencial observado; el [HHI por categorías de tenedores TES](04-espirales-de-liquidez/observed-tes-holder-concentration/) describe concentración agregada. Ninguna de las dos fuentes observa eventos de primera ruptura, ventas sincronizadas o impacto de precio para validar los modelos dinámicos. La gestión de liquidez depende de moneda, horizonte, entidad, acceso a financiación, balance, mercado y reglas prudenciales aplicables.

La edición observada conserva un snapshot mensual SFC por entidad con corte dic-2022 y un anexo discontinuo por tipo para ago-2025, jul-2026 y ago-2026, con fórmula, hashes, reporte, figura, conciliación y límites. Mide ratios de cobertura de liquidez a 30 días frente al mínimo de 100%, no probabilidad de iliquidez ni shortfall de caja realizado.

## Módulos

1. [Expected Shortfall dinámico, FHS y teoría de valores extremos](01-expected-shortfall-dinamico/)
2. [Volatilidad de cambios de régimen y riesgo de transición](02-regimenes-de-volatilidad/)
3. [Liquidez estocástica y tiempo hasta agotamiento](03-liquidez-estocastica/)
4. [Espirales de liquidez, margin calls y fire sales](04-espirales-de-liquidez/)
5. [Optimización CVaR con costos de liquidación](05-optimizacion-de-liquidez/)
6. [Stress testing integrado de mercado y liquidez](06-estres-integrado/)

## Ejecución

```bash
python3 03-financial-risk/03-market-liquidity-research/laboratorio-integrado/python/laboratorio.py
python3 -m unittest discover -s 03-financial-risk/03-market-liquidity-research/laboratorio-integrado/tests -p 'test_*.py' -v
```

Requiere NumPy. Cada simulación fija una semilla para reproducibilidad. Las fórmulas y resultados son hipótesis/modelos, no validación de riesgo real. Las referencias conceptuales incluyen Basel Committee (marcos de riesgo de mercado y liquidez), FRTB/Expected Shortfall, BCBS LCR/NSFR, literatura EVT, GARCH, modelos de fire sales y optimización CVaR; deben verificarse vigencia y aplicación local antes de citar como obligación regulatoria.

## Diseño de validación

Comparar contra baselines, registrar supuestos, hacer validación temporal, stress out-of-distribution, sensibilidad a parámetros, error Monte Carlo y coherencia de unidades. Separar riesgo de liquidez de financiación (cash-flow shortfall) de liquidez de mercado (impacto y profundidad). Una simulación controlada permite estudiar propiedades numéricas; el desempeño predictivo requiere evaluación con datos pertinentes y separación temporal.


## Experimentos ejecutados y contrato numérico

El [notebook](laboratorio-integrado/notebook.ipynb) separa pérdidas de mercado, déficit de financiación y costo económico de financiar ese déficit. Incluye reserva inicial, primera ruptura censurada, sensibilidad de ES y una ablación de dependencia por permutación.

VaR usa ahora la inversa generalizada empírica (sin interpolar entre átomos); ES conserva masa de cola exactamente 1−α. La convención se contrasta con las mismas fixtures racionales de construcción. La acumulación de caja rechaza overflow y los conteos de escenarios/horizonte deben ser enteros explícitos.
