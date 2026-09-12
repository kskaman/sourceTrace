---
title: "PDPA Guide — Asia-Pacific Data Protection Requirements"
category: "Compliance"
doc_type: "reference"
last_updated: "2024-07-01"
owner: "Legal"
classification: "Internal"
kb: "regulatory"
---

# Personal Data Protection Act (PDPA) — Asia-Pacific Guide

**Jurisdictions Covered:** Singapore (PDPA 2012, amended 2020), Australia (Privacy Act 1988, amended 2022), and general APAC data protection principles
**Maintained by:** Acme Corp Legal Department for internal reference
**Last Revised:** July 1, 2024

This document summarizes the key APAC data protection requirements relevant to Acme Corp's operations in the region. Acme Corp currently serves customers in Singapore and Australia and is expanding into additional APAC markets.

---

## 1. Singapore — Personal Data Protection Act (PDPA)

### 1.1 Scope

The PDPA governs the collection, use, disclosure, and care of personal data by organizations in Singapore. It applies to any organization that collects, uses, or discloses personal data in Singapore, regardless of where the organization is incorporated.

### 1.2 Consent

Organizations must obtain consent before collecting, using, or disclosing personal data. Consent must be:

- Informed: the individual is told the purpose of collection.
- Voluntary: not a condition of providing a product or service unless the data is reasonably necessary for that product or service.
- Withdrawable: individuals may withdraw consent at any time with reasonable notice. The organization must inform the individual of the likely consequences of withdrawal.

Deemed consent applies when the individual voluntarily provides personal data for a purpose that would be considered appropriate by a reasonable person.

### 1.3 Data Residency

The PDPA does not impose a strict data residency requirement. However, cross-border transfers are restricted under the Transfer Limitation Obligation:

- Personal data may be transferred outside Singapore only if the receiving country provides a comparable standard of protection.
- Acceptable transfer mechanisms include: contractual arrangements (similar to SCCs), binding corporate rules, or the recipient country being on an approved list.
- If a comparable standard cannot be ensured, the individual's consent to the transfer is required.

### 1.4 Data Breach Notification

Since the 2020 amendments, organizations must notify the Personal Data Protection Commission (PDPC) and affected individuals if a breach:

- Results in, or is likely to result in, significant harm to affected individuals, OR
- Is of a significant scale (500 or more individuals affected).

Notification to the PDPC must be made within **3 calendar days** of assessing that the breach is notifiable.

### 1.5 Penalties

The PDPC may impose financial penalties of up to **SGD 1,000,000 or 10% of annual turnover** in Singapore (whichever is higher) for organizations with annual turnover exceeding SGD 10 million.

---

## 2. Australia — Privacy Act 1988

### 2.1 Scope

The Privacy Act applies to Australian Government agencies, private sector organizations with annual turnover of more than AUD 3 million, and certain other organizations regardless of turnover (health service providers, those trading in personal information).

### 2.2 Australian Privacy Principles (APPs)

The Privacy Act is implemented through 13 Australian Privacy Principles:

| APP | Topic |
|---|---|
| APP 1 | Open and transparent management of personal information |
| APP 2 | Anonymity and pseudonymity options for individuals |
| APP 3 | Collection of solicited personal information |
| APP 5 | Notification of the collection of personal information |
| APP 6 | Use or disclosure of personal information |
| APP 8 | Cross-border disclosure of personal information |
| APP 11 | Security of personal information |
| APP 12 | Access to personal information |
| APP 13 | Correction of personal information |

### 2.3 Cross-Border Transfers (APP 8)

Before disclosing personal information to an overseas recipient, the organization must take reasonable steps to ensure the recipient does not breach the APPs. The organization remains liable for the overseas recipient's handling of the data.

Exceptions: consent from the individual, requirement by law, or the recipient is subject to a binding scheme substantially similar to the APPs.

### 2.4 Data Breach Notification (Notifiable Data Breaches Scheme)

Organizations must notify the Office of the Australian Information Commissioner (OAIC) and affected individuals of eligible data breaches — breaches likely to result in serious harm — within **30 days** of becoming aware.

### 2.5 Penalties

Maximum penalties for serious or repeated interferences with privacy:

- For corporations: the greater of AUD 50 million, three times the value of the benefit obtained, or 30% of domestic turnover during the relevant period.
- For individuals: AUD 2.5 million.

---

## 3. General APAC Data Residency Considerations

Data residency requirements vary significantly across APAC jurisdictions:

| Jurisdiction | Data Residency Requirement |
|---|---|
| Singapore | No strict residency; transfer limitation obligation applies |
| Australia | No strict residency; APP 8 cross-border disclosure rules apply |
| China (PIPL) | Data localization required for critical information infrastructure operators; security assessment required for cross-border transfers |
| India (DPDPA 2023) | Government may restrict transfers to specific countries by notification; no blanket localization for most data |
| Indonesia (PDP Law 2022) | Cross-border transfers permitted with adequate protection; data residency for certain sectors (financial services) |
| Japan (APPI) | Adequate protection or consent required; EU adequacy decision mutual recognition |
| South Korea (PIPA) | Consent or adequate protection required; EU adequacy decision mutual recognition |

**Operational note:** Acme Corp currently hosts APAC customer data in the US-East region. There is no dedicated APAC data center. Customers in jurisdictions with transfer restrictions are served under contractual safeguards (Standard Contractual Clauses or equivalent). If Acme Corp expands significantly in China, Indonesia, or other markets with data localization requirements, a dedicated APAC infrastructure deployment may be necessary. This is not currently planned.

---

## 4. Recommendations for Acme Corp

1. **Singapore and Australia customers** can be served from US-East under current contractual arrangements. Monitor regulatory developments in both jurisdictions for changes to transfer rules.
2. **China expansion** would require a dedicated data residency assessment and likely a local infrastructure deployment. Engage Legal before committing to any customer in mainland China.
3. **Maintain a transfer impact assessment** for APAC transfers, similar to the EU TIA documented in the Cross-Border Data Transfer Mechanisms policy.
4. **Review the Privacy Policy** to ensure APAC-specific disclosure requirements (Singapore PDPA notification, Australian APP 5) are addressed.

---

*This guide was prepared by the Acme Corp Legal Department for internal reference. Last revised July 1, 2024. For questions, contact legal@acmecorp.com.*
