---
title: "Cross-Border Data Transfer Mechanisms"
category: "Compliance"
doc_type: "reference"
last_updated: "2024-10-01"
owner: "Legal"
classification: "Confidential"
---

# Cross-Border Data Transfer Mechanisms

**Effective Date:** October 1, 2024
**Approved by:** General Counsel, Data Protection Officer (Mariana Costa)
**Applies to:** All transfers of personal data from the European Economic Area (EEA) or United Kingdom to countries without an adequacy decision

---

## 1. Overview

Acme Corp is headquartered in the United States and operates cloud infrastructure in two regions: US-East (primary) and EU-West. When personal data originating in the EEA or UK is transferred to or processed in the US, Acme Corp must ensure that appropriate safeguards are in place to provide an essentially equivalent level of data protection.

This document describes the transfer mechanisms Acme Corp relies on and the supplementary measures implemented to address transfer risks.

## 2. Primary Transfer Mechanism: Standard Contractual Clauses (SCCs)

Acme Corp relies on Standard Contractual Clauses adopted by the European Commission (Implementing Decision 2021/914) as the primary legal mechanism for EEA-to-US data transfers.

The applicable module depends on the relationship:

| Relationship | SCC Module |
|---|---|
| Acme Corp as processor, customer as controller | Module 2 (Controller to Processor) |
| Acme Corp as controller (employee data, prospect data) | Module 1 (Controller to Controller) with affiliates |
| Acme Corp to sub-processors | Module 3 (Processor to Processor) |

SCCs are incorporated into:

- The Data Processing Agreement Template (Annex to the Enterprise Agreement).
- Sub-processor agreements with all vendors that process EEA personal data.
- Intra-group data transfer agreements between Acme Corp entities.

## 3. Supplementary Measures

Following the Court of Justice of the EU's Schrems II decision, SCCs alone may not provide sufficient protection if the laws of the receiving country undermine the safeguards. Acme Corp implements the following supplementary measures:

### 3.1 Technical Measures

- **Encryption in transit:** All data transferred between EEA and US infrastructure uses TLS 1.3.
- **Encryption at rest:** All personal data stored in the US region is encrypted using AES-256 with keys managed in HashiCorp Vault. Encryption keys for EEA customer data are stored in the EU-West region and never transferred to the US.
- **Pseudonymization:** Where operationally feasible, personal data is pseudonymized before transfer. The pseudonymization key is stored in the EU-West region.
- **Access controls:** Access to EEA personal data from the US is restricted to personnel with a documented business need, requires MFA, and is logged in the immutable audit trail.

### 3.2 Organizational Measures

- Acme Corp has not received any government access requests for customer data as of the date of this document. If a request is received, Legal will assess whether the request can be challenged and will notify the affected customer to the extent permitted by law.
- Acme Corp publishes a transparency report annually disclosing the number of government access requests received (currently zero).
- The Data Protection Officer reviews transfer mechanisms and supplementary measures annually.

### 3.3 Contractual Measures

- Sub-processors are contractually prohibited from disclosing personal data to government authorities without notifying Acme Corp first, unless legally prohibited from doing so.
- SCCs include the obligation for Acme Corp to challenge government access requests that it reasonably considers to be unlawful.

## 4. Transfer Impact Assessment

Acme Corp conducts a Transfer Impact Assessment (TIA) for each category of cross-border transfer. The TIA evaluates:

1. **Nature of the data:** What categories of personal data are transferred (account data, usage data, support data)?
2. **Destination country legal framework:** Does the receiving country have surveillance laws that could require access to the data? For the US, the relevant laws are FISA Section 702 and Executive Order 12333.
3. **Effectiveness of supplementary measures:** Do the technical, organizational, and contractual measures effectively prevent or detect government access that would undermine EEA-equivalent protection?
4. **Risk assessment:** What is the likelihood that the data in question would be subject to a government access request, considering the nature of Acme Corp's business and customer base?

The most recent TIA (September 2024) concluded that the combination of encryption, access controls, pseudonymization, and contractual safeguards provides an essentially equivalent level of protection for EEA personal data processed in the US, given the low risk profile of the data categories transferred.

TIAs are reviewed annually or when there is a material change in the legal framework of the receiving country.

## 5. Binding Corporate Rules

Acme Corp does not currently use Binding Corporate Rules (BCRs) as a transfer mechanism. BCRs may be considered in the future if Acme Corp expands to additional entities in jurisdictions without adequacy decisions. The Data Protection Officer monitors whether BCR adoption would provide operational benefits over the SCC-based approach.

## 6. Derogations

In limited circumstances, transfers may be based on GDPR Article 49 derogations:

- **Explicit consent:** Where the data subject has explicitly consented to the transfer after being informed of the risks. Used only for one-off transfers, not systematic processing.
- **Performance of a contract:** Where the transfer is necessary for the performance of a contract between the data subject and Acme Corp (e.g., providing the service to a customer who initiates a request that requires US-based processing).

Derogations are not used as a primary transfer mechanism and are documented on a case-by-case basis.

## 7. EU Data Residency Option

Enterprise customers may elect EU data residency, in which case all their data is stored and processed exclusively in the EU-West region. No cross-border transfer occurs for these customers. The data residency election is specified in the customer's Order Form and enforced at the infrastructure level. See the Enterprise SLA, Section 5.1.

## 8. Policy Governance

This document is reviewed annually by the Data Protection Officer and Legal. Questions should be directed to dpo@acmecorp.com or legal@acmecorp.com.

---

*Version 2.0 — Last revised October 1, 2024*
