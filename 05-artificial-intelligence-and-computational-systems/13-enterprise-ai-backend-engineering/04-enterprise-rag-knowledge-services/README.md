# Enterprise RAG & Knowledge Services

**Maturity: S1 — architecture and implementation specification.** No runnable production service, empirical performance claim or completed test is asserted.

## 1. Product and system boundary

Permission-aware retrieval and grounded answering across enterprise documents. Define user stories, tenant ownership, trust boundaries, request lifecycle, failure handling, dependency contracts and acceptance criteria. Technology: **Kotlin REST gateway, Python retrieval/evaluation, Rust ingestion worker, PostgreSQL/pgvector**.

## 2. REST and contract-first design

Endpoints: POST /v1/ingest, POST /v1/search, POST /v1/answers, GET /v1/documents/{id}/lineage.

Use versioned OpenAPI 3.1 schemas, typed error envelopes, cursor pagination, request_id/trace_id, idempotency keys for mutable operations, explicit 401/403/409/429/5xx behavior, documented retries and timeouts. Version compatibility and deprecation policy are required.

## 3. System architecture

Ingest → parse → chunk → classify ACL → embed/index → hybrid retrieval → ACL filter → rerank → answer with evidence → audit. Enforce authorization both before retrieval and at final result.

Separate domain logic from transport and infrastructure. Specify service discovery, configuration, caching, persistence, horizontal scaling, backpressure, eventual consistency and disaster recovery. Include threat boundaries and data classification in ADRs.

## 4. Mathematical and statistical engineering

Ranking score s(d,q)=α·BM25(d,q)+(1−α)·cos(e_d,e_q); α tuned on held-out relevance data. For evaluation: recall@k, MRR, nDCG, citation support and abstention.

Performance experiments require fixed hardware, concurrency profile, warm-up, repetitions, confidence intervals for quantiles (bootstrap where appropriate), load generation outside the target process, saturation tests and tail-latency analysis. Reliability experiments must distinguish correlated failures and timeouts from independent errors.

## 5. Security and identity

Document-level ACL and tenant boundaries, PII redaction, encryption, injection defense, retention/deletion propagation, versioned embeddings.

Apply OWASP API Security risks, secure dependency management, audit integrity and least privilege. OAuth 2.0 authorization and OIDC authentication are distinct; SSO is a user experience / federation pattern, not a substitute for service authorization.

## 6. Verification plan

ACL leak tests, retrieval quality fixtures, prompt injection corpus, stale/deleted documents, missing citations, index consistency.

Quality gates: formatting/lint, static analysis, SAST, SBOM/dependency audit, unit/contract/integration tests, fault injection, performance baseline, independent security review, reproducible builds and documented rollback.

## 7. SLOs and observable outputs

Evidence precision, answer support, retrieval recall, unauthorized disclosure=0 in tests, end-to-end latency.

SLO targets are **to be defined from workload and risk appetite**, not invented as measured results. Instrument traces, logs and metrics with OpenTelemetry, redaction and bounded cardinality.

## 8. Planned repository implementation

```text
api/                  OpenAPI 3.1 + typed schemas
services/             Kotlin or Rust source by service
workers/              async processing / model integration
infra/                Docker, deployment manifests, IaC
security/             policy fixtures, threat model
benchmarks/           reproducible load/fault experiments
tests/                unit, contract, integration, adversarial
adrs/                 architecture decision records
reports/              performance, security, model cards
```

This tree is **planned**, not created in this project yet. Gates: G0 research → G1 architecture → G2 runnable vertical slice → G3 integration/security → G4 load and resilience → G5 cloud release with rollback. G2–G5 pending.

[Shared architecture](../ARCHITECTURE.md) · [Validation](../VALIDATION.md).
