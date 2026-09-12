---
title: "Release Notes — Q3 2025"
category: "Product"
doc_type: "reference"
last_updated: "2025-10-01"
owner: "Product"
classification: "Public"
---

# Release Notes — Q3 2025

**Period:** July 1 – September 30, 2025

---

## Key Changes in Q3

- Semantic search moved from beta to general availability.
- Anomaly detection thresholds are now configurable per dashboard.
- The Compliance Suite added automated GDPR DSAR processing.
- API v2.4 shipped with the new hybrid search endpoint.

## New Features

### Semantic Search — General Availability (July 15)

Hybrid search (combining keyword BM25 and semantic vector similarity) is now available to all Pro, Premium, and Enterprise customers. Search results are ranked by a fused relevance score. The default search mode for the `/v2/search` endpoint is now `hybrid`. Keyword-only mode remains available via the `mode=keyword` parameter.

### Configurable Anomaly Detection Thresholds (August 12)

Customers using the Data & Analytics add-on can now set custom sensitivity thresholds for anomaly detection alerts. Previously, thresholds were fixed at 2 standard deviations. Configurable options: 1.5, 2.0, 2.5, or 3.0 standard deviations. Available under **Settings > Analytics > Anomaly Detection**.

### GDPR DSAR Automation (September 8)

The Compliance Suite now supports automated data subject access request processing. When a DSAR is received through the privacy portal, the system automatically locates all records associated with the requester, generates a portable data package (JSON and PDF), and routes it for DPO review before delivery. Average processing time: 2.3 hours (down from a manual average of 15 hours).

### Integrations Marketplace — Partner SDK (September 22)

Third-party developers can now build and submit integrations using the new Partner SDK. The integrations marketplace is in early access with 8 launch partners. General availability is planned for Q4 2025.

## Improvements

- **Search performance:** Median search latency reduced from 62ms to 47ms through query optimization and index tuning.
- **Bulk export:** Maximum export size increased from 25 GB to 50 GB per request for Enterprise customers.
- **Webhook reliability:** Retry logic updated from 3 retries to 5 retries with longer exponential backoff intervals, reducing failed delivery rate by 40%.
- **Dashboard load time:** Pre-built dashboard templates now load 35% faster due to server-side rendering of chart components.

## Bug Fixes

- Fixed an issue where cursor-based pagination returned duplicate records when a record was updated between page fetches.
- Fixed a race condition in the webhook delivery system that occasionally caused events to be delivered out of order.
- Fixed incorrect CSV encoding for records containing non-ASCII characters in custom metadata fields.
- Fixed a UI bug where the "Export" button was hidden on the mobile web view for accounts with more than 100 records.

## Deprecations

- **API v1:** Reminder that API v1 reaches end-of-life on March 1, 2026 (extended from the original March 2025 deadline). All integrations should migrate to v2. See the API v1-to-v2 Migration Guide.
- **Legacy report builder:** The original report builder (pre-custom-reports) will be removed on December 31, 2025. Saved reports in the legacy format are automatically migrated to the new custom reports system.
- **Offset-based pagination:** The deprecated `page` and `offset` query parameters will be removed from list endpoints on January 1, 2026. Use cursor-based pagination (`cursor` parameter) instead.

## Known Issues

- Natural language query (beta) occasionally returns irrelevant results for queries containing date ranges. The ML Platform team is tuning the date-handling logic; a fix is expected in the October release.
- The mobile app (read-only dashboard access, shipped Q2) does not yet support custom dashboards. Custom dashboard support is planned for Q4.

---

*Release notes published October 1, 2025. Questions or feedback: product@acmecorp.com.*
