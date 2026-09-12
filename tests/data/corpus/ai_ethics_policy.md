---
title: "AI Ethics Policy"
category: "Compliance"
doc_type: "policy"
last_updated: "2024-11-15"
owner: "Engineering"
classification: "Internal"
---

# AI Ethics Policy

**Effective Date:** November 15, 2024
**Approved by:** VP of Engineering (Sarah Chen), Chief Compliance Officer (Jordan Patel)
**Applies to:** All Acme Corp employees and contractors involved in the development, deployment, or operation of AI and machine learning systems

---

## 1. Scope

This policy governs all AI and machine learning systems developed or deployed by Acme Corp, including:

- ML-powered features in the Acme Corp platform (anomaly detection, semantic search, natural language query).
- Internal tools that use machine learning (spam filtering, support ticket routing, lead scoring).
- Third-party AI services integrated into Acme Corp products or operations.

## 2. Bias Testing

All ML models that produce outputs visible to customers or that influence decisions affecting individuals must undergo bias testing before deployment and on an ongoing basis:

- **Pre-deployment:** Bias evaluation across protected demographic categories (where applicable data is available) using fairness metrics appropriate to the use case (demographic parity, equalized odds, or calibration).
- **Post-deployment:** Quarterly bias monitoring for production models. If a model's fairness metrics degrade beyond the threshold established during pre-deployment evaluation, the model is flagged for review and retraining.
- **Documentation:** Bias test results, methodology, and thresholds are documented in the model card for each production model. Model cards are reviewed by the ML Platform team lead and the Data Protection Officer.

Models that cannot be meaningfully tested for bias (e.g., anomaly detection on infrastructure metrics with no demographic dimension) are exempt from demographic bias testing but must still undergo accuracy and error-rate analysis.

## 3. Explainability

Acme Corp requires that AI systems provide explanations appropriate to the stakes of their output:

| Risk Level | Explainability Requirement | Examples |
|---|---|---|
| Low | Model documentation and aggregate performance metrics available | Search ranking, content recommendations, auto-tagging |
| Medium | Per-prediction explanation available to internal operators on request | Support ticket routing, lead scoring, anomaly flagging |
| High | Per-prediction explanation provided to the affected individual automatically | Any model output used in access control decisions, compliance scoring, or fraud detection |

"Explanation" means a description of the key factors that influenced the model's output, in terms understandable to a non-technical audience. Feature importance scores, attention visualizations, or similar technical artifacts are acceptable for internal operators but must be translated into plain language for end-user-facing explanations.

## 4. Human-in-the-Loop

For high-stakes decisions — defined as decisions that may result in denial of service, account termination, financial penalty, or adverse action against an individual — a human must review and approve the decision before it takes effect.

Specifically:

- No customer account may be terminated or suspended solely on the basis of an automated model output.
- No employee may be subjected to disciplinary action based solely on automated monitoring or scoring (see also the Employee Monitoring Policy, Section 7).
- No access to a service or feature may be permanently revoked by an automated system without human review.
- Fraud detection models may temporarily freeze transactions pending human review, but the freeze must be reviewed within 4 hours during business hours or 12 hours outside business hours.

Automated systems may take temporary protective actions (rate limiting, temporary holds, alert generation) without human approval, provided that a human reviews the action within the timeframes above.

## 5. Prohibited Use Cases

Acme Corp prohibits the use of AI for the following purposes:

- **Mass surveillance:** Using AI to monitor or profile individuals at scale without specific, documented justification and legal basis.
- **Social scoring:** Assigning scores to individuals based on social behavior, personal characteristics, or predicted personality traits.
- **Manipulative design:** Using AI to exploit psychological vulnerabilities to influence user behavior against their interests.
- **Autonomous weapons:** Development of or contribution to autonomous weapons systems.
- **Biometric categorization:** Inferring sensitive attributes (race, political opinion, sexual orientation, religious belief) from biometric data.

Employees who believe an AI use case may fall into a prohibited category should raise the concern with the ML Platform team lead or the Data Protection Officer before proceeding.

## 6. Third-Party AI Services

Before integrating a third-party AI service into any Acme Corp product or workflow:

1. The Engineering team must complete an AI vendor assessment covering the vendor's bias testing practices, data handling, and model documentation.
2. The Data Protection Officer reviews the data flows to ensure compliance with the Data Processing Agreement and applicable privacy regulations.
3. The third-party service must not process customer data for the vendor's own model training unless explicitly authorized by the customer.

## 7. Governance and Review

This policy is reviewed semi-annually by the AI Ethics Review Board, which consists of:

- VP of Engineering (chair).
- Data Protection Officer.
- One representative from Product.
- One representative from Legal.
- One external advisor (rotated annually).

The Review Board evaluates new AI use cases, reviews bias test results, and assesses whether the policy remains aligned with evolving regulations and industry best practices.

## 8. Contact

Questions about this policy should be directed to ml-ethics@acmecorp.com or the Data Protection Officer at dpo@acmecorp.com.

---

*Version 1.0 — Last revised November 15, 2024*
