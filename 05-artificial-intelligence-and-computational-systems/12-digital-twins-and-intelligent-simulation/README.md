# Digital Twins & Intelligent Simulation — Banking, Payments and Financial Risk

**Status: S1, research and engineering design.** This section now contains **seven independent project specifications**, **three disciplinary foundations**, common contracts, architecture and a falsifiable validation plan. No production twin or institution-specific model has been built or validated in this folder.

## Scope and distinguishing criterion

A digital twin represents a defined system using a synchronized state estimate, dynamic simulator, uncertainty propagation and independently testable predictions. Distinguish a synchronized digital twin from a dashboard, static stress spreadsheet or generic simulation.

## Three independent foundations

1. [Mathematical and dynamical foundations](fundamentals/01-mathematical-foundations.md)
2. [Statistical inference and data assimilation](fundamentals/02-statistical-foundations.md)
3. [Computational and numerical engineering](fundamentals/03-computational-foundations.md)

## Seven research projects

1. [Digital Banking System Twin](projects/01-digital-banking-system-twin/) — deposits, pricing, credit and balance-sheet economics.
2. [Real-Time Payments & Settlement Twin](projects/02-real-time-payments-settlement-twin/) — rails, intraday liquidity, queues and settlement finality.
3. [Credit Portfolio & Collections Twin](projects/03-credit-portfolio-collections-twin/) — transitions, default, recoveries and policy effects.
4. [Liquidity, Treasury & ALM Twin](projects/04-liquidity-treasury-alm-twin/) — funding, runoff, liquidity gaps and interest-rate risk.
5. [Fraud & Financial Crime Twin](projects/05-fraud-financial-crime-twin/) — adaptive attacks, review queues and customer friction.
6. [Operational & Cyber Resilience Twin](projects/06-operational-cyber-resilience-twin/) — outage cascades and recovery.
7. [Integrated Financial Contagion & Stress Twin](projects/07-integrated-financial-contagion-stress-twin/) — nonlinear feedback, reverse stress and joint breaches.

## Shared engineering

- [Reference architecture and coupling semantics](ARCHITECTURE.md)
- [Versioned data contracts and ledger invariants](DATA_CONTRACTS.md)
- [Validation matrix, implementation roadmap and bank use cases](VALIDATION_AND_ROADMAP.md)
- [Existing credit portfolio digital twin research](../../../03-financial-risk/04-advanced-research/02-nonstationary-credit-digital-twin/README.md) — separate prior proposal, avoid duplicate claims.

## Intended operating modes

**Research** using public/synthetic data; **tactical D+1** using governed bank records; **intraday** only with authorized streaming payment/ledger feeds. Public macro and payment-system aggregates do not identify private customer transitions, fraud labels or actual participant settlement queues.

**Important:** seven new S1 specifications are distinct from the prior five unimplemented illustrative application tracks; no code/test results are asserted.
