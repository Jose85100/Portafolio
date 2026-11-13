# Data gap: corporate ALM and duration gap

**Review date:** 2026-11-11. **Status:** public observed liquidity context available; no matched corporate/institutional asset-liability cash-flow inventory is present.

The SFC historical IRL companion in [observed-sfc-liquidity](observed-sfc-liquidity/README.md) provides category-level ALM and RLN aggregates for Colombian credit establishments from March 2020 to December 2022. The series is official and reproducible, but the downloadable historical file is stale for current monitoring and has no asset/liability repricing cash flows. It supports public liquidity context only. The observed BanRep TRM/DTF sensitivity in [FX and interest-rate exposure](../02-fx-interest-rate-exposure/README.md) uses fixed hypothetical balances; neither dataset gives an entity's realized exposure or EVE/NII outcome.

## Minimum data contract

- Dated asset and liability cash flows, principal, currency, reference index, reset tenor, maturity, and contractual options.
- Repricing and behavioral assumptions with source, owner, version, and observed prepayment/withdrawal outcomes.
- Market curves and instrument valuations at the same as-of times; hedge positions and accounting treatment.
- Reconciled balance-sheet totals, historical rate shocks, realized earnings/EVE outcomes, and permissions.

Validation requires parallel/nonparallel curve shocks, independent valuation, behavioral stress, out-of-time EVE/NII backtests, and approved limits. Aggregate regulatory IRL and market-factor sensitivities alone cannot validate duration gap, liquidity-buffer need, or a specific entity's performance.
