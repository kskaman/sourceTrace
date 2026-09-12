---
title: "Q3 2024 Budget Reallocation — ML Platform Team"
category: "Operations"
doc_type: "announcement"
last_updated: "2024-08-15"
owner: "Office of the VP of Engineering"
classification: "Confidential"
---

# Q3 2024 Budget Reallocation — ML Platform Team

**Date:** August 15, 2024
**From:** Sarah Chen, VP of Engineering
**To:** Engineering Leadership, Finance, Technical Steering Committee
**Classification:** Confidential

---

## Summary

Effective immediately, $2.1M has been reallocated from the FY 2024 Engineering discretionary budget to the ML Platform team for Q3 and Q4 2024. This reallocation was approved by VP of Engineering Sarah Chen on August 15, 2024, following review and recommendation by the Technical Steering Committee at its August 12, 2024 session.

## Background

The ML Platform team has been operating on its original FY 2024 budget of $1.4M, which covered headcount for 6 engineers and baseline infrastructure costs. Over the past two quarters, three factors have created a need for accelerated investment:

1. **Customer demand.** Enterprise pipeline includes 14 active opportunities where ML-powered features (semantic search, anomaly detection, natural language query) are explicit requirements. Estimated ARR at risk if we do not deliver by Q1 2025: $4.2M.
2. **Infrastructure readiness.** The feature store and model serving infrastructure are in prototype stage. Moving to production-grade requires dedicated compute capacity, additional engineering headcount, and third-party tooling licenses.
3. **Competitive pressure.** Two direct competitors shipped ML-powered analytics features in Q2. Our sales team reports that lack of parity is a factor in 3 of the last 5 lost enterprise deals.

## Allocation Breakdown

| Category | Amount | Purpose |
|---|---|---|
| Headcount (4 additional engineers) | $1,200,000 | Senior ML engineer (1), backend engineers (2), infrastructure engineer (1) |
| Cloud infrastructure | $480,000 | GPU compute for model training, expanded PostgreSQL cluster with HNSW vector indexes |
| Tooling and licenses | $220,000 | Feature store platform, experiment tracking, model monitoring |
| Contingency (10%) | $200,000 | Unplanned costs, scope adjustments |
| **Total** | **$2,100,000** | |

## Source of Funds

The reallocation draws from three sources within the existing Engineering budget:

- $900K from the deferred office expansion project (moved to FY 2025).
- $700K from the infrastructure modernization contingency (partially utilized in Q1–Q2; remainder reallocated).
- $500K from open headcount in the Platform Services team (2 unfilled positions, hiring paused for Q3).

No additional budget approval from the Board or CFO is required, as the total remains within the VP of Engineering's discretionary authority for intra-departmental reallocations.

## Expected Outcomes

The ML Platform team is expected to deliver the following by Q1 2025:

- Production-grade feature store supporting real-time and batch feature serving.
- Model serving infrastructure with sub-100ms inference latency at current customer scale.
- Semantic search capability powered by PostgreSQL HNSW vector indexes, integrated into the Core Platform.
- Beta release of the natural language query feature to 5 enterprise design partners.

## Governance

Progress will be tracked through the existing Engineering OKR process. The ML Platform team lead (reporting to Sarah Chen) will present status updates at the monthly Technical Steering Committee meetings. A formal milestone review is scheduled for November 15, 2024.

## Questions

Direct questions about this reallocation to Sarah Chen (sarah.chen@acmecorp.com) or the Engineering Operations team (eng-ops@acmecorp.com).

---

*This memo is classified as Confidential and is intended for internal distribution only.*
