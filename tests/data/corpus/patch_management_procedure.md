---
title: "Patch Management Procedure"
category: "IT"
doc_type: "procedure"
last_updated: "2024-02-01"
owner: "IT Operations"
classification: "Internal"
---

# Patch Management Procedure

**Effective Date:** February 1, 2024
**Applies to:** All Acme Corp-managed systems (servers, workstations, network devices, cloud infrastructure)

## 1. Patch Cadence

Security and software patches are applied according to the following schedule based on severity:

| Severity | CVSS Range | Deadline | Deployment Method |
|---|---|---|---|
| Critical | 9.0–10.0 | 7 days from availability | Emergency change; may deploy outside maintenance window |
| High | 7.0–8.9 | 30 days from availability | Scheduled during next maintenance window |
| Medium | 4.0–6.9 | Monthly patch window | Deployed in the monthly maintenance cycle (second Tuesday) |
| Low | Below 4.0 | Quarterly patch cycle | Deployed in the quarterly maintenance cycle (first Saturday of Jan, Apr, Jul, Oct) |

## 2. Maintenance Windows

- **Weekly:** Wednesday 2:00–4:00 AM UTC for critical and high patches.
- **Monthly:** Second Tuesday, 2:00–6:00 AM UTC for routine patches.
- **Quarterly:** First Saturday of each quarter, 12:00–8:00 AM UTC for cumulative updates and firmware.

All maintenance windows are communicated to affected teams at least 48 hours in advance via the #ops-maintenance Slack channel.

## 3. Process

1. **Identification:** IT Operations monitors vendor advisories, NVD feeds, and automated scanning results for new patches.
2. **Assessment:** Each patch is assessed for applicability and severity against the Acme Corp environment.
3. **Testing:** Patches are deployed to the staging environment and validated for 24 hours (critical) or 72 hours (all others) before production deployment.
4. **Deployment:** Patches are rolled out to production per the cadence above. Automated deployment tools handle workstation patches; server patches are deployed by the infrastructure team.
5. **Verification:** Post-deployment verification confirms that patched systems are functioning correctly and the vulnerability is remediated.
6. **Documentation:** Patch deployment is logged in the change management system with the patch ID, affected systems, deployment date, and verification status.

## 4. Exceptions

If a patch cannot be applied within the defined deadline (e.g., compatibility issue, business-critical system freeze), the system owner must submit a Security Exception Request per the Vulnerability Management Policy. Compensating controls are required until the patch is applied.

## 5. Endpoint Patching

Company-managed laptops and workstations receive OS and application patches automatically. Employees must restart their devices within 48 hours of a pending critical update. IT may force a restart after 72 hours with 1-hour advance notification.

## 6. Policy Governance

This procedure is maintained by IT Operations in coordination with the Information Security team. Questions should be directed to it-ops@acmecorp.com.

---

*Version 1.3 — Last revised February 1, 2024*
