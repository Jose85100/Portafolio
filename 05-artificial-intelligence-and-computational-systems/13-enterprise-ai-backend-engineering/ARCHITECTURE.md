# Enterprise AI Backend — architecture reference

```text
Client / Enterprise SSO (OIDC)
          |
API Gateway (Kotlin: REST, rate limits, authN, audit)
          |
Policy Enforcement (RBAC/ABAC, tenant, scopes)
          |
  +-------+-------------------+--------------------+
  | Job API / control plane   | RAG knowledge API  | Engineering API
  +-------+-------------------+--------------------+
          |                   |                    |
PostgreSQL (durable jobs, outbox, ACL, evidence, audit)
          |                   |                    |
Message Broker          Vector/Search Index       CI Sandbox
          |
Rust workers (bounded concurrency, leases, retry, checkpoints)
          |
Python model/retrieval services (versioned model endpoints)
          |
Observability + SLO + independent security validation
```

## Bounded contexts

1. API and tenant governance; 2. identity and policy; 3. distributed execution; 4. enterprise knowledge; 5. developer workflow. Keep separate logical domains even if initially deployed as modular monolith. Use asynchronous boundaries only for durable jobs; synchronous request chains must have strict timeouts and budgets.

## Sequence and failure semantics

POST creates idempotent job and outbox record in one DB transaction → publisher emits event → worker acquires lease → executes bounded task → stores result → marks state → audit. At-least-once delivery implies duplicate events: use unique job IDs and deduplicated external effects. Never assert exactly-once behavior for third-party APIs.

## Security boundary

External identity provider issues OIDC tokens; gateway verifies signature, issuer, audience, expiry and claims. Authorization happens at each resource boundary, not only edge. Agent tools receive scoped credentials. RAG retrieval filters ACL before and after ranking. CI agents cannot deploy to production without independent approvals.

## Architecture decisions

ADR-001 Kotlin control plane vs Rust data plane (profile-driven); ADR-002 PostgreSQL transactional outbox; ADR-003 OIDC provider not custom IdP; ADR-004 modular monolith first; ADR-005 OpenTelemetry and immutable evidence; ADR-006 independent model/security gates.
