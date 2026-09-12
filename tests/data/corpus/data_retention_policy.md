---
title: "Data Retention Policy"
category: "Compliance"
doc_type: "policy"
last_updated: "2024-01-01"
owner: "Legal"
classification: "Confidential"
---

# Data Retention Policy

**Document ID:** COMP-001
**Effective Date:** January 1, 2024
**Approved by:** Chief Compliance Officer, General Counsel
**Applies to:** All Acme Corp employees, contractors, and systems that process, store, or transmit company or customer data

---

## General Requirements

All customer data must be retained for a minimum of 7 years from the date of the last transaction. This applies to all data categories listed in section 4.2, with the exception of anonymized datasets processed after the effective date of this policy (January 1, 2024).

The 7-year retention requirement covers:

- **Financial records:** Transaction logs, invoices, payment records, revenue recognition data, and audit evidence. Retention is driven by SOX compliance, IRS requirements, and contractual obligations.
- **Customer account data:** Account profiles, subscription history, usage records, and support ticket archives.
- **Contractual records:** Executed agreements, amendments, order forms, and statements of work.
- **Compliance records:** Audit logs, compliance reports, training completion records, and policy acknowledgment receipts.

### Anonymized Data Exception

Anonymized datasets — defined as datasets from which all personally identifiable information (PII) has been irreversibly removed such that no individual can be re-identified — are exempt from the 7-year retention requirement. Anonymized datasets may be retained indefinitely for analytics, research, and product improvement purposes, or deleted at the discretion of the data owner.

The Data Protection Officer must certify that the anonymization process meets the irreversibility standard before a dataset is reclassified as anonymized. Pseudonymized data (where re-identification is possible with a separate key) is NOT considered anonymized and remains subject to the 7-year rule.

### Retention Triggers

The retention clock starts on the date of the last transaction or the last meaningful activity on the record, whichever is later. For customer accounts, "last transaction" means the last subscription payment, the last login, or the contract end date — whichever occurs latest.

If a record is referenced in an active legal hold, audit, or investigation, the retention period is extended until the hold is released, regardless of the standard retention schedule.

---

## EU-Specific Requirements

For customers subject to GDPR, data retention is further constrained by the principle of storage limitation. Personal data may only be retained for as long as necessary for the purpose for which it was collected. The 7-year general requirement applies only to transaction records; personal identification data must be deleted or anonymized within 3 years unless a specific legal basis for longer retention exists.

### What Qualifies as Personal Identification Data

Under this policy, personal identification data includes:

- Name, email address, phone number, mailing address.
- Government-issued identifiers (tax ID, national insurance number) — where collected.
- IP addresses and device identifiers associated with a specific individual.
- Any data that, alone or in combination, can identify a natural person.

### 3-Year Retention Limit

The 3-year limit applies from the date the personal data was last processed for its original purpose. For example:

- A customer's contact information collected during onboarding must be deleted or anonymized within 3 years of the customer's last contract end date.
- Marketing consent records must be retained for the duration of the consent plus 3 years for compliance evidence.

EU customer data stored in the EU-West region is subject to automated retention monitoring. The compliance system flags records approaching the 3-year threshold 90 days in advance, giving the data owner time to confirm deletion or document a lawful basis for continued retention.

### Legal Basis for Extended Retention

Retaining EU personal data beyond 3 years requires a documented legal basis, which must be one of:

- Performance of a contract (active customer relationship).
- Legal obligation (regulatory retention requirement).
- Legitimate interest (documented and balanced against the data subject's rights).

The legal basis must be recorded in the data processing register and reviewed annually by the Data Protection Officer.

---

## Data Deletion Procedures

Upon expiration of the retention period, data must be permanently deleted within 90 calendar days. Deletion must be verified by the Data Protection Officer and logged in the compliance audit trail. Backup copies must be purged within 180 days of the primary deletion.

### Deletion Process

The deletion process consists of four steps:

1. **Identification.** The compliance monitoring system generates a deletion queue of records that have reached the end of their retention period.
2. **Review.** The data owner reviews the queue and confirms that no active legal hold, audit, or contractual obligation requires continued retention.
3. **Execution.** IT executes the deletion across all primary storage systems (production databases, file storage, search indexes). Deletion uses cryptographic erasure where supported (destroying the encryption key for the data segment) or NIST 800-88 compliant media sanitization.
4. **Verification.** The Data Protection Officer verifies that the data has been removed from primary systems and certifies the deletion in the compliance audit trail.

### Backup Purge

Backup copies containing deleted data must be purged within 180 days of the primary deletion. Because backups are typically stored as immutable snapshots, the standard approach is to allow the backup retention cycle to expire naturally (backups are retained for 90 days per the Backup and Recovery Policy). If a specific backup contains Restricted data that has been deleted from primary systems, the backup may be flagged for early expiration.

### Deletion Logging

Every deletion action is logged with:

- Record identifier(s) deleted.
- Date and time of deletion.
- Deletion method (cryptographic erasure, overwrite, physical destruction).
- Name of the person who executed the deletion.
- Name of the Data Protection Officer who verified the deletion.

Deletion logs are retained for 7 years as compliance evidence.

---

## Responsibilities

| Role | Responsibility |
|---|---|
| Data Owner (department head) | Classify data, confirm retention periods, review deletion queues |
| Data Protection Officer | Certify anonymization, verify deletions, review EU retention extensions, maintain the data processing register |
| IT Operations | Execute deletions, manage backup purge cycles, maintain the compliance monitoring system |
| Legal | Advise on legal holds, review retention extensions, maintain the legal hold register |
| Chief Compliance Officer | Approve policy changes, present compliance metrics to the board, oversee audit responses |

---

## Related Documents

- Customer Deletion Workflow — process for deleting customer data upon account termination
- Backup and Recovery Policy — backup retention schedules and recovery procedures
- Data Classification Policy — data classification tiers and handling requirements
- Audit Log Retention — audit log-specific retention (1 year hot, 6 years cold)
- EU Office Data Retention Schedule — EU-specific retention schedule with additional local requirements
- US Office Data Retention Schedule — US-specific overrides for state-law compliance

---

## Policy Governance

This policy is reviewed annually by Legal, the Data Protection Officer, and the Chief Compliance Officer (Jordan Patel). The next scheduled review is January 2025. Questions should be directed to compliance@acmecorp.com.

---

*Document version 3.0 — Last revised January 1, 2024*
