---
title: "CNIL Guidance — HR Data Retention in France"
category: "Compliance"
doc_type: "reference"
last_updated: "2024-09-01"
owner: "Legal"
classification: "Internal"
kb: "regulatory"
---

# CNIL Guidance on HR Data Retention

**Source:** Commission nationale de l'informatique et des libertés (CNIL) — France's data protection authority
**Key references:** CNIL deliberations on HR data processing; CNIL reference framework for HR data (Référentiel relatif aux traitements de données à caractère personnel mis en œuvre aux fins de gestion du personnel), published 2020, updated 2023
**Scope:** Applies to all organizations processing personal data of employees, applicants, and former employees in France
**Maintained by:** Acme Corp Legal Department for internal reference

---

## 1. Overview

The CNIL provides specific guidance on how long employers may retain HR data under French law. These retention periods implement the GDPR's storage limitation principle (Article 5(1)(e)) with French-specific interpretations based on the statute of limitations for employment disputes (Code du travail), tax law, and social security law.

The CNIL's guidance is not binding regulation, but it represents the CNIL's enforcement expectations. Employers that deviate from these periods should be able to justify the deviation under GDPR Article 5(1)(e) and document the justification.

---

## 2. Retention Periods by Record Type

The CNIL distinguishes three retention phases:

- **Active retention (base active):** The data is actively used for its original purpose and accessible to operational staff.
- **Intermediate retention (archivage intermédiaire):** The original purpose has been fulfilled but the data is retained for legal, regulatory, or evidentiary reasons with restricted access.
- **Deletion or anonymization:** The data is permanently deleted or irreversibly anonymized.

| Record Type | Active Retention | Intermediate Retention | Total Maximum | CNIL Basis |
|---|---|---|---|---|
| **Recruitment — applications (not hired)** | Until position is filled | 2 years from last contact with candidate | 2 years | CNIL reference framework |
| **Recruitment — applications (hired)** | Duration of employment | — (becomes part of employee file) | See employee file | — |
| **Employee personnel file** | Duration of employment | 5 years after departure | Employment + 5 years | Statute of limitations for employment disputes (Code du travail, Art. L.1471-1) |
| **Payroll records** | Current fiscal year | 5 years | 6 years total | French tax code (Livre des procédures fiscales, Art. L.102 B) |
| **Time and attendance records** | Current year | 5 years | 5 years | Statute of limitations for wage claims |
| **Performance reviews** | Duration of employment | 2 years after departure | Employment + 2 years | CNIL recommendation; proportionality principle |
| **Disciplinary records** | Duration of employment; sanctions over 3 years old must not be cited in new proceedings | 3 years after the sanction | Employment + 3 years | Code du travail, Art. L.1332-5 |
| **Training records** | Duration of employment | 2 years after departure | Employment + 2 years | CNIL reference framework |
| **Workplace accident / occupational illness** | Duration of employment | 5 years after departure (or longer if litigation pending) | Employment + 5 years | Social security code |
| **Health and safety records (médecine du travail)** | Duration of employment | 10 years after last occupational health visit | Employment + 10 years | Code de la santé publique, Art. R.4624-28 |
| **Social security declarations** | Current year | 6 years | 6 years | Social security code |
| **Works council / CSE election records** | Duration of mandate | 5 years after end of mandate | Mandate + 5 years | Electoral code |

---

## 3. Key Differences from Common International Practice

Organizations operating across multiple jurisdictions should be aware of the following areas where CNIL guidance is more restrictive than typical US or UK practice:

### 3.1 Performance Reviews

The CNIL recommends retaining performance reviews for no more than **2 years after the employee's departure**. This is notably shorter than the 7-year retention common in US practice (driven by US litigation norms) and shorter than many multinational employers' global policies.

**Rationale:** The CNIL considers performance reviews to contain personal assessments (subjective evaluations, development feedback, behavioral observations) that are particularly sensitive. Retaining these assessments for years after departure exceeds what is necessary for the original purpose (managing the employment relationship) and increases the risk of the data being used for unintended purposes.

Employers that wish to retain performance reviews longer than 2 years post-departure must document a specific legal basis (e.g., pending litigation, regulatory investigation) and restrict access to the legal team.

### 3.2 Employee Personnel Files

The CNIL permits intermediate retention of personnel files for **5 years after departure**, aligned with the French statute of limitations for employment disputes. US practice (employment + 7 years) exceeds this by approximately 2 years. For French employees, the CNIL period controls.

### 3.3 Training Records

The CNIL recommends **2 years after departure** for training records. This is shorter than the 5-year retention common in US practice (often driven by SOC 2 evidence requirements or OSHA records). For French employees, the CNIL period controls unless a specific regulation requires longer retention (e.g., safety training records may fall under the occupational health exception).

### 3.4 Recruitment Data (Not Hired)

The CNIL's **2-year** retention for rejected candidates is broadly consistent with US practice (EEOC requires 1–2 years). However, the CNIL requires that candidates be informed of the retention period and that data be deleted automatically — not merely flagged for manual review.

---

## 4. Access Restrictions During Intermediate Retention

During the intermediate retention phase, the CNIL requires that:

- Data is no longer accessible to operational managers or HR generalists.
- Access is restricted to legal, compliance, or audit personnel with a documented need.
- Technical access controls enforce the restriction (not merely a policy statement).
- The data is stored separately from active HR systems, or logical access controls segregate active and archived records.

---

## 5. Deletion and Anonymization

At the end of the total retention period:

- Data must be permanently deleted or irreversibly anonymized.
- Deletion must be verified and logged.
- Aggregated, anonymized workforce statistics (headcount trends, turnover rates, training completion averages) may be retained indefinitely for reporting purposes, provided no individual can be re-identified.

---

## 6. Enforcement

The CNIL has actively enforced HR data retention requirements:

- In 2022, the CNIL fined a French subsidiary of a multinational employer €100,000 for retaining employee surveillance data beyond the authorized period.
- In 2023, the CNIL issued a formal notice to an employer for retaining recruitment files for 5 years (exceeding the 2-year guideline) without documented justification.

The CNIL may conduct audits of HR data processing as part of its annual program of thematic controls. Employers should be prepared to demonstrate that retention periods are implemented, not merely documented in policy.

---

*This summary was prepared by the Acme Corp Legal Department for internal reference. Last revised September 1, 2024. For questions, contact legal@acmecorp.com or dpo@acmecorp.com.*
