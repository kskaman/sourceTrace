---
title: "SLA Dashboard Guide"
category: "Product"
doc_type: "guide"
last_updated: "2024-06-15"
owner: "Customer Success"
classification: "Public"
---

# SLA Dashboard Guide

**Last Updated:** June 15, 2024
**Applies to:** Enterprise customers with an active Enterprise SLA

## 1. Accessing the Dashboard

The SLA dashboard is available at **app.acmecorp.com/sla** for account owners and administrators on Enterprise plans. The dashboard provides a real-time view of your account's uptime, latency, and service credit status.

## 2. Uptime Metrics

The uptime panel shows:

- **Current month uptime:** Percentage of uptime for the current calendar month, updated every 5 minutes. Calculated as: `(Total Minutes − Downtime Minutes) / Total Minutes × 100`.
- **Rolling 12-month uptime:** Average uptime across the last 12 calendar months.
- **Uptime history:** Month-by-month uptime percentage for the last 12 months, displayed as a bar chart. Months where uptime dropped below the 99.95% guarantee are highlighted in red.

Downtime is measured from the Acme Corp monitoring infrastructure. Scheduled maintenance windows (communicated at least 72 hours in advance) are excluded from the downtime calculation per the Enterprise SLA, Section 1.3.

## 3. Latency Metrics

The latency panel shows API response time for your account's production endpoints:

| Metric | Definition | SLA Target |
|---|---|---|
| p50 (median) | 50th percentile response time | < 100ms |
| p95 | 95th percentile response time | < 250ms |
| p99 | 99th percentile response time | < 500ms |

Latency is measured at the Acme Corp load balancer and does not include network transit time between your infrastructure and ours. Data is aggregated in 5-minute intervals and displayed for the last 24 hours, 7 days, and 30 days.

## 4. Service Credit Balance

If uptime in a calendar month falls below 99.95%, your account may be eligible for service credits per the Enterprise SLA, Section 2:

| Monthly Uptime | Credit |
|---|---|
| 99.90% – 99.95% | 10% of monthly fee |
| 99.00% – 99.89% | 25% of monthly fee |
| Below 99.00% | 50% of monthly fee |

The dashboard displays:

- **Earned credits:** Credits accrued from SLA breaches in the current and prior 12 months.
- **Applied credits:** Credits already deducted from invoices.
- **Available balance:** Credits eligible to be applied to the next invoice.

Credits are not applied automatically. To apply a credit, click **Request Credit** on the dashboard or email sla-credits@acmecorp.com within 30 days of the affected month.

## 5. Incident History

The incident history panel lists all incidents that affected your account in the last 12 months:

- Incident date and time.
- Duration.
- Severity (SEV1–SEV4).
- Root cause summary (linked to the public postmortem, if published).
- Whether the incident resulted in downtime counted against the SLA.

## 6. Notifications

Configure SLA notifications under **SLA Dashboard > Settings > Alerts**:

- **Uptime alert:** Receive an email when current-month uptime drops below a threshold you set (default: 99.97%).
- **Latency alert:** Receive an email when p99 latency exceeds 500ms for more than 10 consecutive minutes.
- **Credit eligibility:** Receive an email at month-end if your account has earned a new service credit.

Notifications are sent to all account administrators by default. Additional recipients can be added in the alert settings.

## 7. FAQ

**Q: Why does the dashboard show different uptime than the status page?**
A: The public status page (status.acmecorp.com) shows platform-wide uptime. The SLA dashboard shows uptime specific to the endpoints and services covered by your Enterprise SLA. Minor incidents that affect one customer's workload may not register on the platform-wide status page.

**Q: How long do I have to request a credit?**
A: Credit requests must be submitted within 30 days of the end of the affected month. Credits not requested within this window are forfeited.

**Q: Can I export SLA data for internal reporting?**
A: Yes. Click **Export** on any panel to download the data as CSV. Monthly SLA summary reports are also available as PDF under **SLA Dashboard > Reports**.

---

*For questions about the SLA dashboard or your service credit balance, contact your Customer Success Manager or email sla-credits@acmecorp.com.*
