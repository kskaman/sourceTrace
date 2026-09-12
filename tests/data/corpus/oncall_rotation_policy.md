---
title: "On-Call Rotation Policy"
category: "Engineering"
doc_type: "policy"
last_updated: "2024-07-01"
owner: "Engineering"
classification: "Internal"
---

# On-Call Rotation Policy

**Effective Date:** July 1, 2024
**Owner:** Engineering Platform team
**Applies to:** All Acme Corp engineers on production on-call rotations

---

## 1. Rotation Structure

On-call rotations run weekly, from Monday 9:00 AM PT to the following Monday 9:00 AM PT. Two engineers are on call at all times:

- **Primary:** First responder for all production alerts.
- **Secondary:** Backup if the primary does not acknowledge an alert within 5 minutes. Also available for parallel investigation during SEV1/SEV2 incidents.

Rotations are managed in PagerDuty. Each team with a production service maintains its own rotation. Cross-team escalation follows the Incident Response Runbook.

## 2. Eligibility

All engineers L2 and above who own or regularly contribute to a production service are eligible for on-call duty. L1 (junior) engineers may shadow an on-call rotation for training but are not assigned as primary or secondary.

New engineers must complete on-call onboarding before their first rotation:

- Read the Incident Response Runbook and the Deployment Runbook.
- Shadow one full rotation with a senior engineer.
- Complete the on-call simulation exercise (a mock SEV2 scenario).

## 3. Handoff

At each rotation change, the outgoing primary conducts a 15-minute handoff meeting with the incoming primary:

- Active incidents and their current status.
- Ongoing investigations or monitoring watch items.
- Known fragile systems or upcoming risky deployments.
- Unresolved alerts that were deferred.

Handoff notes are posted to the #oncall-handoff Slack channel.

## 4. Response Expectations

| Alert Severity | Acknowledgment SLA | Action |
|---|---|---|
| SEV1 — Critical | 5 minutes | Page secondary immediately. Begin triage. Open incident channel. |
| SEV2 — High | 15 minutes | Begin triage. Assess if secondary support is needed. |
| SEV3 — Medium | 1 hour | Investigate during business hours. After-hours: acknowledge and schedule for next business day unless escalating. |
| SEV4 — Low | Next business day | Acknowledge and add to the team backlog. |

If the primary does not acknowledge within the SLA, PagerDuty automatically pages the secondary. If neither responds within 10 minutes, the engineering manager is paged.

## 5. Compensation

On-call duty is compensated as follows:

| Component | Amount |
|---|---|
| Weekly on-call stipend (primary or secondary) | $500 |
| Per-incident bonus (SEV1 response) | $200 per incident |
| Per-incident bonus (SEV2 response) | $100 per incident |
| Comp time for after-hours incidents | 1 hour of comp time per hour of active incident work outside 9 AM – 6 PM PT |

Compensation is processed through payroll on a monthly basis. Engineers log on-call incidents and hours in the engineering time-tracking tool.

## 6. Swaps and Coverage

- Swaps must be arranged at least 24 hours in advance and logged in PagerDuty.
- If an on-call engineer is sick or has an emergency, they notify their engineering manager immediately. The manager arranges coverage from the team's backup pool.
- On-call engineers should avoid scheduling vacation during their rotation. If unavoidable, arrange a swap at least 1 week in advance.

## 7. Escalation Path

If an on-call engineer needs help beyond their team's expertise:

| Escalation | Contact |
|---|---|
| Database issues | DBA on-call (separate PagerDuty rotation) |
| Infrastructure / networking | Platform on-call (separate PagerDuty rotation) |
| Security incident | InfoSec on-call (security@acmecorp.com + PagerDuty) |
| Customer-impacting incident (SEV1/SEV2) | Incident commander per the Incident Response Runbook |

## 8. Well-Being

On-call duty should not lead to burnout. Engineering managers are responsible for:

- Ensuring no engineer is on primary rotation more than once every 4 weeks (for teams with fewer than 4 members, this may require cross-team coverage arrangements).
- Reviewing on-call load quarterly. If an engineer's after-hours page count exceeds 10 per rotation consistently, the team must invest in reliability improvements.
- Encouraging engineers to take comp time promptly rather than accumulating it.

---

*Version 1.1 — Last revised July 1, 2024*
