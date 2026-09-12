---
title: "Release Notes — Q4 2025"
category: "Product"
doc_type: "reference"
last_updated: "2026-01-05"
owner: "Product"
classification: "Public"
---

# Release Notes — Q4 2025

**Period:** October 1 – December 31, 2025

---

## Highlights

- AI-generated report summaries reached general availability.
- Granular role-based access controls shipped for Pro, Premium, and Enterprise.
- The Startup tier launched on October 1 alongside the Q4 pricing restructure.
- FedRAMP initial application was submitted on October 28.

## New Features

### AI-Generated Report Summaries — General Availability (November 12)

Available on Premium and Enterprise plans. The platform now generates a natural language summary for any report or dashboard, highlighting key trends, outliers, and period-over-period changes. Summaries can be included in scheduled report emails or viewed inline on the dashboard. The feature uses Acme Corp's internal ML models; customer data is not sent to third-party AI providers.

### Granular Role-Based Access Controls (December 10)

Administrators can now define custom permission roles beyond the default Owner / Admin / Member / Viewer hierarchy. Custom roles support fine-grained permissions at the workspace, record type, and field level. Available on Pro (up to 5 custom roles), Premium (up to 15), and Enterprise (unlimited). Existing accounts retain their current role structure; migration to custom roles is optional.

### Startup Tier (October 1)

A new plan tier for companies with fewer than 50 employees, priced at $35/seat/month (40% discount off Pro). Annual billing only. Companies that grow beyond 50 employees transition to Pro pricing at their next renewal. See the Q4 2025 Pricing Structure for full details.

### Data Retention Automation (November 28)

Enterprise customers can now configure automated data retention rules within the platform. Rules specify retention periods per record type and automatically archive or delete records when the retention period expires. This feature supports compliance with internal retention policies and regulatory requirements (GDPR storage limitation, industry-specific mandates). Configuration is under **Settings > Compliance > Data Retention**.

## Improvements

- **Natural language query:** Improved date-range handling (fix for the known issue from Q3). Queries like "revenue last quarter" and "incidents in September" now correctly resolve to the appropriate date range.
- **Search relevance:** Tuned the hybrid search scoring model, improving mean reciprocal rank (MRR) by 8% on internal benchmarks.
- **Webhook delivery:** Added a delivery log viewable in the dashboard under **Settings > API > Webhooks > Delivery Log**. Each delivery shows status, response code, latency, and retry history.
- **CSV export:** Added support for UTF-8 BOM header in CSV exports, resolving character encoding issues when opening exports in Microsoft Excel.
- **Onboarding:** New interactive setup wizard for first-time users, reducing median time-to-first-value from 22 minutes to 9 minutes.

## Bug Fixes

- Fixed an issue where custom metadata filters in the search API returned empty results when the filter value contained special characters (ampersand, forward slash).
- Fixed a display bug in the admin console where suspended users appeared as "active" in the user count on the billing page.
- Fixed an edge case in the anomaly detection engine that produced false positives on datasets with fewer than 30 data points.
- Fixed webhook signature validation failure when the request body contained escaped Unicode characters.
- Fixed a timeout on the bulk export API for exports between 40 GB and 50 GB caused by an insufficient connection pool size.

## Deprecations

- **API v1:** End-of-life extended to March 1, 2026. This is the final extension. API v1 will be permanently deactivated on that date. All remaining v1 consumers have been contacted by the Developer Relations team.
- **Legacy report builder:** Removed on December 31, 2025 as previously announced. All saved reports were migrated to the custom reports system. No data was lost.
- **Offset-based pagination:** The `page` and `offset` parameters are removed effective January 1, 2026. Use `cursor` parameter for all list endpoints.

## Known Issues

- The mobile app does not yet support custom dashboards. Planned for Q1 2026.
- Data retention automation does not apply retroactively to records created before the rule was configured. A backfill option is planned for Q1 2026.
- Granular RBAC does not yet integrate with SCIM provisioning for automatic role assignment. Manual role assignment is required after SCIM-provisioned users are created. Fix planned for Q1 2026.

---

*Release notes published January 5, 2026. Questions or feedback: product@acmecorp.com.*
