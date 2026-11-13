# Residual data gap: cash conversion and forecasting

**Review date:** 2026-11-11. **Status:** official public filings support sector-level input coverage and a complete-case DIO component for the matched 2024 top-1,000 cohort. They do not support exact DSO/DPO, CCC, a cash forecast, or Liquidity-at-Risk.

The [Supersociedades working-capital companion](observed-supersociedades-working-capital-coverage/README.md) links the official 2025 cohort workbook to NIIF balance sheets for 2023/2024 and the 2024 NIIF income statement. NIT and presentation-basis matching is done in memory; only macro-sector coverage counts and median inventory-days proxy are published. From the top-1,000 cohort, the runner found 615 aligned 2023 balance reports, 642 aligned 2024 balance reports, 639 aligned 2024 income reports, and 543 entities with the complete positive inputs for DIO (54.3%). See the companion manifest for concept-level missingness, source hashes, duplicate/conflict checks, and sector-specific coverage.

## Why DSO, DPO, and CCC remain blocked

- **DSO:** the public statement has `Cuentas comerciales por cobrar y otras cuentas por cobrar corrientes`, but it combines trade and other receivables. `Ingresos de actividades ordinarias` is total ordinary revenue, not sales to credit customers. The required numerator/denominator concepts do not align.
- **DPO:** the public statement has `Cuentas por pagar comerciales y otras cuentas por pagar corrientes`, which includes other payables. `Costo de ventas` is not supplier purchases. Estimating purchases from cost of sales and inventory change would require unvalidated assumptions about write-offs, impairment, FX, acquisitions, production, and other inventory movements; this companion does not do so.
- **Cash conversion cycle:** without semantically aligned DSO and DPO, `DSO + DIO − DPO` would combine incomplete or mismatched ratios. It is not calculated.
- **Forecast / LaR:** annual balance sheets and income statements do not show collection/payment dates, cash availability, facility draw conditions, covenant headroom, forecast vintages, or realized cash shortfalls.

## Minimum data needed to close the gap

1. Same-entity, same-perimeter credit sales and pure trade receivable balances, with opening and closing dates and an approved treatment of returns, taxes, and write-offs.
2. Supplier purchases and pure trade payables on the same accounting perimeter, or validated inventory roll-forward data that supports purchase reconstruction.
3. More frequent cash receipts, payments, inventories, and funding sources, retaining forecast vintages and the information available at each forecast origin.
4. Realized shortfall/breach outcomes, cure dates, emergency funding costs, and institution-approved thresholds.
5. Authorized data use, lineage, filing/version rules, source reconciliation, and independent out-of-time validation criteria.

The only calculated rotation measure is the complete-case DIO proxy described in the companion: average current inventory at the 2023 and 2024 year-end balance dates divided by 2024 cost of sales, multiplied by 365. The entity's declared NIIF presentation basis is aligned across both balance dates and the income statement; all three fields follow Supersociedades' thousands-of-COP reporting guidance, so the monetary unit cancels. It is an annual stock-to-flow accounting proxy, not cash turnover or a forecast.
