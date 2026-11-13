# Data gap: issuer-level corporate credit spreads

## What is observable

BanRep/Suameca series 15129 provides a reproducible monthly, weighted-average effective annual rate for new commercial bank loans in the “Preferencial o Corporativo” category. Its current repository snapshot covers 2002-05–2026-09. The `observed-banrep-commercial-credit-cost` companion uses it only for a hypothetical bank-refinancing cost sensitivity.

## What remains missing

The official public series located does **not** provide an issuer-level corporate bond/loan spread over a matched reference curve, nor a named borrower's all-in refinancing cost. TES, DTF and IBR are sovereign or reference rates and are not substitutes for the missing borrower premium. SFC's public methodology describes aggregate placement-rate data by product, tenor and other dimensions, while SICOP is a reporting system for issuers; the material located did not expose a public instrument-level historical yield/spread panel suitable for this analysis. BVC placement summaries show aggregate issuance activity/indicators, not the complete matched issuer and reference-curve history required here.

## Sources investigated

- [BanRep historical interest-rate methodology](https://www.banrep.gov.co/es/estadisticas-economicas/series-historicas/tasas-interes): describes SFC-reported placement-rate categories and weighted aggregation by disbursed amounts.
- [BanRep/Suameca series download catalog](https://suameca.banrep.gov.co/descarga-multiple-de-datos/): exposes monthly series 15129, “Créditos Comerciales (Preferencial o Corporativo), Tasa de interés.”
- [SFC SICOP](https://www.superfinanciera.gov.co/sfc-sicop-web/login.jsf): public description says authorized issuers report offerings/placements through the system; the system entry point is authenticated and is not itself a validated public spread dataset.
- BVC-related public issuance summaries found via market reports provide aggregate totals and coupon/index types but do not furnish complete, reproducible matched issuer yields and curve points for the risk metric.

## Minimum data contract to close the gap

For each refinancing/issuance observation: borrower or stable pseudonymous issuer ID; instrument and seniority; issue / repricing date; currency; coupon type and index; tenor and duration; issue price / yield or all-in effective cost including fees; amount; collateral / rating / sector where permitted; matched-currency and matched-tenor reference yield at the same timestamp; and subsequent refinancing/default outcome. Include source lineage, revisions, coverage, licensing and permission to retain/reuse. Without both borrower yield and a matched reference yield, do not calculate or label a corporate spread.

The current public-data companion is context only. It cannot validate this project's issuer-level spread or refinancing-risk application.
