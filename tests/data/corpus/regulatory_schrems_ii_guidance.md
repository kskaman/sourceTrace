---
title: "Schrems II Guidance — International Data Transfers"
category: "Compliance"
doc_type: "reference"
last_updated: "2024-09-01"
owner: "Legal"
classification: "Internal"
kb: "regulatory"
---

# Post-Schrems II Guidance on International Data Transfers

**Background:** Court of Justice of the EU, Case C-311/18, Data Protection Commissioner v. Facebook Ireland Ltd and Maximillian Schrems ("Schrems II"), decided July 16, 2020
**Supplementary guidance:** European Data Protection Board (EDPB) Recommendations 01/2020 on supplementary measures (adopted June 2021)
**Maintained by:** Acme Corp Legal Department for internal reference

---

## 1. What the Schrems II Ruling Decided

The Court of Justice of the EU (CJEU) ruled that:

1. **The EU-US Privacy Shield is invalid.** The Privacy Shield framework, which had been used by thousands of organizations to transfer personal data from the EU to the US, was struck down because US surveillance laws (particularly FISA Section 702 and Executive Order 12333) did not provide EU data subjects with adequate protection or effective legal remedies.

2. **Standard Contractual Clauses (SCCs) remain valid in principle.** However, the mere execution of SCCs is not sufficient. The data exporter must assess, on a case-by-case basis, whether the law of the receiving country provides an essentially equivalent level of protection for personal data. If it does not, the exporter must implement supplementary measures to bridge the gap, or suspend the transfer.

3. **Supervisory authorities must intervene** if a data exporter fails to ensure adequate protection, including suspending transfers where supplementary measures are insufficient.

---

## 2. The EU-US Data Privacy Framework (DPF)

Following Schrems II, the EU and US negotiated a new framework:

- **Executive Order 14086** (October 2022) introduced new safeguards for US signals intelligence activities, including proportionality requirements and a Data Protection Review Court (DPRC) for EU individuals to seek redress.
- **EU adequacy decision** (July 2023) established the EU-US Data Privacy Framework as a valid transfer mechanism for organizations certified under the DPF.

Organizations certified under the DPF may transfer personal data from the EU without the need for SCCs or supplementary measures for those transfers. However:

- Certification is voluntary and requires annual self-certification with the US Department of Commerce.
- The adequacy decision may be challenged or revoked (a "Schrems III" scenario). Organizations should not treat the DPF as permanent.
- Organizations not certified under the DPF must continue to rely on SCCs with supplementary measures.

**Operational note:** As of the date of this document, Acme Corp has not self-certified under the EU-US Data Privacy Framework. Acme Corp relies on SCCs with supplementary measures as its primary transfer mechanism. The decision on DPF certification is under review by Legal.

---

## 3. Transfer Impact Assessment (TIA)

The EDPB recommends a six-step process for assessing international transfers:

### Step 1 — Map Your Transfers

Identify all transfers of personal data to third countries, including:

- Direct transfers (data sent from EU to a non-EU entity).
- Onward transfers (data transferred by an EU processor to a non-EU sub-processor).
- Remote access (non-EU personnel accessing data stored in the EU).

### Step 2 — Identify the Transfer Mechanism

Determine the legal basis for each transfer:

- Adequacy decision (Article 45).
- Standard Contractual Clauses (Article 46(2)(c)).
- Binding Corporate Rules (Article 46(2)(b)).
- Derogations (Article 49) — only for occasional, non-repetitive transfers.

### Step 3 — Assess the Law of the Receiving Country

Evaluate whether the receiving country's legal framework impairs the effectiveness of the transfer mechanism. Key factors:

- Does the country have laws that permit government access to personal data (surveillance laws, national security legislation)?
- Are such laws limited to what is necessary and proportionate?
- Do data subjects have effective legal remedies against government access?
- Is there an independent oversight mechanism?

For transfers to the US, the relevant laws are:

- **FISA Section 702:** Allows targeted surveillance of non-US persons outside the US for foreign intelligence purposes. Does not permit bulk collection. Post-EO 14086, proportionality and necessity requirements apply.
- **Executive Order 12333:** Authorizes the collection of foreign intelligence through signals intelligence. Post-EO 14086, new safeguards apply but the scope remains broader than EU standards.
- **CLOUD Act:** Allows US law enforcement to compel US-based service providers to produce data regardless of where the data is stored. May conflict with GDPR if the request targets EU data subject data.

### Step 4 — Identify Supplementary Measures

If the assessment in Step 3 concludes that the transfer mechanism alone does not provide essentially equivalent protection, implement supplementary measures. The EDPB categorizes supplementary measures into three types:

**Technical measures:**

- Encryption with keys controlled by the data exporter (the importer cannot access the plaintext).
- Pseudonymization with the mapping table held exclusively by the exporter.
- Split or multi-party processing where no single entity in the receiving country has access to the complete dataset.

**Organizational measures:**

- Internal policies on handling government access requests.
- Transparency reporting on government requests received.
- Governance structures to ensure the importer challenges disproportionate government requests.

**Contractual measures:**

- Obligations for the importer to notify the exporter of government access requests (to the extent legally permitted).
- Obligations to challenge requests that the importer considers disproportionate.
- Obligations to provide minimum information if compelled to disclose data, and to inform the data subject (if legally permitted).

### Step 5 — Procedural Steps

Implement any procedural steps necessary to activate the supplementary measures (e.g., amending contracts, deploying technical infrastructure, updating policies).

### Step 6 — Re-Evaluate at Appropriate Intervals

Monitor developments in the receiving country's legal framework and re-evaluate the TIA periodically. The EDPB recommends re-evaluation at least annually or when a material legal change occurs.

---

## 4. When Supplementary Measures Are Insufficient

If the assessment concludes that no combination of supplementary measures can bridge the protection gap — for example, if the receiving country's law requires the importer to provide government access to data in plaintext and the technical measures cannot prevent this — the transfer must be suspended.

The data exporter must notify the competent supervisory authority if it continues transfers despite being unable to ensure essentially equivalent protection.

---

## 5. Practical Implications

| Scenario | Recommended Approach |
|---|---|
| Transfer to a country with an adequacy decision (e.g., Japan, UK, South Korea) | No supplementary measures required. Rely on adequacy decision. |
| Transfer to the US under DPF certification | No supplementary measures required while adequacy decision is in effect. Monitor for revocation. |
| Transfer to the US without DPF certification | SCCs + supplementary measures (encryption, access controls, TIA). |
| Transfer to a country without adequacy and with broad surveillance powers | Evaluate whether technical measures can prevent government access. If not, consider data localization. |
| Remote access by non-EU personnel to EU-stored data | Treat as a transfer. Apply the same assessment and supplementary measures. |

---

## 6. Key Takeaways

1. SCCs are necessary but not sufficient. Every transfer requires a case-by-case assessment.
2. Technical measures (encryption with exporter-held keys) are the most effective supplementary measure because they prevent the importer from accessing plaintext, neutralizing the risk of compelled disclosure.
3. The EU-US Data Privacy Framework provides an alternative pathway but is not permanent and does not cover organizations that have not self-certified.
4. Transfer Impact Assessments must be documented and kept current. They are evidence of compliance in the event of a supervisory authority inquiry.
5. Data localization (keeping EU data in the EU) eliminates transfer risk entirely and should be considered for high-sensitivity processing.

---

*This guidance was prepared by the Acme Corp Legal Department for internal reference. Last revised September 1, 2024. For questions, contact legal@acmecorp.com or dpo@acmecorp.com.*
