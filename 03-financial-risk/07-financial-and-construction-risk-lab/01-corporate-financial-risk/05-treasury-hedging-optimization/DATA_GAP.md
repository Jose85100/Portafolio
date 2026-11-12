# Brecha de datos: optimización de coberturas

**Corte de revisión:** 2026-11-11. **Estado:** hay choques públicos de mercado, pero no posiciones ni operaciones de cobertura para evaluar una política.

El companion [TRM/DTF BanRep](../02-fx-interest-rate-exposure/README.md) muestra sensibilidades separadas sobre saldos hipotéticos. No observa exposición neta, contratos de derivados, spreads, colateral, costos, efectividad contable o resultados de una estrategia de cobertura.

## Datos mínimos

- Exposición subyacente y calendario de flujos por moneda/índice, bruto y neto, incluyendo incertidumbre de forecast.
- Instrumento hedge, nocional, precio, tenor, contraparte, colateral, costos de transacción y modificaciones.
- Política aprobada, límites, objetivos (P&L, caja, VaR/CVaR o cobertura contable) y restricciones legales/contables.
- Riesgo y costo realizados por fecha para comparar política vigente, alternativas y baseline sin cobertura.

La validación requiere backtest fuera de muestra con precios ejecutables, sensibilidad a basis risk, costos y cambios de liquidez, análisis de estabilidad de pesos y revisión independiente de efectividad. Sin libro de exposiciones y trades, la optimización solo puede demostrar matemática bajo escenarios; no recomendar hedge ratios institucionales.
