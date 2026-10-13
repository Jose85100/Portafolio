# Secure Identity & AI Access Gateway

**Maturity: S1 — architecture and implementation specification.** No runnable production service, empirical performance claim or completed test is asserted.

## 1. Product and system boundary

Central identity and policy enforcement for AI APIs, agents and enterprise knowledge resources. Define user stories, tenant ownership, trust boundaries, request lifecycle, failure handling, dependency contracts and acceptance criteria. Technology: **Kotlin / Spring Security, Rust policy evaluator, OpenID Connect, OAuth 2.0, PostgreSQL**.

## 2. REST and contract-first design

Endpoints: GET /.well-known/openid-configuration (external IdP), POST /v1/policy/evaluate, GET /v1/audit/events.

Use versioned OpenAPI 3.1 schemas, typed error envelopes, cursor pagination, request_id/trace_id, idempotency keys for mutable operations, explicit 401/403/409/429/5xx behavior, documented retries and timeouts. Version compatibility and deprecation policy are required.

## 3. System architecture

External OIDC provider → JWT verifier → policy enforcement point → policy decision point → protected service. Never build a bespoke identity provider unnecessarily.

Separate domain logic from transport and infrastructure. Specify service discovery, configuration, caching, persistence, horizontal scaling, backpressure, eventual consistency and disaster recovery. Include threat boundaries and data classification in ADRs.

## 4. Mathematical and statistical engineering

Access decision allow(s,a,r,c)=authenticated(s) ∧ scope(s,a) ∧ role(s,r) ∧ tenant_match(s,r) ∧ contextual_policy(s,a,r,c). Deny by default; explicit policy version.

Performance experiments require fixed hardware, concurrency profile, warm-up, repetitions, confidence intervals for quantiles (bootstrap where appropriate), load generation outside the target process, saturation tests and tail-latency analysis. Reliability experiments must distinguish correlated failures and timeouts from independent errors.

## 5. Security and identity

OIDC authorization code with PKCE for public clients, JWT issuer/audience/expiry/key rotation, OAuth scopes, RBAC/ABAC, mTLS for internal services, SSRF prevention, least privilege.

Apply OWASP API Security risks, secure dependency management, audit integrity and least privilege. OAuth 2.0 authorization and OIDC authentication are distinct; SSO is a user experience / federation pattern, not a substitute for service authorization.

## 6. Verification plan

Token substitution, replay, expired tokens, key rotation, IDOR, privilege escalation, policy-conflict, malicious redirect and audit completeness tests.

Quality gates: formatting/lint, static analysis, SAST, SBOM/dependency audit, unit/contract/integration tests, fault injection, performance baseline, independent security review, reproducible builds and documented rollback.

## 7. SLOs and observable outputs

Unauthorized access rejection, policy evaluation latency, audit coverage and false-denial rates.

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
