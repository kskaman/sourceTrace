---
title: "EU AI Act Summary — Risk Tiers and Obligations"
category: "Compliance"
doc_type: "reference"
last_updated: "2024-11-01"
owner: "Legal"
classification: "Internal"
kb: "regulatory"
---

# EU Artificial Intelligence Act — Summary of Key Requirements

**Source Regulation:** Regulation (EU) 2024/1689 of the European Parliament and of the Council (the "AI Act")
**Adopted:** June 13, 2024
**Entry into force:** August 1, 2024
**Full application:** August 2, 2026 (with phased deadlines for specific provisions)
**Maintained by:** Acme Corp Legal Department for internal reference

---

## 1. Overview

The EU AI Act is the first comprehensive legal framework for artificial intelligence. It regulates the development, deployment, and use of AI systems placed on the EU market or affecting persons in the EU, regardless of where the provider is established. The Act adopts a risk-based approach: the higher the risk an AI system poses, the stricter the requirements.

The Act applies to:

- **Providers** (developers) of AI systems placed on the EU market.
- **Deployers** (users) of AI systems within the EU.
- **Importers and distributors** of AI systems in the EU.
- Providers and deployers outside the EU whose AI system output is used in the EU.

---

## 2. Risk Tiers

The AI Act classifies AI systems into four risk tiers:

### 2.1 Unacceptable Risk (Prohibited)

AI practices that pose an unacceptable risk to fundamental rights are banned. Prohibited practices include:

- **Social scoring** by public authorities or on their behalf — evaluating or classifying natural persons based on social behavior or personal characteristics, leading to detrimental treatment unrelated to the context in which the data was generated.
- **Real-time remote biometric identification** in publicly accessible spaces for law enforcement purposes (with narrow exceptions for serious crime).
- **Exploitation of vulnerabilities** — AI systems that exploit the vulnerabilities of specific groups (age, disability, social or economic situation) to materially distort behavior in a way that causes or is likely to cause harm.
- **Subliminal manipulation** — AI techniques that deploy subliminal components beyond a person's consciousness to materially distort behavior, causing or likely to cause harm.
- **Untargeted scraping of facial images** from the internet or CCTV for the purpose of creating facial recognition databases.
- **Emotion recognition** in the workplace or educational institutions (with exceptions for medical or safety purposes).
- **Biometric categorization** that infers sensitive attributes (race, political opinions, trade union membership, religious beliefs, sexual orientation) from biometric data.

**Effective date:** February 2, 2025 (6 months after entry into force).

### 2.2 High Risk

AI systems that pose a significant risk to health, safety, or fundamental rights. Two categories:

**Category 1:** AI systems that are safety components of products covered by EU harmonization legislation (medical devices, machinery, vehicles, aviation, etc.).

**Category 2:** Standalone AI systems in specified areas:

| Domain | Examples |
|---|---|
| Biometric identification | Remote biometric identification systems (non-real-time) |
| Critical infrastructure | AI used in management of water, gas, electricity, or transport |
| Education and vocational training | AI that determines access to or assignment in educational institutions |
| Employment | AI for recruitment, screening, evaluation, or termination decisions |
| Essential services | AI for creditworthiness assessment, risk assessment in insurance, or prioritization of emergency services |
| Law enforcement | AI for risk assessment, polygraph, evidence evaluation |
| Migration and border control | AI for processing applications, risk assessment |
| Administration of justice | AI for researching and interpreting facts and law |

**Obligations for high-risk AI systems** (see Section 3).

**Effective date:** August 2, 2026 (24 months after entry into force).

### 2.3 Limited Risk

AI systems with specific transparency obligations:

- AI systems that interact with natural persons (chatbots) must disclose that the person is interacting with an AI system.
- AI-generated content (deepfakes, synthetic text, synthetic audio) must be labeled as AI-generated.
- Emotion recognition or biometric categorization systems (where permitted) must inform the exposed person.

### 2.4 Minimal Risk

All other AI systems. No specific obligations under the AI Act, though providers are encouraged to adopt voluntary codes of conduct.

---

## 3. Obligations for High-Risk AI Systems

Providers of high-risk AI systems must comply with the following requirements:

