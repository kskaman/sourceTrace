---
title: "Security Advisory Bulletin: Q1 2024"
category: "IT"
doc_type: "advisory"
last_updated: "2024-03-10"
owner: "Information Security"
classification: "Confidential"
---

# Security Advisory Bulletin: Q1 2024

**Document ID:** ITSEC-ADV-2024-Q1
**Published:** March 10, 2024
**Audience:** Engineering, Platform, SRE, Security Engineering
**Classification:** Confidential

## Overview

This bulletin summarizes the high-priority advisories the InfoSec team has triaged during Q1 2024. Each entry includes the affected component, Acme Corp's exposure, the remediation status, and any residual risk. System owners listed are accountable for verifying that the patched build is running in their production environment.

## CVE-2024-1234 — OAuth 2.0 Token Handler Credential Replay

- **Severity:** High (CVSS 8.2)
- **Disclosed:** February 3, 2024
- **Affected component:** Authentication service, OAuth 2.0 authorization code flow, versions 4.1.x through 4.3.2
- **Fixed in:** Authentication service 4.3.3
- **Owner:** Platform Security team (on-call: security-oncall@acmecorp.com)

### Affected systems at Acme Corp

CVE-2024-1234 affects the OAuth 2.0 refresh token validation logic in the authentication service. At Acme Corp, this service issues access tokens for:

- Customer-facing dashboard (app.acmecorp.com)
- Admin console (admin.acmecorp.com)
- Partner API integrations authenticated via OAuth 2.0 authorization code flow

Server-to-server API integrations that use API keys (rather than OAuth) are **not** affected. The on-premises enterprise deployment is **not** affected because it uses a different authentication stack.

### Description

A malformed refresh token can, under specific network conditions involving out-of-order delivery of token endpoint responses, allow replay of expired credentials against the token endpoint. An attacker who has already obtained a valid but expired refresh token could exchange it for a new access token beyond its intended lifetime. The vulnerability does not allow token forgery or privilege escalation.

### Remediation status

- **Production:** Patched on February 5, 2024 (48 hours after disclosure, within the Critical remediation SLA from the Vulnerability Management Policy).
- **Staging and non-production:** Patched on February 7, 2024.
- **Customer impact:** No evidence of exploitation. Audit log review for the 14 days preceding the patch showed no anomalous token exchange patterns.
- **Disclosure:** Customers on the enterprise SSO plan were notified through the standard security bulletin on February 6, 2024.

### Residual risk

None. The patched version enforces strict token expiry checks at the validation layer and rejects out-of-order refresh token exchanges.

## CVE-2024-0987 — PostgreSQL 15.x Internal Admin Tooling

- **Severity:** Critical (CVSS 9.4)
- **Disclosed:** January 18, 2024
- **Affected component:** Internal PostgreSQL admin tooling running PostgreSQL 15.3–15.5
- **Fixed in:** PostgreSQL 15.6
- **Owner:** Database team

Acme Corp's customer-facing database is **not** affected; this CVE only impacts internal admin tooling used by the Database team for schema migrations and capacity planning. Emergency patch deployed on January 19, 2024. The affected tooling is monitored for 14 days post-patch.

## CVE-2023-8472 — Internal Logging Library

- **Severity:** Medium (CVSS 5.6)
- **Disclosed:** December 2023
- **Affected component:** Internal structured logging library used across platform services
- **Fixed in:** Pending; vendor patch expected Q2 2024
- **Owner:** Platform team

A Security Exception Request has been approved because the library is deeply embedded in internal services and an upgrade requires coordinated rollout. Compensating controls: log sink is network-isolated, and logs do not contain user-supplied content on the vulnerable code path. Target remediation: Q2 2024.

## Questions

Direct all questions about this bulletin to security@acmecorp.com or post in the #infosec-questions Slack channel.

---

*InfoSec Bulletin 2024-Q1. Next update: June 2024.*
