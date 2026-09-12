---
title: "Backup and Recovery Policy"
category: "IT"
doc_type: "policy"
last_updated: "2023-06-01"
owner: "IT Operations"
classification: "Confidential"
---

# Backup and Recovery Policy

**Document ID:** ITSEC-007
**Effective Date:** June 1, 2023
**Applies to:** All Acme Corp production systems, databases, and critical business applications

## 1. Recovery Objectives

| Objective | Target |
|---|---|
| Recovery Point Objective (RPO) | 1 hour — no more than 1 hour of data loss in a disaster scenario |
| Recovery Time Objective (RTO) | 4 hours — systems restored to operational state within 4 hours of a declared disaster |

These targets apply to all Tier 1 (production) and Tier 2 (business-critical) systems. Tier 3 (development, staging) systems have relaxed targets of RPO 24 hours / RTO 24 hours.

## 2. Backup Schedule

| System Tier | Backup Type | Frequency | Retention |
|---|---|---|---|
| Tier 1 (production databases) | Continuous WAL/binlog replication | Real-time | 30 days of point-in-time recovery |
| Tier 1 (production databases) | Full snapshot | Daily at 2:00 AM UTC | 90 days |
| Tier 2 (business apps, file storage) | Incremental | Every 6 hours | 30 days |
| Tier 2 (business apps, file storage) | Full snapshot | Weekly (Sunday 3:00 AM UTC) | 90 days |
| Tier 3 (dev, staging) | Full snapshot | Weekly | 14 days |

All backups are encrypted at rest using AES-256 per the Encryption Standards.

## 3. Backup Storage

- **Primary backups** are stored in a separate availability zone within the same cloud region as the source system.
- **Secondary backups** are replicated to a geographically separate region (minimum 500 miles from the primary region) within 1 hour of creation.
- Backup storage is access-controlled. Only the IT Operations team and designated database administrators have access. Access is logged and reviewed quarterly.

## 4. Recovery Testing

Recovery tests are conducted quarterly to validate that backups are usable and that RTO/RPO targets can be met.

Each quarterly test includes:

- Full restoration of at least one Tier 1 database from backup to an isolated recovery environment.
- Verification of data integrity (row counts, checksums, application-level validation).
- Measurement of actual recovery time against the 4-hour RTO target.
- Documentation of any issues encountered and remediation actions.

Test results are reported to the VP of Engineering and retained for audit purposes. Failed tests are treated as SEV3 incidents per the Incident Response Runbook.

## 5. Disaster Recovery

In the event of a regional outage or catastrophic failure:

1. The incident commander declares a disaster recovery event.
2. IT Operations initiates failover to the secondary region using the secondary backup set.
3. Application teams verify service health in the recovery environment.
4. DNS and load balancer configurations are updated to route traffic to the recovery region.
5. The VP of Engineering authorizes the switch to production traffic.

A full disaster recovery drill is conducted annually in addition to the quarterly backup restoration tests.

## 6. Responsibilities

| Role | Responsibility |
|---|---|
| IT Operations | Configure, monitor, and test backups; execute recovery procedures |
| Database Administrators | Validate database-specific backup integrity; assist with point-in-time recovery |
| System Owners | Classify their systems into the correct tier; validate recovery priorities |
| Information Security | Audit backup encryption and access controls |

## 7. Policy Governance

This policy is reviewed annually by IT Operations and the Information Security team. Questions should be directed to it-ops@acmecorp.com.

---

*Version 1.2 — Last revised June 1, 2023*
