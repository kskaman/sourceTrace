---
title: "Vendor Management Policy"
category: "Operations"
doc_type: "policy"
last_updated: "2024-04-01"
owner: "Legal"
classification: "Confidential"
---

# Vendor Management Policy

**Effective Date:** April 1, 2024
**Applies to:** All Acme Corp departments that engage third-party vendors, service providers, or sub-processors

## 1. Vendor Onboarding

Before engaging a new vendor, the sponsoring department must complete the vendor onboarding process:

1. **Business justification.** The sponsoring team submits a vendor request form describing the business need, estimated annual spend, and the type of data the vendor will access (if any).
2. **Security review.** The Information Security team conducts a risk assessment based on the vendor's SOC 2 report (or equivalent), data handling practices, and incident history. Vendors accessing Confidential or Restricted data require a full security questionnaire and evidence review. Target turnaround: 10 business days.
3. **Legal review.** Legal reviews the vendor's contract terms, including liability clauses, indemnification, termination provisions, and compliance with applicable regulations.
4. **Data processing agreement.** Vendors that process personal data on behalf of Acme Corp or its customers must execute a Data Processing Agreement (DPA) before any data is shared. The DPA template is maintained by Legal (see the Data Processing Agreement Template).
5. **Approval.** Vendor onboarding requires sign-off from the sponsoring department head and, for annual spend above $50,000, the CFO.

## 2. Restrictions on Third-Party Data Sharing

Acme Corp restricts the sharing of data with third-party vendors as follows:

- **Minimum necessary.** Only the minimum data necessary for the vendor to perform their contracted services may be shared. Bulk data exports to vendors are prohibited unless explicitly approved in the DPA.
- **No onward sharing.** Vendors may not share Acme Corp data with sub-processors unless the sub-processor is listed in the DPA and Acme Corp has provided written consent. Unauthorized sub-processing is grounds for immediate contract termination.
- **Restricted data.** Personally identifiable information (PII), protected health information (PHI), and financial data classified as Restricted may only be shared with vendors who have completed a full security review, executed a DPA, and (for PHI) signed a HIPAA Business Associate Agreement.
- **No use for vendor's own purposes.** Vendors may not use Acme Corp data for product development, analytics, model training, benchmarking, or any purpose other than fulfilling the contracted scope of work.
- **Encryption in transit.** All data shared with vendors must be encrypted in transit using TLS 1.3. Data shared via file transfer must use the company's secure file exchange portal; email attachments are not an approved transfer method for Confidential or Restricted data.
- **Return or destruction.** Upon contract termination, the vendor must return or certifiably destroy all Acme Corp data within 30 days. Destruction certificates are retained by Legal for 7 years.

## 3. Ongoing Monitoring

Active vendors are monitored on a recurring basis:

| Vendor Tier | Review Frequency | Review Scope |
|---|---|---|
| Critical (access to Restricted data or core infrastructure) | Annually | Full security reassessment, DPA compliance audit, sub-processor list review |
| Standard (access to Confidential data) | Every 2 years | Security questionnaire update, contract compliance check |
| Low-risk (no data access or Public data only) | Every 3 years | Contract renewal review |

The Information Security team maintains the vendor registry and tracks review due dates. Vendors that fail a review are placed on a remediation plan with a 60-day deadline; failure to remediate results in contract termination.

## 4. Vendor Offboarding

When a vendor engagement ends:

1. The sponsoring department notifies Legal and IT at least 30 days before the contract end date.
2. The vendor returns or destroys all Acme Corp data per the DPA terms.
3. IT revokes the vendor's access to all systems.
4. Legal confirms receipt of the data destruction certificate.
5. The vendor is marked as inactive in the vendor registry.

## 5. Policy Governance

This policy is administered by Legal in coordination with Information Security and Finance. Questions should be directed to legal@acmecorp.com.

---

*Version 2.0 — Last revised April 1, 2024*
