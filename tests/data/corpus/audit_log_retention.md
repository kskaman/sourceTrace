---
title: "Audit Log Retention"
category: "IT"
doc_type: "policy"
last_updated: "2024-01-01"
owner: "Information Security"
classification: "Confidential"
---

# Audit Log Retention

**Document ID:** ITSEC-009
**Effective Date:** January 1, 2024
**Applies to:** All Acme Corp systems that generate audit logs

## 1. Retention Schedule

Audit logs are retained in two tiers:

| Storage Tier | Duration | Access | SLA |
|---|---|---|---|
| Hot storage (indexed, searchable) | 1 year | Real-time query via the SIEM and log management platform | Sub-second search response |
| Cold storage (archived) | 6 years | Retrievable within 72 hours upon request to IT Operations | 72-hour retrieval SLA |

Total retention is 7 years from the date the log entry was created. This meets the requirements of SOC 2, HIPAA, and Acme Corp's general data retention policy of 7 years for business records.

## 2. What Is Logged

All systems handling Confidential or Restricted data must generate audit logs capturing:

| Event Category | Fields Captured |
|---|---|
| Authentication | Timestamp (UTC), user ID, source IP, authentication method, success/failure |
| Authorization | Timestamp, user ID, resource requested, permission checked, granted/denied |
| Data access | Timestamp, user ID, source IP, operation (read/write/delete), record or resource identifier |
| Administrative actions | Timestamp, admin user ID, action performed, target system/configuration, before/after values |
| System events | Timestamp, system identifier, event type (startup, shutdown, error, configuration change) |

Logs for Internal-tier systems must capture authentication and administrative actions at a minimum. Logging for Public-tier systems is optional.

## 3. Log Integrity

- Logs are written to append-only storage. Log entries cannot be modified or deleted by the system or users whose activity they record.
- Logs are forwarded from source systems to the centralized logging infrastructure within 60 seconds of generation.
- The logging infrastructure resides in the management network zone, isolated from production and corporate zones.
- Log integrity is verified daily via checksum comparison between source and centralized copies.

## 4. Access to Audit Logs

Access to audit logs is restricted:

| Role | Access |
|---|---|
| Information Security | Full read access for investigation and monitoring |
| IT Operations | Read access for operational troubleshooting (hot storage only) |
| Data Protection Officer | Read access for compliance audits |
| Legal | Access upon documented request tied to litigation hold or regulatory inquiry |
| System Owners | Read access to logs for their own systems (hot storage only) |

No role has the ability to modify or delete audit log entries.

## 5. Retention Justification

The 7-year total retention period is driven by:

- **SOC 2 Type II:** Requires evidence of continuous control operation; audit logs are primary evidence for access control and change management controls.
- **HIPAA:** Requires retention of security-related documentation for 6 years from the date of creation or the date it was last in effect.
- **Acme Corp Data Retention Policy:** General business records are retained for 7 years.
- **Incident investigation:** Historical logs are frequently needed for root cause analysis of security incidents with delayed detection.

## 6. Disposal

After 7 years, audit logs are permanently deleted using cryptographic erasure (destroying the encryption keys for the archived log volumes). Deletion is logged in the data disposal register and confirmed by the Information Security team.

## 7. Policy Governance

This policy is maintained by the Information Security team. Questions should be directed to security@acmecorp.com.

---

*Version 1.1 — Last revised January 1, 2024*
