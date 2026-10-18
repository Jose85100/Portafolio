# Riesgo de mercado y liquidez: laboratorio avanzado

Programa de investigación aplicada con seis estudios de modelación, una implementación Python reproducible y pruebas de invariantes. Los resultados son **simulaciones didácticas**, no calibraciones ni requerimientos regulatorios. La gestión de liquidez depende de moneda, horizonte, entidad, acceso a financiación, balance, mercado y reglas prudenciales aplicables.

## Módulos

1. [Expected Shortfall dinámico, FHS y teoría de valores extremos](01_ES_DINAMICO_EVT.md)
2. [Volatilidad de cambios de régimen y riesgo de transición](02_REGIMENES_VOLATILIDAD.md)
3. [Liquidez estocástica y tiempo hasta agotamiento](03_LIQUIDEZ_ESTOCASTICA.md)
4. [Espirales de liquidez, margin calls y fire sales](04_ESPIRALES_LIQUIDEZ.md)
5. [Optimización CVaR con costos de liquidación](05_OPTIMIZACION_LIQUIDEZ.md)
6. [Stress testing integrado de mercado y liquidez](06_STRESS_INTEGRADO.md)

## Ejecución

```bash
python3 03-financial-risk/03-market-liquidity-research/python/laboratorio.py
python3 -m unittest discover -s 03-financial-risk/03-market-liquidity-research/tests -p 'test_*.py' -v
```

Requiere NumPy. Cada simulación fija una semilla para reproducibilidad. Las fórmulas y resultados son hipótesis/modelos, no validación de riesgo real. Las referencias conceptuales incluyen Basel Committee (marcos de riesgo de mercado y liquidez), FRTB/Expected Shortfall, BCBS LCR/NSFR, literatura EVT, GARCH, modelos de fire sales y optimización CVaR; deben verificarse vigencia y aplicación local antes de citar como obligación regulatoria.

## Diseño de validación

Comparar contra baselines, registrar supuestos, hacer validación temporal, stress out-of-distribution, sensibilidad a parámetros, error Monte Carlo y coherencia de unidades. Separar riesgo de liquidez de financiación (cash-flow shortfall) de liquidez de mercado (impacto y profundidad). Un modelo sin datos reales puede demostrar propiedades numéricas, no poder predictivo.


## Experimentos ejecutados y contrato numérico

El [notebook](notebook.ipynb) separa pérdidas de mercado, déficit de financiación y costo económico de financiar ese déficit. Incluye reserva inicial, primera ruptura censurada, sensibilidad de ES y una ablación de dependencia por permutación.

VaR usa ahora la inversa generalizada empírica (sin interpolar entre átomos); ES conserva masa de cola exactamente 1−α. La convención se contrasta con las mismas fixtures racionales de construcción. La acumulación de caja rechaza overflow y los conteos de escenarios/horizonte deben ser enteros explícitos.
