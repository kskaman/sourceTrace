---
title: "Security Advisory Bulletin: Q4 2023"
category: "IT"
doc_type: "advisory"
last_updated: "2023-12-12"
owner: "Information Security"
classification: "Confidential"
---

# Security Advisory Bulletin: Q4 2023

**Document ID:** ITSEC-ADV-2023-Q4
**Published:** December 12, 2023
**Audience:** Engineering, Platform, SRE, Security Engineering
**Classification:** Confidential

## Overview

This bulletin summarizes the high-priority advisories the InfoSec team has triaged during Q4 2023. Each entry includes the affected component, Acme Corp's exposure, the remediation status, and any residual risk.

## CVE-2023-6612 — Apache Kafka Broker Authorization Bypass

- **Severity:** High (CVSS 8.1)
- **Disclosed:** October 17, 2023
- **Affected component:** Apache Kafka 3.4.x–3.5.1, event streaming platform
- **Fixed in:** Kafka 3.5.2
- **Owner:** Data Platform team

### Affected systems at Acme Corp

CVE-2023-6612 affects Acme Corp's internal event streaming cluster used for audit log delivery, billing events, and real-time analytics pipelines. A malformed SASL GSSAPI handshake can bypass ACL enforcement, allowing an authenticated broker client to produce or consume topics outside its permitted scope.

### Remediation status

- **Production:** Patched on October 20, 2023.
- **Non-production:** Patched on October 21, 2023.
- **Customer impact:** No customer-facing APIs use Kafka directly. No evidence of exploitation.

### Residual risk

None. ACL audit completed post-patch; no unauthorized topic access detected in broker logs.

## CVE-2023-5189 — Terraform Provider AWS Credential Exposure

- **Severity:** Medium (CVSS 6.8)
- **Disclosed:** November 3, 2023
- **Affected component:** Terraform AWS provider, versions 5.0.0–5.21.0
- **Fixed in:** AWS provider 5.22.0
- **Owner:** Infrastructure team (DevOps)

Under specific plan output configurations, sensitive resource attributes could be written to Terraform state in plaintext. Acme Corp stores Terraform state in an encrypted S3 backend with access restricted to CI/CD service accounts. No credentials were exposed. Provider upgrade completed as part of the November infrastructure tooling refresh.

## CVE-2023-4477 — OpenTelemetry Collector Memory Exhaustion

- **Severity:** Low (CVSS 3.9)
- **Disclosed:** September 28, 2023
- **Affected component:** OpenTelemetry Collector, versions 0.85.x–0.87.x
- **Fixed in:** OpenTelemetry Collector 0.88.0
- **Owner:** Observability team

A malformed OTLP export payload can cause unbounded memory growth in the collector process. Acme Corp's collector instances accept traffic only from internal services over mTLS; external payloads cannot reach the OTLP endpoint. Upgraded as part of the Q4 observability stack release.

## Questions

Direct all questions about this bulletin to security@acmecorp.com or post in the #infosec-questions Slack channel.

---

*InfoSec Bulletin 2023-Q4. Next update: March 2024.*
