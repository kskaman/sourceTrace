---
title: "Development Workflow"
category: "Engineering"
doc_type: "reference"
last_updated: "2024-11-01"
owner: "Engineering"
classification: "Internal"
---

# Development Workflow

**Effective Date:** November 1, 2024
**Owner:** Engineering Platform team
**Applies to:** All Acme Corp engineering teams

---

## 1. Branching Strategy

Acme Corp uses a trunk-based development workflow with short-lived feature branches:

- **`main`** is the trunk. It is always in a deployable state. Direct commits to `main` are blocked; all changes go through pull requests.
- **Feature branches** are created from `main` for each unit of work (feature, bug fix, refactor). Branch naming convention: `<type>/<ticket-id>-<short-description>` (e.g., `feat/ENG-1234-add-hybrid-search`, `fix/ENG-5678-null-pointer-export`).
- Feature branches should be short-lived: merge within 2–3 days. Branches open longer than 5 days are flagged in the weekly engineering standup.
- **Long-lived branches** (release branches, hotfix branches) are used only for coordinated releases and emergency fixes. They follow the same review and CI requirements as feature branches.

## 2. Pull Request Workflow

1. Engineer creates a feature branch and implements the change.
2. Engineer opens a pull request against `main`. The PR description must include: what the change does, why it is needed, how to test it, and links to the relevant ticket and design document (if applicable).
3. CI runs automatically on the PR: lint, unit tests, integration tests, and security scanning.
4. A code owner reviews the PR per the Code Review Guidelines.
5. If the change touches security-sensitive areas, additional review is required (see Section 4).
6. Once approved, the PR enters the merge queue. The merge queue rebases onto `main`, runs CI again, and merges if all checks pass.

## 3. CI/CD Pipeline

### 3.1 Continuous Integration

Every pull request triggers the following CI checks:

| Stage | Tool | Purpose | Blocking? |
|---|---|---|---|
| Formatting | ruff format / gofmt / prettier | Code style consistency | Yes |
| Linting | ruff / golangci-lint / eslint | Static analysis, code quality | Yes |
| Unit tests | pytest / go test / jest | Functional correctness | Yes |
| Integration tests | pytest (with test database) | End-to-end path verification | Yes |
| Security scan | Snyk / Dependabot | Dependency vulnerabilities | Yes (critical/high) |
| Coverage check | coverage.py / go tool cover | Minimum 80% line coverage | Yes |

All stages must pass before a PR can be approved and merged. There are no manual overrides for CI failures except during a hotfix (see the Deployment Runbook).

### 3.2 Continuous Deployment

After a PR merges to `main`:

1. The deployment pipeline builds a container image tagged with the commit SHA.
2. The image is pushed to the container registry.
3. The image is deployed to the staging environment automatically.
4. Automated smoke tests run against staging.
5. If smoke tests pass, the deployment proceeds to production via the canary rollout process described in the Deployment Runbook.

Average time from merge to production: 25 minutes (including canary observation).

## 4. Security Review Checkpoint

Certain categories of changes require a mandatory security review by the Information Security (InfoSec) team before the PR can be merged. This checkpoint ensures that security-sensitive changes are evaluated by a specialist in addition to the standard code review.

### 4.1 Changes Requiring Security Review

A security review is required for any PR that modifies:

- **Authentication or authorization logic:** Changes to the Auth Service, API key validation, OAuth flows, permission checks, or session management.
- **Encryption or key management:** Changes to encryption algorithms, key rotation logic, TLS configuration, or secrets management integration (HashiCorp Vault).
- **Data access patterns:** New database queries that access Confidential or Restricted data, new API endpoints that expose PII or PHI, or changes to data export functionality.
- **Infrastructure security:** Changes to firewall rules, network segmentation, VPN configuration, or production access controls.
- **Dependency additions:** Adding a new third-party library that processes sensitive data or runs with elevated privileges.

The PR author is responsible for identifying whether a security review is needed. CI includes a label check: PRs that modify files in designated security-sensitive paths are automatically labeled `security-review-required` and cannot be merged without an approval from a member of the InfoSec team.

### 4.2 Security Review Process

1. The PR is labeled `security-review-required` (automatically or manually).
2. The InfoSec team is notified via the #security-reviews Slack channel.
3. An InfoSec engineer reviews the change within 2 business days. The review focuses on:
   - Compliance with the IT Security Policy (password handling, encryption standards, access control requirements).
   - Adherence to OWASP Top 10 guidelines (injection, broken auth, XSS, etc.).
   - Proper use of security libraries and APIs.
   - Potential for data leakage or privilege escalation.
4. The InfoSec engineer approves, requests changes, or escalates to the InfoSec team lead for complex cases.
5. The PR cannot merge until the security review is resolved.

### 4.3 Interaction with the IT Security Policy

The security review checkpoint is a control required by the IT Security Policy (Section 8 — Vulnerability Management and Patching, and Section 4 — Access Controls). It ensures that changes to security-sensitive code are reviewed by personnel with security expertise, in addition to the functional code review by the service's code owner.

The InfoSec team maintains a list of security-sensitive file paths per repository. This list is updated quarterly and published in the engineering wiki. When a new service is created, the service owner and the InfoSec team jointly define which paths require security review.

## 5. Environments

| Environment | Purpose | Deployment | Data |
|---|---|---|---|
| Local | Developer workstation | Manual (docker-compose) | Synthetic seed data |
| CI | Automated testing | On every PR | Ephemeral test database |
| Staging | Pre-production validation | Automatic on merge to `main` | Anonymized copy of production data (refreshed weekly) |
| Production | Customer-facing | Canary rollout from staging | Real customer data |

Engineers do not have direct write access to the production environment. All production changes go through the CI/CD pipeline and the canary rollout process. Read access to production logs and metrics is available through Datadog and Grafana. Direct database access requires a documented justification and goes through the database proxy with full session recording per the Access Control Policy.

## 6. Hotfix Process

For emergency fixes during an active SEV1 or SEV2 incident:

1. Create a branch from `main`.
2. Implement the fix with a minimal, focused change.
3. Obtain one approval from any available senior engineer (L4+) — the standard code review process is completed retroactively within 24 hours.
4. Merge and deploy directly to production, bypassing the canary observation period if the incident commander approves.
5. Document the hotfix in the incident channel and link it to the postmortem.

## 7. Policy Governance

This workflow is maintained by the Engineering Platform team. Changes are discussed in the biweekly engineering standards review meeting. Questions: eng-standards@acmecorp.com.

---

*Version 2.0 — Last revised November 1, 2024*
