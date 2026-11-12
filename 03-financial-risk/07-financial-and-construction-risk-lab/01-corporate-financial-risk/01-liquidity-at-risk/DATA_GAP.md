# Data gap: corporate Liquidity-at-Risk

**Review date:** 2026-11-11. **Status:** an observed annual current-ratio sector proxy exists; no observed entity cash shortfall panel or project-level application is available in this repository.

The [Supersociedades top-1,000 current-ratio companion](observed-supersociedades-current-ratio/README.md) reports 2024 year-end accounting liquidity by macro-sector after an in-memory linkage between the official 2025 cohort workbook and NIIF records. It is a selected cohort and static balance-sheet measure, not liquidity-at-risk or a cash-flow forecast. Public macro rates and balance-sheet variables cannot establish cash timing, payment commitments, drawable credit, covenant headroom, or realized liquidity shortfalls. The separate Supersociedades NIIF extraction assessed for the [working-capital route](../03-working-capital-liquidity-forecast/DATA_GAP.md) lacks a sector field and had unstable broad extraction; the cohort-specific query used for this companion is filtered by official NITs and a declared accounting basis.

The executed companion matched 642/1,000 entities (64.2%) with both current-account concepts and an aligned NIIF presentation basis; sector coverage was 41.2%–75.4%. It returned 1,994 source rows for 1,000 NIT queries, retained 642 complete basis-aligned filings, excluded 12 ambiguous generic-group cases, and found no conflicting values within filing/concept. These are coverage and QA checks, not performance or validation results. Rerun the [companion runner](observed-supersociedades-current-ratio/build_companion.py) to refresh source hashes and review whether those coverage rules still hold.

## Minimum data contract

- Entity/project and as-of date; opening unrestricted cash and eligible liquidity buffers.
- Contractual and realized receipts/payments by date, currency, counterparty, and source system; forecast vintages retained.
- Committed and available facilities, draw conditions, maturities, covenants, and collateral constraints.
- Observed breach/shortfall outcomes, cure dates, emergency funding costs, and approved risk thresholds.
- Permissions, lineage, consistent units, missingness rules, and entity-level deduplication.

Acceptance requires independent reconciliation to bank/ERP statements, rolling out-of-time backtests of shortfall probability and amount, stress and reverse-stress checks, and approved thresholds. Without those outcomes, a cash path is an illustrative scenario, not observed LaR.
