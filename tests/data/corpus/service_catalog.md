---
title: "Service Catalog"
category: "Engineering"
doc_type: "reference"
last_updated: "2025-01-15"
owner: "Engineering"
classification: "Internal"
---

# Service Catalog

**Last Updated:** January 15, 2025
**Maintained by:** Engineering Platform team

This catalog lists all production services operated by Acme Corp engineering, their owners, SLOs, and key dependencies.

---

## Core Services

| Service | Owner | Description | SLO (Availability) | SLO (p99 Latency) | Dependencies |
|---|---|---|---|---|---|
| API Gateway | Platform team | Routes and authenticates all inbound API requests | 99.99% | < 20ms (overhead only) | Auth Service, rate limiter (Redis) |
| Auth Service | Platform team | Handles authentication (API key, OAuth 2.0) and session management | 99.99% | < 50ms | PostgreSQL (primary), Redis (session store), Okta (SSO) |
| Records Service | Core Platform team | CRUD operations for records, the primary data entity | 99.95% | < 200ms | PostgreSQL (primary), Search Service |
| Search Service | ML Platform team | Hybrid search (BM25 + semantic) over records | 99.95% | < 300ms | PostgreSQL (pgvector replica), Embedding Service, Redis (cache) |
| Embedding Service | ML Platform team | Generates vector embeddings for documents and queries | 99.95% | < 100ms | Model serving infrastructure (acme-embed-v2) |
| Webhook Service | Core Platform team | Delivers outbound webhook events to customer endpoints | 99.9% | N/A (async) | Kafka (event bus), Redis (delivery state) |

## Data Services

| Service | Owner | Description | SLO (Availability) | SLO (p99 Latency) | Dependencies |
|---|---|---|---|---|---|
| Ingestion Pipeline | Data Engineering team | Extracts data from sources and loads into the feature store | 99.9% | N/A (batch) | Kafka, Spark, S3, PostgreSQL |
| Feature Store | ML Platform team | Manages feature computation, storage, and serving | 99.95% | < 5ms (online reads) | Redis (online store), S3 (offline store) |
| Export Service | Core Platform team | Handles bulk data exports (CSV, JSON) | 99.9% | N/A (async) | PostgreSQL (read replica 2), S3 |

## Analytics and ML Services

| Service | Owner | Description | SLO (Availability) | SLO (p99 Latency) | Dependencies |
|---|---|---|---|---|---|
| Anomaly Detection | ML Platform team | Identifies unusual patterns in time-series data | 99.9% | < 200ms | Feature Store, model serving (acme-anomaly-v1) |
| NLQ Service | ML Platform team | Natural language query processing (beta) | 99.5% (beta) | < 2000ms | Embedding Service, Search Service, LLM provider (external) |
| Classification Service | ML Platform team | Support ticket and content classification | 99.95% | < 50ms | Model serving (acme-classify-v3) |

## Compliance Services

| Service | Owner | Description | SLO (Availability) | SLO (p99 Latency) | Dependencies |
|---|---|---|---|---|---|
| DSAR Processor | Compliance Engineering team | Automates data subject access request fulfillment | 99.9% | N/A (async) | PostgreSQL, Export Service, notification service |
| Evidence Collector | Compliance Engineering team | Automates SOC 2 evidence collection | 99.9% | N/A (batch) | Audit log store, PostgreSQL, S3 |

## Infrastructure Services

| Service | Owner | Description | SLO (Availability) | SLO (p99 Latency) | Dependencies |
|---|---|---|---|---|---|
| PostgreSQL Cluster | Database Engineering team | Primary relational database (including pgvector) | 99.99% | N/A (measured per query) | AWS RDS, S3 (backups) |
| Redis Cluster | Platform team | Caching, session storage, feature store online layer | 99.99% | < 2ms | AWS ElastiCache |
| Kafka Cluster | Platform team | Event streaming for webhooks, ingestion, and inter-service communication | 99.95% | < 50ms (produce) | AWS MSK |
| Monitoring Stack | Platform team | Datadog, Grafana, PagerDuty integration | 99.9% | N/A | Datadog (SaaS), PagerDuty (SaaS) |

---

## Service Ownership Rules

- Every service must have exactly one owning team. The owning team is responsible for the service's SLO, on-call rotation, and runbook.
- Ownership changes require approval from both the outgoing and incoming team leads and must be documented in this catalog within 5 business days.
- Services without an active on-call rotation are not permitted in production.

## SLO Governance

- SLOs are reviewed quarterly per the Engineering Standards.
- Services that miss their availability SLO for 2 consecutive months trigger an error budget freeze (feature development paused until reliability is restored).
- SLO data is published in the weekly engineering metrics report.

---

*Questions about service ownership or SLOs: platform-eng@acmecorp.com.*
