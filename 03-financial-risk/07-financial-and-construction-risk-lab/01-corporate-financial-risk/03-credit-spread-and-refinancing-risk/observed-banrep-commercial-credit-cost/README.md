# BanRep commercial-credit refinancing sensitivity

## Executive use

For a treasury or risk committee, the decision question is whether current bank refinancing conditions could materially change annual financing expense on a maturing balance. This companion puts an official Colombian lending-rate history into a transparent sensitivity: it applies the latest observed rate and historical distribution points to a fixed hypothetical COP 10 billion balance. It helps frame a discussion about repricing capacity and interest-cost buffers. It does not estimate a company's credit spread, predict a future rate, or establish what a borrower would actually pay.

## Architecture

```text
BanRep Suameca monthly series 15129
        → versioned CSV snapshot + SHA-256
        → schema / chronology / range QA
        → latest, historical median, p90 and maximum rate scenarios
        → annual-interest sensitivity + chart + QA manifest
```

## Observed data and reproducibility

- Publisher: Banco de la República, Suameca. Series 15129: **“Créditos Comerciales (Preferencial o Corporativo), Tasa de interés”**, monthly, effective annual percentage. Coverage in this snapshot: 2002-05–2026-09 (293 observations).
- BanRep describes placement rates as rates applied by credit institutions to credit products. The data are aggregated from SFC reports and rates are weighted averages by disbursed amount. The category is a bank-loan benchmark for new disbursements; it is not bond issuance yields or a matched-maturity risk-free curve.
- API endpoint and request parameters, retrieval timestamp, response SHA-256, and snapshot SHA-256 are in `data/source_manifest.json`. The CSV is the small aggregate time series only; no borrower-level data are present.
- Rebuild outputs offline with Python and Matplotlib: `python3 run_application.py`. The runner validates the source hash, row count, unique ascending periods and positive plausible rates, then regenerates `results/` and `figures/`.
- Output uses a hypothetical fixed principal of COP 10 billion. Annual interest is calculated as principal × effective annual rate; it is a simple annualized sensitivity, not a payment schedule or accounting effective interest rate.

## Trade-off log

| Decision | Rationale | Cost / consequence |
|---|---|---|
| Use BanRep commercial preferential/corporate lending rates | Official, repeatable, long monthly history with defined aggregation | Does not reveal issuer-level risk premium, tenor curve or instrument terms |
| Use historical median, p90, maximum and latest observation | Transparent observed-rate scenarios that are easy to challenge | Historical percentiles are not forecasts or calibrated stress quantiles |
| Fix principal and annualize interest | Keeps the calculation auditable for executive discussion | Ignores amortization, fees, taxes, covenants, collateral, currency and term structure |
| Do not subtract TES, DTF or IBR | Those are sovereign or money-market/reference rates, not matched borrower funding spreads | A corporate spread estimate requires instrument-level borrowing yield and matched reference yield |

## Model risk, governance and regulatory relevance

This is an observed-data sensitivity, not a credit-risk model. There is no estimated PD/LGD, spread curve, calibration or production decision rule. For any institutional use, Treasury must replace the illustrative balance with approved maturity schedules, validate the applicable borrower/product/tenor segment, and independently reconcile source definitions and interest conventions. A second reviewer should reproduce the extract and calculation from the manifest before the output informs a limit or funding decision.

The design supports traceability and challenge consistent with the governance intent of ISO 31000 / COSO ERM: source, assumption, calculation and decision boundary are explicit. It does not claim compliance with Basel, IFRS 9, ISO 31000 or COSO ERM. Basel / IFRS 9 credit measurement would require entity-specific exposures and governed credit-risk inputs; this benchmark cannot substitute for them.

## Limitations and data gap

- The source is an aggregate weighted average of **new commercial bank credit disbursements**; a borrowing company's refinancing cost can differ materially by rating, size, sector, collateral, tenor, relationship, currency, and market access.
- “Preferential or corporate” is the source's loan category, not a corporate bond spread. No spread is inferred from the series.
- The snapshot ends 2026-09 and may be revised or updated. A refreshed snapshot requires recording new retrieval metadata and recalculating hashes.
- The model specification in the parent README remains design-only. To validate issuer-level refinancing application, minimum missing evidence is borrower/instrument, currency, amount, issuance or repricing date, tenor, contractual and all-in cost (including fees), matched reference curve, amortization/maturity profile, and realized refinancing outcomes. For credit spread analysis, both borrower yield and a same-currency / matched-tenor reference yield are necessary.
- The sensitivity is not a refinancing recommendation, valuation, forecast, regulatory capital measure, or approved internal model.

## Independent validation acceptance gates

Before any institutional reuse: (1) independently retrieve and hash the official series; (2) reconcile category, frequency, effective-rate convention, and revisions to the BanRep methodology; (3) unit-check the principal × rate calculation and cross-check it independently; (4) test robustness to borrower-specific rates, tenor, fees, amortization and currency once authorized data exist; and (5) define acceptance tolerances with Treasury / Model Risk before evaluating results. No issuer-level validation or backtest is possible with the aggregate public series alone.

## Official sources

- [BanRep historical interest-rate methodology](https://www.banrep.gov.co/es/estadisticas-economicas/series-historicas/tasas-interes) — explains placement rates, SFC formats, weighting by disbursement amount and category definitions.
- [BanRep Suameca multiple-data download](https://suameca.banrep.gov.co/descarga-multiple-de-datos/) — public catalog/download interface for the series.
- [BanRep placement-rate tables](https://www.banrep.gov.co/es/node/41999) — describes consolidated information from SFC reports and historical coverage.
