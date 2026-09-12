---
title: "Code Review Guidelines"
category: "Engineering"
doc_type: "guide"
last_updated: "2024-09-01"
owner: "Engineering"
classification: "Internal"
---

# Code Review Guidelines

**Effective Date:** September 1, 2024
**Owner:** Engineering Platform team
**Applies to:** All Acme Corp engineers submitting or reviewing code changes

---

## 1. When a Review Is Required

All changes to production code, infrastructure configuration, and CI/CD pipelines require at least one approving review before merge. This includes:

- Application code (Python, Go, TypeScript).
- Database migrations.
- Terraform and infrastructure-as-code changes.
- CI/CD pipeline definitions (GitHub Actions workflows).
- Configuration changes that affect production behavior (feature flags, environment variables).

Exceptions: documentation-only changes (README updates, inline comment fixes) may be merged without review by the file's code owner, unless the change touches a runbook or API contract.

## 2. Approval Rules

| Change Type | Required Approvals | Who Can Approve |
|---|---|---|
| Standard code change | 1 | Any code owner for the affected files |
| Database migration | 2 | 1 code owner + 1 database administrator |
| Security-sensitive change (auth, encryption, access control) | 2 | 1 code owner + 1 member of the InfoSec team |
| Infrastructure / Terraform | 2 | 1 code owner + 1 member of the Platform team |
| CI/CD pipeline change | 1 | Code owner for `.github/workflows/` |

Code owners are defined in the `CODEOWNERS` file at the root of each repository.

## 3. Review Expectations

### 3.1 For Reviewers

- **Respond within 1 business day.** If you cannot review within that window, reassign or comment that you need more time. Stale PRs block the author and the team.
- **Read the PR description first.** Understand what the change is trying to accomplish before reading the code.
- **Distinguish blocking from non-blocking feedback:**
  - **Blocking:** correctness bugs, security issues, missing tests for new logic, data loss risk, API contract violations. These must be resolved before merge.
  - **Non-blocking (nit):** style preferences not enforced by the linter, alternative approaches that are equivalent in quality, minor naming suggestions. Prefix with `nit:` so the author knows it is optional.
- **Be specific.** "This is confusing" is not actionable. "This function does three things — consider splitting into X and Y" is.
- **Approve when satisfied.** Do not withhold approval over nits. If the only remaining feedback is non-blocking, approve with comments.

### 3.2 For Authors

- **Keep PRs small.** Target fewer than 400 lines of changed code. PRs over 400 lines take disproportionately longer to review and have a higher defect escape rate. If a change is inherently large, break it into stacked PRs with clear dependency order.
- **Write a useful PR description.** Include: what the change does, why it is needed, how to test it, and any risks or trade-offs. Link to the relevant ticket or design document.
- **Self-review before requesting review.** Read the diff yourself as if you were the reviewer. Catch obvious issues before consuming someone else's time.
- **Respond to all comments.** Resolve blocking feedback with a code change. Acknowledge non-blocking feedback with a reply (even "noted, will address in a follow-up" is fine). Do not leave comments unaddressed.
- **Do not merge your own PR.** The reviewer who approves clicks merge, not the author. This ensures a second pair of eyes has signed off.

## 4. Merge Queue

Acme Corp uses a merge queue (GitHub merge queue) for all production repositories:

1. When a PR is approved, the author adds it to the merge queue by clicking **Merge when ready**.
2. The merge queue rebases the PR onto the latest `main`, runs the full CI suite (lint, unit tests, integration tests), and merges only if all checks pass.
3. If CI fails after rebase, the PR is ejected from the queue and the author is notified.
4. PRs in the queue are processed in order. Do not force-merge or bypass the queue.

The merge queue prevents broken `main` by ensuring every merged commit has passed CI against the true head of the branch.

## 5. Special Cases

### 5.1 Hotfixes

Emergency production fixes (during an active SEV1 or SEV2 incident) may be merged with a single approval from any available senior engineer (L4+). The standard review process must be completed retroactively within 24 hours of the hotfix merge.

### 5.2 Reverts

Reverts of a recently merged change may be merged with a single approval from any engineer, regardless of code ownership, to unblock the team quickly. The original author and reviewer are notified.

### 5.3 Refactors

Large refactoring PRs that change many files without changing behavior should include before/after test results demonstrating that behavior is preserved. Reviewers focus on correctness of the transformation rather than line-by-line logic review.

## 6. Anti-Patterns

Avoid these common review anti-patterns:

- **Rubber-stamping:** Approving without reading the code. If you do not have time, say so.
- **Bikeshedding:** Extended debate over trivial style choices already covered by the linter. Defer to the automated tooling.
- **Gatekeeping:** Blocking a PR over an architectural preference when the author's approach is correct and passes tests. Raise architectural concerns in design reviews, not code reviews.
- **Silent disapproval:** Requesting changes without explaining why. Every request for changes must include a justification.

## 7. Policy Governance

These guidelines are maintained by the Engineering Platform team. Proposed changes are discussed in the biweekly engineering standards review meeting. Questions should be directed to eng-standards@acmecorp.com.

---

*Version 2.0 — Last revised September 1, 2024*
