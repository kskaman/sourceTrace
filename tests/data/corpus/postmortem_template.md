---
title: "Postmortem Template"
category: "Engineering"
doc_type: "template"
last_updated: "2024-03-01"
owner: "Engineering"
classification: "Internal"
---

# Postmortem Template

**Instructions:** Copy this template for each new postmortem. Complete all sections within 5 business days of incident resolution. Post the finished document to the #postmortems Slack channel and archive it in the postmortem repository.

---

## Incident Summary

| Field | Value |
|---|---|
| Incident ID | INC-YYYY-NNN |
| Severity | SEV1 / SEV2 / SEV3 |
| Date | YYYY-MM-DD |
| Duration | HH:MM (from detection to resolution) |
| Incident Commander | Name |
| Author | Name |

**One-line summary:** _A single sentence describing what happened and what was affected._

---

## Timeline

Record all significant events in UTC. Include detection, escalation, containment, and resolution milestones.

| Time (UTC) | Event |
|---|---|
| HH:MM | Alert fired: [alert name] |
| HH:MM | On-call acknowledged |
| HH:MM | Incident commander paged |
| HH:MM | Containment action taken: [describe] |
| HH:MM | Root cause identified |
| HH:MM | Fix deployed |
| HH:MM | Monitoring confirms recovery |
| HH:MM | Incident resolved |

---

## Customer Impact

- **Customers affected:** Number or percentage of customers who experienced degraded service.
- **User-facing symptoms:** What did customers see? (errors, latency, missing data, downtime)
- **Duration of impact:** How long customers were affected (may differ from total incident duration if containment was partial).
- **Data exposure or loss:** Was any customer data exposed, corrupted, or lost? If yes, describe scope and initiate breach assessment per the Incident Response Runbook.
- **SLA impact:** Did the incident cause monthly uptime to drop below the 99.95% Enterprise SLA threshold?

---

## Root Cause

Describe the underlying cause of the incident. Be specific and technical. Do not blame individuals.

_Example: A database migration added a NOT NULL column without a default value. The migration succeeded on the empty staging database but failed on the production database with 2.3M existing rows, causing a 12-minute outage while the migration was rolled back._

---

## Contributing Factors

List factors that allowed the root cause to produce customer impact or that delayed detection/resolution:

- _Example: The migration was not tested against a production-sized dataset._
- _Example: The alerting threshold was set too high, delaying detection by 4 minutes._
- _Example: The on-call engineer was unfamiliar with the database rollback procedure._

---

## What Went Well

Acknowledge effective responses. This reinforces good practices.

- _Example: Incident was detected within 2 minutes of the migration failure._
- _Example: Rollback was executed cleanly with no data loss._
- _Example: Customer communication was posted to the status page within 15 minutes._

---

## What Went Poorly

Identify gaps without blame. Focus on systems, processes, and tooling.

- _Example: The migration testing process does not include a production-scale dataset._
- _Example: The runbook did not cover this specific migration failure mode._
- _Example: The on-call handoff notes did not mention the scheduled migration._

---

## Action Items

Every postmortem must include at least two concrete follow-up actions. Each action must have an owner and a due date.

| # | Action | Owner | Due Date | Status |
|---|---|---|---|---|
| 1 | _Example: Add production-scale migration testing to the CI pipeline_ | _Name_ | _YYYY-MM-DD_ | Open |
| 2 | _Example: Update the database runbook with migration rollback steps_ | _Name_ | _YYYY-MM-DD_ | Open |
| 3 | _Example: Lower the alerting threshold from 5% to 2% error rate_ | _Name_ | _YYYY-MM-DD_ | Open |

Action items are tracked in the engineering project management system. The incident commander is responsible for ensuring all items are completed by their due dates.

---

## Review

This postmortem is reviewed in the weekly engineering team meeting. Attendees confirm that the root cause is accurately captured, the action items are sufficient, and no additional follow-up is needed.

| Reviewer | Date | Approved |
|---|---|---|
| Engineering Manager | | ☐ |
| VP of Engineering (SEV1 only) | | ☐ |

---

*Template version 2.0. Maintained by the Engineering Platform team. Questions: eng-standards@acmecorp.com.*
