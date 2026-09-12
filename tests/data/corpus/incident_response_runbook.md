---
title: "Incident Response Runbook"
category: "IT"
doc_type: "runbook"
last_updated: "2024-09-01"
owner: "Information Security"
classification: "Confidential"
---

# Incident Response Runbook

**Document ID:** ITSEC-010
**Effective Date:** September 1, 2024
**Applies to:** All Acme Corp engineering and operations personnel

## 1. Severity Classification

| Severity | Label | Definition | Response SLA |
|---|---|---|---|
| SEV1 | Critical | Active data breach, ransomware, complete production outage affecting all customers, security compromise with data exposure | 15 minutes to assemble response team |
| SEV2 | High | Major feature unavailable or severely degraded, confirmed unauthorized access to Restricted data, exploitation of a known vulnerability | 1 hour |
| SEV3 | Medium | Suspicious activity under investigation, successful phishing attempt, minor service degradation with workaround available, policy violation | 4 hours |
| SEV4 | Low | Failed attack attempt, minor policy deviation, security question, single-user access issue | Next business day |

## 2. On-Call Structure

### 2.1 Rotation

The engineering on-call rotation follows a weekly schedule (Monday 9 AM to Monday 9 AM). Two engineers are on call at all times:

- **Primary:** First responder for all alerts. Acknowledges within the SLA response time.
- **Secondary:** Backup if the primary does not acknowledge within 5 minutes. Also available for parallel investigation during SEV1/SEV2.

The on-call schedule is managed in PagerDuty. Swaps must be arranged at least 24 hours in advance and logged in PagerDuty.

### 2.2 On-Call Handoff

At each rotation change, the outgoing on-call engineer conducts a 15-minute handoff meeting with the incoming engineer covering:

- Active incidents and their current status.
- Ongoing investigations or monitoring watch items.
- Any known fragile systems or upcoming deployments that increase risk.
- Unresolved alerts that were deferred during the rotation.

Handoff notes are posted to the #oncall-handoff Slack channel.

## 3. Incident Response Process

### Step 1 — Detection and Reporting

Incidents may be detected through:

- Automated monitoring alerts (PagerDuty, Datadog, Grafana).
- Employee reports to security@acmecorp.com or the #security-incidents Slack channel.
- Customer reports through the support team.
- External notification (e.g., vulnerability researcher, partner, law enforcement).

Any employee who suspects a security incident must report it immediately. Do not attempt to investigate or remediate independently.

### Step 2 — Acknowledgment and Triage

The on-call engineer acknowledges the alert within the SLA response time for the severity level. Acknowledgment is recorded in PagerDuty and auto-posted to #incidents in Slack.

During triage, the on-call engineer:

1. Confirms the severity classification.
2. Assesses blast radius: how many customers, systems, or data sets are affected?
3. Determines if the issue is escalating, stable, or resolving.
4. For SEV1/SEV2: pages the incident commander (InfoSec team lead) and opens a dedicated incident Slack channel.

### Step 3 — Escalation Process for Critical Incidents

For SEV1 and SEV2 incidents, the following escalation chain applies:

| Time from Detection | Action | Responsible |
|---|---|---|
| 0–15 minutes | Primary on-call acknowledges, begins triage | On-call engineer |
| 15 minutes | Incident commander paged if not already engaged | On-call engineer |
| 15–30 minutes | Incident commander assembles response team, opens war room | Incident commander |
| 30 minutes | VP of Engineering notified | Incident commander |
| 1 hour | Status page updated with initial customer-facing communication | Incident commander + Customer Success |
| 2 hours | Chief Compliance Officer notified if data breach is suspected | Incident commander |
| 4 hours | Executive leadership briefed if incident is not contained | VP of Engineering |

For SEV3/SEV4 incidents, the on-call engineer handles triage and resolution independently, escalating to the InfoSec team lead only if the situation warrants reclassification to SEV2 or above.

### Step 4 — Containment

The response team takes immediate actions to limit scope and impact:

