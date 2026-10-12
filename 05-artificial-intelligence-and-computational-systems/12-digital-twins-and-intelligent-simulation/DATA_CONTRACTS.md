# Versioned contracts and accounting invariants

All contracts are conceptual v1 schemas; production implementations must use JSON Schema/Protobuf with compatibility tests. Prefer decimal minor units for money, explicit ISO 4217 currency, timezone-aware timestamps, UTC storage, and event-time vs available-time separation.

## TwinObservation/v1

```json
{"schema_version":"1","entity_id":"pseudonym","event_id":"uuid","event_time":"2026-01-01T00:00:00Z","available_time":"2026-01-01T00:01:00Z","variable":"settled_amount","value_minor":1000,"currency":"COP","source":"authorized_ledger","quality":"verified"}
```

## TwinState/v1

```json
{"schema_version":"1","twin_id":"payments","as_of":"2026-01-01T00:01:00Z","state_version":"hash","model_version":"semver","observations_cutoff":"2026-01-01T00:01:00Z","posterior_ref":"artifact-uri"}
```

## TwinScenario/v1

```json
{"schema_version":"1","scenario_id":"outage-stress","horizon_minutes":1440,"interventions":[],"exogenous_paths_ref":"artifact-uri","seed":1234,"assumptions_version":"hash"}
```

## TwinRun/v1 and TwinValidation/v1

Run records include input and code hashes, seed, calendar, scenario, numerical tolerances, outputs, error and hardware metadata. Validation records include out-of-time windows, baselines, calibration, reconciliation, convergence, independent sign-off and limitations.

## Non-negotiable invariants

1. For internal settled transfers, sum of signed participant transfers is zero in each currency before fees and external flows.
2. A payment has one authoritative settlement state; replay and deduplication do not create money.
3. Asset/liability stocks reconcile with corresponding cashflow and journal entries.
4. Loan transitions are exclusive and exhaustive for the defined state machine; absorbing default only when explicitly modeled.
5. No observation with available_time > decision_time can enter an as-of state.
6. Probabilities are normalized and cash amounts cannot be silently converted across currencies.
7. Every simulation records whether parameters are estimated, assumed or synthetic.

## Security and privacy

No PAN, credentials, unmasked account numbers or customer PII in public repositories, traces or synthetic fixtures. Scope access by tenant, least privilege, retention and audit. Bank transaction access requires explicit authorization.
