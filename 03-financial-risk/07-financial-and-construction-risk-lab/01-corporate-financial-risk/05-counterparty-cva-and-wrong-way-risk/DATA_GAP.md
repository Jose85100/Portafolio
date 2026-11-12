# Data gap: counterparty CVA and wrong-way risk

**Review date:** 2026-11-11. **Status:** no public matched panel or authorized internal trade/default panel is available in this project; CVA/WWR are not estimable.

Public risk factors exist, but do not identify a counterparty valuation adjustment. BanRep's third-quarter 2026 report studies Colombian sovereign CDS structure and pricing; this is a sovereign credit signal, not a bank or corporate counterparty curve, and the report page does not provide a dated public spread panel suitable for hazard calibration. SFC open data on loan quality and the MURIC reporting description cover loan/debtor records, not derivative netting sets and collateralized exposures. Currency rates, sovereign CDS and aggregate credit quality may be contextual stress variables; their co-movement is not evidence of wrong-way risk without aligned `EPE/PFE`, default and recovery for the same counterparties.

## Minimum data contract

- Stable pseudonymous legal-counterparty and netting-set keys, permitted linkage, group and jurisdiction.
- Trade-level dated valuations, cash flows and exposure profiles under market and default scenarios.
- Enforceable netting/CSA terms, collateral calls, disputes, haircuts, liquidation delay and close-out assumptions.
- Dated counterparty credit curves or rating/default histories, event definitions, recoveries, collateral realized and exposure at default.
- Timestamp-aligned market factors, defaults, collateral and exposure history to estimate conditional dependency and wrong-way stress.
- Source lineage, valuation controls, accounting reconciliation, permissions, and realized close-out outcomes for independent backtesting.

## Why the public proxies do not close the gap

- A sovereign CDS spread prices protection on Colombia's sovereign debt. It cannot be assigned to a private issuer or bank without an explicit, validated mapping; even such a mapping would not supply exposure or recovery.
- Loan-portfolio ratings/default quality describe borrowers and loan balances. They do not represent counterparty derivative exposures, legally netted positions, CSA collateral, or close-out losses.
- Macro factors (TRM, rates, yield curves) describe market states but contain no default-event or loss measure for the same counterparty population.
- Cross-sectional institution ratings or aggregate system ratios, where publicly visible, do not give a time-aligned exposure-credit panel. An aggregate correlation is ecological and cannot validate conditional exposure/default dependence.

Advancement requires an internal, authorized, longitudinal dataset meeting the minimum contract. Without it, the defensible deliverable is source documentation and a data contract, not an observed CVA estimate. A separate reproducible market-conditioned sensitivity is provided in `public_proxy.py`; its exposure and spread-to-hazard mapping are assumptions, not observed counterparty outcomes.
