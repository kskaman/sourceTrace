---
title: "HIPAA Compliance Overview"
category: "IT"
doc_type: "reference"
last_updated: "2024-10-01"
owner: "Information Security"
classification: "Confidential"
---

# HIPAA Compliance Overview

**Effective Date:** October 1, 2024
**Applies to:** All Acme Corp systems, teams, and personnel that process protected health information (PHI) on behalf of healthcare customers

## 1. Background

Acme Corp processes electronic protected health information (ePHI) for a subset of its customer base under executed Business Associate Agreements (BAAs). As a business associate under the Health Insurance Portability and Accountability Act (HIPAA), Acme Corp is required to implement administrative, physical, and technical safeguards to protect the confidentiality, integrity, and availability of ePHI.

This document summarizes Acme Corp's HIPAA obligations and the internal controls that satisfy them. It is intended as a reference for employees who work with healthcare customer data. For the full regulatory text, refer to 45 CFR Parts 160 and 164.

## 2. The HIPAA Privacy Rule

The HIPAA Privacy Rule establishes standards for the protection of individually identifiable health information. Under the Privacy Rule, Acme Corp must:

- Use and disclose protected health information only as permitted or required by the Privacy Rule or as authorized by the individual.
- Apply the **minimum necessary standard**: when using, disclosing, or requesting PHI, limit the information to the minimum amount necessary to accomplish the intended purpose.
- Provide individuals with access to their PHI upon request.
- Maintain records of disclosures for at least 6 years.

The minimum necessary standard does not apply to disclosures for treatment purposes or to disclosures required by law. In all other cases, employees must limit PHI access and sharing to what is strictly needed for the task at hand.

## 3. The HIPAA Security Rule

The HIPAA Security Rule requires covered entities and business associates to implement safeguards to protect ePHI. Acme Corp's controls are organized into three categories:

### 3.1 Administrative Safeguards

- Designated Security Officer responsible for HIPAA security compliance (function held by the Data Protection Officer).
- Workforce training on HIPAA requirements (annual, per the Mandatory Training Catalog).
- Risk analysis conducted annually to identify threats to ePHI.
- Sanctions for workforce members who violate HIPAA policies.
- Business Associate Agreements with all subcontractors who access ePHI.

### 3.2 Physical Safeguards

- Facility access controls (badge readers, visitor escort requirements).
- Workstation security (screen lock, full disk encryption, endpoint agent).
- Device disposal procedures (cryptographic erasure before decommissioning).

### 3.3 Technical Safeguards

The HIPAA Security Rule, Section 164.312(a)(1), requires access controls that restrict access to ePHI to authorized persons and software. Acme Corp implements the following access controls for ePHI systems:

- **Unique user identification:** Every user has a unique account. Shared accounts are prohibited for ePHI systems.
- **Emergency access procedure:** A documented break-glass process allows emergency access to ePHI systems when normal access mechanisms are unavailable.
- **Automatic logoff:** Sessions on ePHI systems time out after 15 minutes of inactivity.
- **Encryption and decryption:** ePHI is encrypted at rest (AES-256) and in transit (TLS 1.3) per the Encryption Standards.

Additional technical controls include:

- **Audit controls (Section 164.312(b)):** All access to ePHI is logged with user identity, timestamp, action performed, and records accessed. Logs are retained per the Audit Log Retention policy (1 year hot, 6 years cold).
- **Integrity controls (Section 164.312(c)(1)):** Mechanisms to authenticate ePHI and detect unauthorized alteration, including database checksums and application-level integrity verification.
- **Transmission security (Section 164.312(e)(1)):** All ePHI transmitted over electronic networks is encrypted using TLS 1.3. No exceptions for internal service-to-service traffic.

## 4. Breach Notification

Under the HIPAA Breach Notification Rule, Acme Corp must notify affected individuals, the Department of Health and Human Services (HHS), and in some cases the media, following a breach of unsecured PHI.

- **Individual notification:** Within 60 days of discovering the breach.
- **HHS notification:** Within 60 days for breaches affecting 500 or more individuals. Breaches affecting fewer than 500 individuals are reported to HHS annually.
- **State attorneys general:** Notification as required by state breach notification laws.

Internally, the breach response process is coordinated per the Incident Response Runbook. The Data Protection Officer and Chief Compliance Officer are notified within 4 hours of breach confirmation.

## 5. Rules for Keeping Medical Records Private

Employees who handle protected health information must follow these rules to keep medical records private:

- Access ePHI only when required for your assigned duties. Do not browse patient or customer health records out of curiosity.
- Do not discuss PHI in public areas, shared office spaces, or non-secure communication channels.
- Do not copy ePHI to personal devices, personal email, or personal cloud storage.
- Verify the identity and authorization of anyone requesting PHI before disclosing it.
- Report any suspected unauthorized access or disclosure to security@acmecorp.com immediately.

Violations of these rules are subject to disciplinary action and may result in civil or criminal penalties under HIPAA.

## 6. Scope of Acme Corp's HIPAA Obligations

Not all Acme Corp systems or customers are subject to HIPAA. HIPAA requirements apply only to:

- Systems designated as "HIPAA in scope" in the service catalog.
- Customer accounts with an executed BAA.
- Employees and contractors who access ePHI as part of their role.

Employees who do not work with healthcare customers or ePHI are not subject to the HIPAA-specific controls described in this document, though the general security policies (IT Security Policy, Access Control Policy, Data Classification Policy) apply to all employees.

## 7. Policy Governance

This document is maintained by the Information Security team in coordination with the Data Protection Officer and the Chief Compliance Officer (Jordan Patel). It is reviewed annually and updated to reflect changes in HIPAA regulations or Acme Corp's BAA portfolio. Questions should be directed to security@acmecorp.com.

---

*Version 2.0 — Last revised October 1, 2024*
