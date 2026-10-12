# Delivery and validation roadmap

## Milestones

- M0: workload characterization, threat model, API contracts and SLO definitions.
- M1: Kotlin gateway, OIDC integration, PostgreSQL job lifecycle and typed REST errors.
- M2: Rust worker with lease, idempotency, retry budgets and crash recovery tests.
- M3: RAG retrieval with ACL fixtures, citations, redaction and evaluation corpus.
- M4: AI engineering workflow with sandboxed test generation, CI gate and human review.
- M5: load, chaos, pen-test, recovery, SBOM, architecture review and cloud staging.

## Test matrix

| Quality axis | Baseline | Challenger / validation |
|---|---|---|
| REST correctness | OpenAPI contract fixtures | backward compatibility + fuzzing |
| Identity | expired/wrong-audience token tests | privilege escalation / tenant isolation |
| Queue execution | single worker | burst, crash, duplicate, lease expiry |
| Performance | synchronous baseline | Kotlin/Rust measured p95/p99 and cost |
| RAG | lexical retrieval | hybrid retrieval, reranking, ACL leakage |
| AI coding | manual review baseline | controlled AI review with defect detection |
| Deployment | manual staging | CI, rollback, chaos, observability |

## Acceptance discipline

A green build is necessary but insufficient. Do not label production-ready without threat review, load evidence, runbooks, rollback and on-call ownership. This repository currently contains architecture specifications only, not the listed implementation milestones.
