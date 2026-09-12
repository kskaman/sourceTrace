---
title: "Engineering Standards"
category: "Engineering"
doc_type: "reference"
last_updated: "2025-01-15"
owner: "Engineering"
classification: "Internal"
---

# Engineering Standards

**Effective Date:** January 15, 2025
**Owner:** Sarah Chen, VP of Engineering
**Applies to:** All Acme Corp engineering teams

---

## 1. Language Choices

Acme Corp uses three primary languages across its stack. Team leads may not introduce additional languages without VP of Engineering approval.

| Language | Usage | Version Policy |
|---|---|---|
| Python | API services, ML pipeline, data processing, internal tooling | 3.11+ (track latest stable minus one) |
| Go | High-throughput ingestion service, real-time event bus, CLI tools | 1.22+ (track latest stable) |
| TypeScript | Frontend (React), serverless functions, BFF (backend-for-frontend) layer | 5.3+ (track latest stable) |

SQL (PostgreSQL dialect) is used for database queries and migrations but is not counted as a primary language.

Shell scripts (Bash) are permitted for CI/CD pipelines and operational automation. Scripts exceeding 100 lines should be rewritten in Python.

## 2. Code Style

### 2.1 Formatting

All code must be auto-formatted before commit:

| Language | Formatter | Configuration |
|---|---|---|
| Python | `ruff format` | `pyproject.toml` (repo root) |
| Go | `gofmt` | Default settings |
| TypeScript | `prettier` | `.prettierrc` (repo root) |

CI rejects pull requests with formatting violations. No exceptions.

### 2.2 Linting

| Language | Linter | Configuration |
|---|---|---|
| Python | `ruff check` | `pyproject.toml` |
| Go | `golangci-lint` | `.golangci.yml` |
| TypeScript | `eslint` | `.eslintrc.json` |

All lint rules are enforced in CI. Adding a lint suppression comment (`# noqa`, `//nolint`, `// eslint-disable`) requires a justifying comment explaining why the rule does not apply.

### 2.3 Naming Conventions

- Python: `snake_case` for functions and variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Go: Exported identifiers `PascalCase`, unexported `camelCase`, per Go convention.
- TypeScript: `camelCase` for variables and functions, `PascalCase` for types, interfaces, and React components.
- Database: `snake_case` for tables and columns. Table names are plural (`users`, `records`, `audit_logs`).

## 3. Testing Requirements

### 3.1 Coverage Targets

| Level | Minimum Coverage | Enforcement |
|---|---|---|
| Unit tests | 80% line coverage | CI blocks merge below threshold |
| Integration tests | Critical paths covered (no numeric target) | Reviewed in PR by code owner |
| End-to-end tests | Smoke suite must pass on every deploy | CI blocks deploy on failure |

### 3.2 Test Conventions

- Test files live alongside the code they test (`foo.py` → `foo_test.py`, `bar.go` → `bar_test.go`, `baz.ts` → `baz.test.ts`).
- Tests are deterministic. No reliance on wall-clock time, network calls to external services, or shared mutable state between test cases.
- Flaky tests are quarantined in CI within 24 hours of detection and tracked in the engineering backlog. A test that fails intermittently more than twice in a week is quarantined.
- Integration tests that require a database use a dedicated test database instance, reset between test suites.

### 3.3 Load and Performance Tests

Services with an SLO must have a performance test suite that runs weekly in the staging environment. The suite validates that the service meets its latency SLO under expected peak load (2x average daily traffic).

## 4. SLIs/SLOs for Services

Every production service must define at least three Service Level Indicators (SLIs) and corresponding Service Level Objectives (SLOs):

| SLI | Definition | Standard SLO |
|---|---|---|
| Availability | Percentage of successful requests (non-5xx) out of total requests | 99.95% |
| Latency (p99) | 99th percentile response time measured at the load balancer | < 500ms |
| Error rate | Percentage of requests returning a 5xx status code | < 0.05% |

### 4.1 SLO Review

SLOs are reviewed quarterly by the service owner and the engineering manager. If a service misses its SLO in any calendar month, the team must:

1. Conduct a root cause analysis within 5 business days.
2. Identify remediation actions with owners and deadlines.
3. Report findings in the monthly engineering review.

### 4.2 Error Budgets

Each service has an error budget derived from its availability SLO. For a 99.95% SLO, the monthly error budget is 21.6 minutes of downtime (in a 30-day month). When the error budget is exhausted:

- Feature development freezes for the affected service.
- The team focuses exclusively on reliability work until the budget is replenished at the start of the next month.
- The VP of Engineering may grant an exception for critical business deadlines, documented in writing.

## 5. Dependency Management

### 5.1 Version Pinning

All dependencies are version-pinned in lock files (`poetry.lock`, `go.sum`, `package-lock.json`). Floating version ranges in manifest files are prohibited in production services.

### 5.2 Automated Updates

Dependabot (GitHub) is configured to open pull requests for dependency updates weekly. Security updates are prioritized per the Vulnerability Management Policy:

- Critical CVEs: PR merged within 7 days.
- High CVEs: PR merged within 30 days.
- Routine updates: Batched and merged monthly.

### 5.3 Approved and Prohibited Dependencies

The engineering wiki maintains a list of pre-approved libraries for common tasks (HTTP clients, logging, serialization, testing frameworks). Libraries not on the approved list require a lightweight review by the relevant platform team before adoption.

Prohibited categories:
- Libraries with known unpatched critical vulnerabilities.
- Libraries with licenses incompatible with Acme Corp's commercial use (GPL, AGPL without a commercial exception).
- Libraries that have not been updated in 2+ years (abandoned projects).

## 6. Code Review

All production code changes require at least one approving review from a code owner before merge. See the Code Review Guidelines for detailed expectations, approval rules, and merge queue procedures.

## 7. Documentation

Every service must maintain:

- A `README.md` with setup instructions, architecture overview, and deployment notes.
- An API contract (OpenAPI spec for HTTP services, protobuf definitions for gRPC services).
- A runbook linked from the service catalog, covering common operational tasks and known failure modes.

## 8. Policy Governance

These standards are maintained by the Engineering Platform team and approved by the VP of Engineering (Sarah Chen). Proposed changes are discussed in the biweekly engineering standards review meeting. Questions should be directed to eng-standards@acmecorp.com.

---

*Version 4.0 — Last revised January 15, 2025*
