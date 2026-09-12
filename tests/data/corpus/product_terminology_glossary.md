---
title: "Product Terminology Glossary"
category: "Product"
doc_type: "reference"
last_updated: "2025-01-10"
owner: "Product"
classification: "Internal"
---

# Product Terminology Glossary

**Last Updated:** January 10, 2025

This glossary defines key terms used in the Acme Corp platform, documentation, and internal communications. Use these definitions consistently in customer-facing materials.

---

| Term | Definition |
|---|---|
| **Account** | A billable entity in the Acme Corp platform. Each account has one Owner, one or more Admins, and any number of Members and Viewers. |
| **Workspace** | A container for records, dashboards, and settings. Accounts can have multiple workspaces to organize content by team, project, or department. |
| **Record** | The fundamental unit of content in Acme Corp. A record has a name, body (text content), tags, metadata, and attachments. |
| **Dashboard** | A visual display of metrics and charts built from records and analytics data. Available as pre-built templates or custom configurations. |
| **Hybrid search** | The default search mode on Pro plans and above. Combines BM25 keyword matching with semantic vector similarity to rank results by relevance. |
| **Semantic search** | Search based on the meaning of the query rather than exact keyword matches. Uses vector embeddings to find conceptually similar content. |
| **BM25** | A keyword-based ranking function used in the hybrid search pipeline. Effective for queries containing specific terms, identifiers, or exact phrases. |
| **Anomaly detection** | An ML-powered feature (Data & Analytics add-on) that identifies unusual patterns in time-series data and generates alerts when configured thresholds are exceeded. |
| **Natural language query** | A feature (currently in beta) that allows users to ask questions in plain English and receive answers generated from their data. |
| **Compliance Suite** | An add-on product for regulated industries. Includes HIPAA-compliant data handling, automated SOC 2 evidence collection, and GDPR DSAR processing. |
| **DSAR** | Data Subject Access Request. A formal request from an individual to access, correct, or delete their personal data, as provided under GDPR and similar regulations. |
| **SSO** | Single Sign-On. Allows users to authenticate with their organization's identity provider (Okta, Azure AD, Google Workspace) instead of a separate Acme Corp password. |
| **SCIM** | System for Cross-domain Identity Management. A protocol for automatically provisioning and deprovisioning user accounts from an identity provider. Enterprise only. |
| **Webhook** | An HTTP callback that sends real-time event notifications to a customer's endpoint when something happens in Acme Corp (e.g., record created, user invited). |
| **API key** | A credential used to authenticate API requests. Prefixed `acme_sk_live_` for production and `acme_sk_test_` for sandbox. |
| **OAuth 2.0** | An authorization protocol used for third-party integrations that act on behalf of a user. Acme Corp supports the Authorization Code and Client Credentials flows. |
| **Seat** | A licensed user slot. Billing is per seat per month. Adding a user consumes a seat; removing a user frees one at the next billing cycle. |
| **Tier** | A pricing level (Starter, Startup, Pro, Enterprise) that determines available features, limits, and support levels. |
| **Add-on** | An optional product module (Data & Analytics, Compliance Suite, Advanced API) that can be added to a Pro or Enterprise subscription for an additional per-seat fee. |
| **Service credit** | A billing credit issued to Enterprise customers when monthly uptime falls below the 99.95% SLA guarantee. Requested through the SLA dashboard. |
| **Data residency** | The geographic region where customer data is stored and processed. Options: US-East (default) and EU-West (Enterprise, on request). |
| **Sandbox** | A non-production environment for testing integrations, configurations, and workflows. Enterprise accounts may have up to 3 sandboxes. |
| **Postmortem** | A blameless review conducted after a service incident. Includes timeline, root cause, customer impact, and action items. Published internally and (for major incidents) to affected customers. |

---

## Internal Engineering Terms

These terms are used internally by the engineering and operations teams. They do not appear in customer-facing documentation.

| Term | Definition |
|---|---|
| **Feature store** | The component of the ML platform that manages feature computation, storage, and serving for real-time and batch inference. |
| **HNSW** | Hierarchical Navigable Small World. The approximate nearest neighbor algorithm used in PostgreSQL (via pgvector) for semantic search indexing. |
| **pgvector** | A PostgreSQL extension that adds vector data types and similarity search operators. The foundation of Acme Corp's semantic search infrastructure. |
| **Backend stack** | The platform backend is built primarily in Python (API services, ML pipeline, data processing) and Go (high-throughput ingestion service, real-time event bus). The frontend uses TypeScript and React. |
| **Canary deployment** | A deployment strategy where new code is rolled out to a small percentage of traffic before full rollout. Used for all production deployments. |
| **Circuit breaker** | A resilience pattern that stops calling a failing downstream service after repeated failures, preventing cascading outages. Implemented in the API gateway. |

---

*Additions or corrections to this glossary should be submitted to product@acmecorp.com.*
