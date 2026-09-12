---
title: "Order Fulfillment Process"
category: "Operations"
doc_type: "procedure"
last_updated: "2024-02-15"
owner: "Operations"
classification: "Internal"
---

# Order Fulfillment Process

**Effective Date:** February 15, 2024
**Applies to:** All new customer provisioning (self-serve, Pro, and Enterprise tiers)

## 1. Self-Serve and Pro Tier

Self-serve and Pro tier customers are provisioned automatically:

1. Customer completes checkout on acmecorp.com or the in-app upgrade flow.
2. Payment is processed and confirmed by the billing system.
3. The provisioning service creates the customer's workspace within 60 seconds of payment confirmation.
4. A welcome email with login credentials and quickstart link is sent immediately.
5. The Customer Success team is notified for accounts exceeding 20 seats for proactive onboarding outreach.

No manual intervention is required. If the automated provisioning fails (e.g., payment gateway timeout, identity provider error), the order is queued for manual review by the Operations team with a target resolution of 2 hours.

## 2. Enterprise Tier

Enterprise provisioning follows a structured onboarding workflow:

| Step | Owner | SLA |
|---|---|---|
| Contract signed and countersigned | Sales / Legal | — |
| Order entered into billing system | Deal Desk | 1 business day |
| Workspace provisioned | Operations | 1 business day after order entry |
| SSO and identity provider configured | IT + Customer IT | 3–5 business days |
| Data import (if migrating from another platform) | Solutions Engineering | 5–10 business days |
| Admin training session delivered | Customer Success | Within 10 business days of provisioning |
| Go-live confirmation | Customer Success Manager | Coordinated with customer |

Total time from signed contract to go-live is typically 10–15 business days for standard deployments. Complex deployments (custom integrations, data residency requirements, HIPAA-scoped environments) may take 20–30 business days.

## 3. Data Residency

Customers are provisioned in the US-East region by default. EU data residency (EU-West) is available at no additional cost and must be specified in the Order Form or requested before provisioning. Changing data residency after provisioning requires a data migration coordinated by the Solutions Engineering team (timeline: 5–10 business days).

## 4. Post-Provisioning

Once the customer workspace is active:

- The Customer Success Manager (CSM) is assigned within 1 business day.
- The CSM schedules a kickoff call within 5 business days of go-live.
- A 30-day health check is conducted to review adoption metrics, resolve open issues, and identify expansion opportunities.

## 5. Policy Governance

This process is maintained by the Operations team. Questions should be directed to operations@acmecorp.com.

---

*Version 1.1 — Last revised February 15, 2024*