### 3.1 Risk Management System

Establish, implement, document, and maintain a risk management system throughout the AI system's lifecycle. The system must identify and analyze known and reasonably foreseeable risks, estimate and evaluate risks that may emerge when the system is used in accordance with its intended purpose and under conditions of reasonably foreseeable misuse, and adopt appropriate risk management measures.

### 3.2 Data and Data Governance

Training, validation, and testing datasets must be relevant, representative, free of errors, and complete. Data governance measures must address:

- Data collection and origin.
- Data preparation and labeling.
- Identification and mitigation of possible biases.
- Identification of data gaps or shortcomings.

### 3.3 Technical Documentation

Providers must draw up technical documentation before the system is placed on the market or put into service. Documentation must be kept up to date and include:

- General description of the AI system.
- Detailed description of elements and development process.
- Information about monitoring, functioning, and control.
- Risk management documentation.
- Changes made throughout the system's lifecycle.

### 3.4 Record-Keeping (Logging)

High-risk AI systems must be designed with logging capabilities that enable:

- Recording of events relevant to identifying risks and substantial modifications.
- Traceability of the system's operation throughout its lifecycle.
- Monitoring of the system's ongoing compliance.

Logs must be retained for a period appropriate to the intended purpose and at minimum for 6 months (unless longer retention is required by other EU or member state law).

### 3.5 Transparency and User Information

Providers must ensure that the AI system is accompanied by instructions for use that include:

- Identity and contact details of the provider.
- System characteristics, capabilities, and limitations.
- Intended purpose and foreseeable misuse.
- Performance metrics, including known limitations for specific groups.
- Human oversight measures.
- Expected lifetime and maintenance needs.

### 3.6 Human Oversight

High-risk AI systems must be designed to allow effective human oversight, including the ability for the human overseeing the system to:

- Fully understand the system's capabilities and limitations.
- Monitor its operation (including through interpretability tools).
- Decide not to use the system or to override, reverse, or interrupt its output.
- Intervene in the system's operation or stop it through a "stop" button or similar procedure.

### 3.7 Accuracy, Robustness, and Cybersecurity

High-risk AI systems must achieve and maintain an appropriate level of accuracy, robustness, and cybersecurity throughout their lifecycle. Systems must be resilient against errors, faults, inconsistencies, and attempts at manipulation by unauthorized third parties.

### 3.8 Conformity Assessment

Before placing a high-risk AI system on the market, the provider must conduct a conformity assessment to demonstrate compliance with the requirements. For most high-risk systems in Category 2, self-assessment is permitted. For biometric identification systems and critical infrastructure, third-party conformity assessment is required.

---

## 4. General-Purpose AI Models (GPAI)

The AI Act introduces specific provisions for general-purpose AI models (foundation models, large language models):

- **All GPAI providers:** Must provide technical documentation, usage instructions, comply with EU copyright law, and publish a training content summary.
- **GPAI with systemic risk** (models with cumulative training compute above 10^25 FLOPs, or designated by the Commission): Must additionally perform model evaluations, assess and mitigate systemic risks, report serious incidents, and ensure adequate cybersecurity protection.

---

## 5. Penalties

| Violation | Maximum Fine |
|---|---|
| Prohibited AI practices | €35,000,000 or 7% of worldwide annual turnover, whichever is higher |
| Non-compliance with high-risk obligations | €15,000,000 or 3% of worldwide annual turnover, whichever is higher |
| Supplying incorrect information to authorities | €7,500,000 or 1% of worldwide annual turnover, whichever is higher |

For SMEs and startups, proportionate caps apply.

---

## 6. Timeline

| Date | Milestone |
|---|---|
| August 1, 2024 | AI Act enters into force |
| February 2, 2025 | Prohibitions on unacceptable-risk AI practices apply |
| August 2, 2025 | GPAI provisions apply; codes of practice established |
| August 2, 2026 | Full application of high-risk AI system obligations |
| August 2, 2027 | High-risk obligations apply to AI systems embedded in regulated products (Category 1) |

---

*This summary was prepared by the Acme Corp Legal Department for internal reference. Last revised November 1, 2024. For questions, contact legal@acmecorp.com.*
