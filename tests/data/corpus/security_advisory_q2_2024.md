---
title: "Security Advisory Bulletin: Q2 2024"
category: "IT"
doc_type: "advisory"
last_updated: "2024-06-14"
owner: "Information Security"
classification: "Confidential"
---

# Security Advisory Bulletin: Q2 2024

**Document ID:** ITSEC-ADV-2024-Q2
**Published:** June 14, 2024
**Audience:** Engineering, Platform, SRE, Security Engineering
**Classification:** Confidential

## Overview

This bulletin summarizes the high-priority advisories the InfoSec team has triaged during Q2 2024. Each entry includes the affected component, Acme Corp's exposure, the remediation status, and any residual risk.

## CVE-2024-3871 — Container Runtime Privilege Escalation

- **Severity:** High (CVSS 8.6)
- **Disclosed:** April 9, 2024
- **Affected component:** Container runtime (containerd 1.6.x–1.7.4)
- **Fixed in:** containerd 1.7.5
- **Owner:** Platform Infrastructure team

### Affected systems at Acme Corp

CVE-2024-3871 affects the container runtime used across Acme Corp's Kubernetes worker nodes. A malicious container image with crafted mount options can escape the container sandbox and gain elevated access on the host. All production Kubernetes nodes running containerd 1.6.x or 1.7.x before 1.7.5 are in scope.

### Remediation status

- **Production:** Patched on April 11, 2024.
- **Non-production:** Patched on April 13, 2024.
- **Customer impact:** No evidence of exploitation. Image provenance controls (registry allowlist) limit exposure to first-party images only.

### Residual risk

None. All nodes have been patched and verified. Image signing enforcement is being evaluated as an additional compensating control.

## CVE-2024-4102 — Nginx HTTP/2 Header Parsing

- **Severity:** Medium (CVSS 6.3)
- **Disclosed:** May 2, 2024
- **Affected component:** Nginx reverse proxy, versions 1.24.0–1.25.2
- **Fixed in:** Nginx 1.25.3
- **Owner:** Platform Networking team

Acme Corp's edge load balancers use the affected Nginx versions. A malformed HTTP/2 HPACK header can cause a worker process to crash, resulting in brief request drops. No memory disclosure or code execution is possible. Patched on May 6, 2024 during the next scheduled maintenance window.

## CVE-2024-2987 — Go Standard Library net/http

- **Severity:** Low (CVSS 4.1)
- **Disclosed:** March 18, 2024
- **Affected component:** Go standard library net/http, versions before Go 1.22.2
- **Fixed in:** Go 1.22.2
- **Owner:** Engineering (all Go services)

Affects request smuggling under specific reverse-proxy configurations. Acme Corp's edge terminates HTTP/2 and forwards HTTP/1.1 internally, which mitigates the primary attack vector. Go toolchain upgrade to 1.22.3 is tracked in the Q2 2024 toolchain refresh milestone.

## Questions

Direct all questions about this bulletin to security@acmecorp.com or post in the #infosec-questions Slack channel.

---

*InfoSec Bulletin 2024-Q2. Next update: September 2024.*
