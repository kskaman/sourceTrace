---
title: "Security Advisory Bulletin: Q3 2024"
category: "IT"
doc_type: "advisory"
last_updated: "2024-09-10"
owner: "Information Security"
classification: "Confidential"
---

# Security Advisory Bulletin: Q3 2024

**Document ID:** ITSEC-ADV-2024-Q3
**Published:** September 10, 2024
**Audience:** Engineering, Platform, SRE, Security Engineering
**Classification:** Confidential

## Overview

This bulletin summarizes the high-priority advisories the InfoSec team has triaged during Q3 2024. Each entry includes the affected component, Acme Corp's exposure, the remediation status, and any residual risk.

## CVE-2024-7743 — Elasticsearch Improper Access Control

- **Severity:** Critical (CVSS 9.1)
- **Disclosed:** July 22, 2024
- **Affected component:** Elasticsearch 8.x before 8.14.2, used in Acme Corp's internal search service
- **Fixed in:** Elasticsearch 8.14.2
- **Owner:** Search Infrastructure team

### Affected systems at Acme Corp

CVE-2024-7743 affects Acme Corp's internal document search service, which indexes support tickets, internal wikis, and engineering runbooks. A specially crafted query can bypass field-level security and expose documents outside the requesting user's permission scope. Customer-facing search is not affected; it uses a separate managed service.

### Remediation status

- **Production:** Patched on July 24, 2024.
- **Non-production:** Patched on July 25, 2024.
- **Customer impact:** No customer data is stored in the affected service. No evidence of exploitation.

### Residual risk

None. Field-level security configuration has been reviewed and tightened post-patch.

## CVE-2024-6218 — Redis Unauthenticated Command Injection

- **Severity:** High (CVSS 8.0)
- **Disclosed:** August 5, 2024
- **Affected component:** Redis 7.0.x before 7.0.13, session cache layer
- **Fixed in:** Redis 7.0.13
- **Owner:** Caching Infrastructure team

Acme Corp's session cache uses Redis 7.0.x to store short-lived user session tokens. An attacker with network access to the Redis port could inject arbitrary commands. The Redis instance is not directly reachable from the internet; access is restricted to the internal VPC. Patched on August 8, 2024. Network segmentation review confirmed no external exposure.

## CVE-2024-5501 — Python Cryptography Library Key Derivation

- **Severity:** Medium (CVSS 5.8)
- **Disclosed:** June 30, 2024
- **Affected component:** Python cryptography library, versions 42.0.0–42.0.5
- **Fixed in:** cryptography 42.0.6
- **Owner:** API Platform team

Affects PBKDF2 key derivation under specific parameter combinations not used in Acme Corp's primary password hashing flow. A Security Exception Request was reviewed and closed — the vulnerable code path is not exercised. Library upgrade is included in the Q4 2024 dependency refresh.

## Questions

Direct all questions about this bulletin to security@acmecorp.com or post in the #infosec-questions Slack channel.

---

*InfoSec Bulletin 2024-Q3. Next update: December 2024.*
