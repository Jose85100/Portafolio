# Observed Credit Data & Proxy Registry — Colombia

**Status: adapter implemented and offline test cases authored. The API has not yet been run or a real snapshot validated by this PR.**

This module introduces observed external aggregate signals alongside synthetic research datasets. **It never relabels aggregate delinquency prevalence as individual PD.**

## Reproducible run (online environment)

```bash
python3 03-financial-risk/01-credit-risk/observed-data-proxies/src/observed_portfolio.py --as-of 2026-10-31 --output /tmp/credit-observed
python3 -m unittest discover -s 03-financial-risk/01-credit-risk/observed-data-proxies/tests -v
```

Output: CSV of monthly regional delinquency stock proportions and SHA256 manifest with extraction time, source and grain. If API count reaches the request limit, extraction refuses to publish an incomplete sample. This first adapter expects unique (date, department); if the source has multiple dimensions, aggregate them with explicit definitions before ingestion.

## Verified source registry and model mapping

| Evidence | Dataset / link | Features | Compatible analysis | Cannot establish |
|---|---|---|---|---|
| Observed Colombia aggregate | [ICETEX education credit portfolio](https://www.datos.gov.co/Educaci-n/Comportamiento-de-Cartera-y-Cr-dito-/dugh-vkir) | date, department, credit counts by arrears bucket, published portfolio indicator | macro-regional stress; market monitoring | individual PD / flow transition |
| Observed Colombia aggregate | [ICETEX portfolio by product](https://www.datos.gov.co/Hacienda-y-Cr-dito-P-blico/Distribuci-n-de-cartera-por-producto/rvii-eis8) | balance, entity, modality, product, risk class, delinquency | sector benchmarks | individual LGD |
| Observed Colombia aggregate | [ICETEX pricing](https://www.datos.gov.co/Econom-a-y-Finanzas/Tasas-de-inter-s-activas-por-tipo-de-cr-dito-Hist-/w9zh-vetq) | weighted rate, disbursements, duration, product | pricing and scenario assumptions | contractual rates for specific customer |
| Observed Colombia macro | [Banco de la Republica](https://suameca.banrep.gov.co/descarga-multiple-de-datos/) | policy rate, interest, exchange, inflation | macro IFRS9 scenarios | causal PD response without model validation |
| Observed Colombia macro | [DANE](https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-y-desempleo) | monthly labor indicators | employment shock sensitivity | borrower-specific capacity |
| Observed individual foreign | [UCI Taiwan card defaults](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients+dataset) | payment history, bill, limit, next-month target; 30,000 clients | supervised ML, Gini/KS and calibration | Colombia 12m or lifetime IFRS9 PD |
| Observed individual foreign | [UCI South German Credit](https://archive.ics.uci.edu/dataset/573/south+german+credit) | 1000 historical loans; stratified sample | scorecard baseline | calibrated population-level PD |

## Integrating current workflow

Source -> extraction with timestamp/hash -> source schema and reconciliation -> risk-data-platform -> curated regional/macro features -> credit model feature join -> model validation -> monitoring.

Existing locations:
- Data platform: 05-artificial-intelligence-and-computational-systems/data-engineering/risk-data-platform
- Credit examples: 03-financial-risk/01-credit-risk/credit-risk-products
- IFRS9 research: 03-financial-risk/04-advanced-research/04-ifrs9-forward-looking-ecl
- Validation metrics: PR #151, production-credit-risk-lab

**Open integration gap:** point-in-time features need source publication timestamps (not just observation dates). An API extraction in 2026 cannot prove that a series value was known in 2024. Maintain archival publication vintages. Need independent microcredit default and recovery labels to validate Colombian PD/LGD/EAD. Never fabricate these labels from arrears stocks.

## Data governance

Downloaded raw datasets remain outside Git, with licenses and attribution checked. No customer PII. UCI Taiwan is CC BY 4.0 (DOI 10.24432/C55S3H). The official source indicator is preserved as a raw field because its scale and balance-denominator differ from the derived >90d count share.

## Roadmap

1. Validate live Socrata schema and pagination against a real snapshot; handle historical revisions and dimensional grain.
2. Add curated vintage snapshots for BanRep/DANE plus ICETEX product series; source field mapping and quality gates.
3. Build a separate UCI loader with explicit target metadata, no default-horizon conflation.
4. Wire output as external-feature table in risk-data-platform with as-known-at join, lineage, tests.
5. Test stress elasticity, scenarios and individual-model challenger using independent default labels.

## Corrección de procedencia (2026-11-05)

`dugh-vkir` pertenece a **ICETEX, Vicepresidencia de Crédito y Cobranza**; frecuencia trimestral. No es una serie general de cartera bancaria SFC. La distinción Estudios / Amortización (`epoca_cartera`) forma parte del grano. Los desajustes de conciliación se guardan en `rejected_records.json` y la ejecución falla si superan el 10% de filas o no quedan registros utilizables. La cifra del 10% es un control técnico provisional, no una tolerancia de gobierno aprobada. Revisar el artefacto y el porqué de las discrepancias antes de utilizar indicadores.
