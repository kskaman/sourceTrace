---
title: "Data Classification Policy"
category: "IT"
doc_type: "policy"
last_updated: "2023-05-01"
owner: "Information Security"
classification: "Internal"
---

# Data Classification Policy

**Document ID:** ITSEC-002
**Effective Date:** May 1, 2023
**Approved by:** VP of Engineering, Chief Compliance Officer
**Classification:** Internal

## 1. Purpose

This policy establishes a framework for classifying all data processed, stored, or transmitted by Acme Corp. Proper classification ensures that data receives handling protections appropriate to its sensitivity and regulatory requirements.

## 2. Classification Tiers

All Acme Corp data falls into one of four tiers:

### Tier 1 — Public

Information approved for external distribution with no restrictions.

**Examples:** Marketing materials, published API documentation, press releases, open-source code, public job postings.

**Handling:** No special controls required. May be shared freely.

### Tier 2 — Internal

Non-sensitive information intended for employee use. Disclosure outside Acme Corp would not cause material harm but is not authorized without approval.

**Examples:** Internal announcements, team wiki pages, meeting notes, org charts, internal training materials.

**Handling:**
- Store on company-managed systems.
- Encryption in transit required (TLS 1.2 or higher).
- Do not post to public channels or personal accounts.

### Tier 3 — Confidential

Sensitive business information whose unauthorized disclosure could harm the company, its customers, or its partners.

**Examples:** Financial reports, customer lists, pricing strategy, source code, product roadmaps, vendor contracts, employee compensation data.

**Handling:**
- Encryption at rest required.
- Encryption in transit required (TLS 1.3).
- Access restricted to employees with a documented business need.
- Access logging required.
- External sharing requires NDA and VP approval.
- Must not be stored on personal devices unless enrolled in the MDM program.

### Tier 4 — Restricted

Highly sensitive information subject to regulatory, legal, or contractual obligations. Unauthorized disclosure could result in regulatory penalties, legal liability, or significant harm to individuals.

**Examples:** Personally identifiable information (PII), protected health information (PHI), credentials and encryption keys, security audit results, penetration test reports, data breach investigation records.

**Handling:**
- Encryption at rest required (AES-256).
- Encryption in transit required (TLS 1.3).
- Access controlled by the system owner and the Data Protection Officer.
- Immutable audit trail for all access events.
- External sharing prohibited without review and approval by Legal.
- Must not be stored on removable media.
- Must not be printed unless operationally necessary, and printed copies must be secured or shredded.

## 3. Classification Responsibilities

| Role | Responsibility |
|---|---|
| Data creator | Assign an initial classification at the time of creation. |
| System owner | Ensure that systems enforce the handling requirements for the highest classification of data they process. |
| Information Security | Maintain this policy, conduct classification audits, and advise on edge cases. |
| All employees | Handle data according to its classification. When in doubt, treat data as Confidential until clarified. |

## 4. Reclassification

Data classification may change over time. Common triggers for reclassification include:

- A previously Confidential document is approved for public release (Confidential → Public).
- Customer data that was anonymized and aggregated is no longer Restricted (Restricted → Internal).
- A document marked Internal contains a newly added customer name (Internal → Confidential).

Reclassification requests are submitted to the InfoSec team through the IT portal. The system owner and InfoSec review the request within 5 business days.

## 5. Labeling

Documents classified as Confidential or Restricted should include the classification label in the document header or footer. Electronic files should include the classification in the file metadata where supported.

Labeling is recommended but not required for Internal documents.

## 6. Policy Governance

This policy is reviewed annually by the Information Security team. Questions should be directed to security@acmecorp.com.

---

*Version 1.2 — Last revised May 1, 2023*