- Isolate affected systems from the network.
- Revoke compromised credentials and rotate affected secrets.
- Block malicious IPs or domains at the firewall and WAF.
- Roll back the most recent deployment if the incident correlates with a release.
- Enable circuit breakers for affected downstream services.
- Preserve forensic evidence (do not reboot or rebuild affected systems until forensic snapshots are taken).

Containment actions are logged in the incident channel in real time.

### Step 5 — Investigation

The incident commander coordinates the investigation:

- Root cause analysis: what vulnerability or failure led to the incident?
- Scope determination: what data, systems, or customers were affected?
- Forensic evidence collection: logs, disk images, memory dumps as appropriate.
- Timeline reconstruction: what happened, in what order, starting from when?

Investigation findings are documented in the incident record. External forensic investigators may be engaged for SEV1 incidents at the discretion of the VP of Engineering and Legal.

### Step 6 — Remediation

Once the root cause is identified:

- Apply the fix (patch, configuration change, code fix).
- Verify the fix through testing in staging before production deployment.
- Restore affected systems from clean backups if necessary.
- Re-enable any services or features that were disabled during containment.
- Confirm that monitoring shows normal behavior.

### Step 7 — Communication

**Internal communication:**

- Incident status updates posted to #incidents every 30 minutes during SEV1/SEV2.
- Post-resolution summary sent to engineering-all@acmecorp.com within 4 hours of resolution.

**Customer communication:**

- Status page updated within 15 minutes of SEV1/SEV2 acknowledgment, and updated at least every hour until resolution.
- Direct notification to affected customers within 24 hours of resolution for incidents involving data access or service degradation exceeding 1 hour.

**Regulatory communication:**

See Section 4 (Breach Notification).

### Step 8 — Postmortem

A blameless postmortem is conducted within 5 business days of incident resolution. The postmortem document must include:

- **Timeline:** Chronological sequence of events from detection through resolution.
- **Root cause:** Technical explanation of what failed and why.
- **Customer impact:** Number of customers affected, duration, data exposure (if any).
- **What went well:** Response actions that were effective.
- **What went poorly:** Gaps in detection, communication, or response.
- **Action items:** At least two concrete follow-up actions, each with an owner and a due date.

Postmortems are reviewed in the weekly engineering team meeting and archived in the postmortem repository. Action items are tracked to completion in the project management system.

## 4. Breach Notification

In the event of a confirmed data breach involving personal data:

### 4.1 Internal Notification

- The Data Protection Officer is notified within 4 hours of breach confirmation.
- The Chief Compliance Officer (Jordan Patel) is notified within 4 hours.
- Legal counsel is engaged within 8 hours.

### 4.2 Regulatory Notification

- **GDPR:** The relevant supervisory authority must be notified within 72 hours of becoming aware of the breach, per GDPR Article 33.
- **HIPAA:** If PHI is involved, notification follows the HIPAA Breach Notification Rule. The HIPAA Privacy Officer (a function of the Data Protection Officer) coordinates the notification.
- **State laws:** Notification to affected individuals follows applicable state breach notification laws. Legal determines which state laws apply based on the residency of affected individuals.

### 4.3 Customer Notification

Affected customers are notified in writing (email and, where appropriate, in-app notification) with:

- A description of the incident and the data involved.
- The date or date range of the breach.
- Steps Acme Corp is taking to remediate.
- Steps the customer can take to protect themselves.
- Contact information for questions.

## 5. Tools and Resources

| Tool | Purpose | Access |
|---|---|---|
| PagerDuty | Alerting and on-call management | All engineering |
| Grafana | Infrastructure and application metrics | All engineering |
| Datadog | Infrastructure health and container metrics | All engineering |
| Sentry | Application error tracking | All engineering |
| Slack (#incidents, #security-incidents) | Real-time coordination | All employees |
| Status page (status.acmecorp.com) | Customer-facing incident communication | Incident commanders |
| Postmortem template | Standardized postmortem format | Confluence / wiki |

## 6. Policy Governance

This runbook is maintained by the Information Security team and reviewed quarterly. The VP of Engineering is the process owner. Questions should be directed to security@acmecorp.com.

---

*Version 3.0 — Last revised September 1, 2024*
