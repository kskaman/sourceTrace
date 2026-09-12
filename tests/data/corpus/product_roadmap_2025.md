---
title: "Product Roadmap — 2025"
category: "Product"
doc_type: "reference"
last_updated: "2025-01-10"
owner: "Product"
classification: "Confidential"
---

# Product Roadmap — 2025

**Last Updated:** January 10, 2025
**Owner:** Anika Johansson, VP of Product
**Classification:** Confidential — do not share externally

---

## Strategic Themes

Three themes guide the 2025 roadmap:

1. **AI-native workflows.** Ship ML-powered features from beta to general availability and expand natural language capabilities across the platform.
2. **Enterprise scale.** Invest in performance, governance, and compliance features that unlock larger deployments and regulated industries.
3. **Platform extensibility.** Open the platform to third-party integrations and customer-built automations through a public API and webhook ecosystem.

## Q1 2025 (January – March)

| Priority | Feature | Target Date | Status |
|---|---|---|---|
| P0 | Semantic search GA (hybrid keyword + vector) | February 15 | In progress |
| P0 | HIPAA compliance for Compliance Suite — GA | January 31 | Shipped |
| P1 | Natural language query — beta to 20 enterprise design partners | March 1 | In progress |
| P1 | Bulk data export API (up to 50 GB) | February 28 | In progress |
| P2 | Dashboard template library expansion (51 → 75 templates) | March 31 | Planned |

## Q2 2025 (April – June)

| Priority | Feature | Target Date | Status |
|---|---|---|---|
| P0 | Natural language query — GA | May 15 | Planned |
| P0 | SOC 2 automated evidence collection — customer-facing | April 30 | Planned |
| P1 | Custom workflow builder (no-code automation) | June 15 | Planned |
| P1 | SAML 2.0 SSO for Pro tier (currently Enterprise only) | May 31 | Planned |
| P2 | Mobile app — read-only dashboard access (iOS and Android) | June 30 | Planned |

## Q3 2025 (July – September)

| Priority | Feature | Target Date | Status |
|---|---|---|---|
| P0 | Public API v2 — webhooks, search, and records endpoints GA | July 15 | Planned |
| P1 | Anomaly detection — configurable thresholds and alerting | August 31 | Planned |
| P1 | Multi-region data residency — APAC region evaluation | September 30 | Discovery |
| P2 | AI-generated report summaries (beta) | September 30 | Planned |
| P2 | Integrations marketplace — partner SDK and submission workflow | August 31 | Planned |

## Q4 2025 (October – December)

| Priority | Feature | Target Date | Status |
|---|---|---|---|
| P0 | FedRAMP authorization — initial application | October 31 | Discovery |
| P1 | AI-generated report summaries — GA | November 15 | Planned |
| P1 | Role-based access controls — granular permissions model | December 15 | Planned |
| P2 | Offline mode for mobile app | December 31 | Planned |
| P2 | Data retention automation — customer-configurable policies | November 30 | Planned |

## Priority Definitions

| Priority | Meaning |
|---|---|
| P0 | Must ship in the quarter. Revenue or compliance commitment. |
| P1 | Should ship in the quarter. High strategic value; may slip one quarter. |
| P2 | Planned for the quarter. May be deferred based on P0/P1 progress. |

## Dependencies and Risks

- **Semantic search GA** depends on the ML Platform infrastructure funded by the Q3 2024 budget reallocation. The PostgreSQL HNSW index migration must be complete before launch.
- **APAC region evaluation** requires Legal review of data residency requirements in Singapore and Australia (see the PDPA Guide). No infrastructure commitment in 2025; decision point is September 30.
- **FedRAMP** is a multi-year effort. The Q4 2025 target is the initial application only. Authorization is expected no earlier than Q3 2026.

## How to Provide Input

Product requests and feedback should be submitted through the internal Product Feedback board (product.acmecorp.com/feedback) or discussed directly with your team's Product Manager. Roadmap review meetings are held monthly on the first Thursday.

---

*This roadmap is a planning document and is subject to change. It does not constitute a commitment to deliver any specific feature by any specific date.*
