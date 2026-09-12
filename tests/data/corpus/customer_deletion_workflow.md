---
title: "Customer Deletion Workflow"
category: "Compliance"
doc_type: "procedure"
last_updated: "2024-09-01"
owner: "Legal"
classification: "Confidential"
---

# Customer Deletion Workflow

**Document ID:** COMP-002
**Effective Date:** September 1, 2024
**Approved by:** General Counsel, Data Protection Officer
**Applies to:** All customer account terminations (voluntary churn, contract expiration, non-renewal, and termination for cause)

---

## 1. Purpose

This workflow defines the process for deleting customer data when a customer terminates their account with Acme Corp. It ensures that all customer data — including production data, backups, and archives — is removed from Acme Corp systems within the required timeframe.

## 2. Scope and Deletion Commitment

When a customer terminates their account, ALL customer data is deleted within 90 days of the termination notice. This applies to:

- Production databases (account records, usage data, configuration, uploaded content).
- Search indexes and vector stores.
- Log entries containing customer-identifiable information.
- Backup snapshots that include the customer's data.
- Data replicas in secondary regions (e.g., EU-West).
- Cached data in CDN and application caches.
- Data held by sub-processors on Acme Corp's behalf (see Section 5).

The 90-day deletion window begins on the date Acme Corp receives written termination notice from the customer, or on the contract end date, whichever is earlier.

## 3. Pre-Deletion Steps

Before deletion begins, the following steps are completed:

1. **Termination confirmation.** Customer Success confirms that the customer intends to terminate and that the termination is not a billing dispute or temporary suspension.
2. **Data export offer.** The customer is offered a data export in JSON or CSV format. The export must be requested within 30 days of the termination notice. Exports are delivered within 10 business days.
3. **Final invoice.** Finance issues the final invoice and confirms that all outstanding payments are settled or written off.
4. **Legal hold check.** Legal confirms whether any litigation hold or regulatory investigation requires data preservation. If a hold exists, deletion is paused for the affected data until the hold is released.

## 4. Deletion Process

| Step | Owner | Timeline |
|---|---|---|
| Disable customer account access | IT Operations | Within 24 hours of termination confirmation |
| Delete production data (databases, file storage, search indexes) | IT Operations | Within 30 days |
| Purge data from application caches and CDN | IT Operations | Within 7 days |
| Remove customer-identifiable entries from application logs | Data Engineering | Within 60 days |
| Purge backup snapshots containing customer data | IT Operations | Within 90 days |
| Confirm deletion with sub-processors | Legal | Within 90 days |
| Data Protection Officer certifies deletion | DPO | Within 90 days |

### Deletion Methods

- **Production databases:** Targeted row-level deletion with verification query confirming zero remaining rows for the customer ID.
- **File storage and object storage:** Object deletion with versioning cleanup.
- **Backup snapshots:** Because backups are stored as immutable snapshots, individual customer data cannot be surgically removed. Backup snapshots are retained for their standard 90-day lifecycle per the Backup and Recovery Policy. Snapshots older than 90 days that have not yet expired at the time of the deletion request are flagged for priority expiration.
- **Search indexes:** Customer documents are removed from the index and the index is rebuilt or compacted to ensure deleted content is not retrievable.
- **Sub-processor data:** See Section 5.

## 5. Sub-Processor Deletion

Acme Corp uses sub-processors that may hold customer data (cloud infrastructure providers, analytics services, communication platforms). Upon customer termination:

1. Legal sends a deletion request to each sub-processor that processed data for the terminated customer.
2. Sub-processors must confirm deletion within 30 days of the request per the terms of their Data Processing Agreement.
3. Deletion confirmations are collected and retained by Legal.

The list of active sub-processors is maintained in the Data Processing Agreement Template and updated quarterly.

## 6. Verification and Certification

After all deletion steps are complete, the Data Protection Officer:

1. Reviews the deletion log for completeness (all systems, all regions, all sub-processors).
2. Runs a verification query against production databases and search indexes to confirm zero results for the customer ID.
3. Issues a Deletion Certificate documenting the customer name, account ID, termination date, deletion completion date, and systems covered.

The Deletion Certificate is retained for 7 years as compliance evidence.

## 7. Exceptions

- **Legal holds:** If a legal hold is in effect for any portion of the customer's data, that data is preserved until the hold is released. All other customer data is deleted on schedule. The customer is notified that a hold is delaying partial deletion (without disclosing the nature of the hold, unless required by law).
- **Aggregated and anonymized data:** Data that has been irreversibly anonymized and aggregated (e.g., usage statistics that cannot be attributed to a specific customer) is not subject to this workflow. See the Data Retention Policy for the anonymized data exception.
- **Regulatory retention:** If a specific regulation requires Acme Corp to retain certain customer records beyond 90 days (e.g., financial transaction records under tax law), those records are retained for the minimum required period and then deleted. This exception must be documented and approved by Legal.

## 8. Relationship to the Data Retention Policy

This workflow operates independently of the general Data Retention Policy, which specifies a 7-year retention period for customer data. The Data Retention Policy governs how long data is retained during an active customer relationship. This workflow governs what happens after the relationship ends.

When a customer terminates, the deletion commitment in this workflow takes precedence: all customer data is deleted within 90 days, regardless of where the data sits in its retention lifecycle under the general policy.

## 9. Policy Governance

This workflow is maintained by Legal in coordination with the Data Protection Officer and IT Operations. Questions should be directed to legal@acmecorp.com.

---

*Version 2.0 — Last revised September 1, 2024*
