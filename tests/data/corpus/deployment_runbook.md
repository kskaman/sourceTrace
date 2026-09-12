---
title: "Deployment Runbook"
category: "Engineering"
doc_type: "runbook"
last_updated: "2024-11-15"
owner: "Engineering"
classification: "Internal"
---

# Deployment Runbook

**Effective Date:** November 15, 2024
**Owner:** Engineering Platform team
**Applies to:** All production deployments for Acme Corp services

---

## 1. Deployment Strategy

Acme Corp uses a blue-green deployment model with canary rollout for all production services.

- **Blue environment:** The current live production environment serving all customer traffic.
- **Green environment:** The standby environment where the new version is deployed and verified before receiving traffic.

A deployment proceeds through three phases: canary, progressive rollout, and full cutover.

## 2. Pre-Deployment Checklist

Before initiating a deployment:

- [ ] All CI checks pass on the release branch (lint, unit tests, integration tests, end-to-end smoke suite).
- [ ] Database migrations (if any) have been applied to the staging environment and verified.
- [ ] The change has been approved through the code review process per the Code Review Guidelines.
- [ ] The deployment is logged in the #deployments Slack channel with: service name, version, deployer, and link to the changelog.
- [ ] Confirm that no active SEV1 or SEV2 incident is in progress. If one is, defer the deployment unless the deployment itself is the incident fix.
- [ ] Confirm the deployment window: standard deployments are allowed Monday–Thursday, 9 AM – 3 PM PT. Friday deployments require Platform team approval.

## 3. Canary Rollout

1. Deploy the new version to the green environment.
2. Run the post-deployment verification suite against the green environment (see Section 6).
3. Route **5% of production traffic** to the green environment via the load balancer.
4. Monitor for 15 minutes. Check:
   - Error rate: must not exceed baseline by more than 0.1%.
   - Latency (p99): must not exceed baseline by more than 50ms.
   - No new error types in Sentry.
   - No anomalous patterns in Datadog dashboards.
5. If metrics are healthy, proceed to progressive rollout.
6. If metrics degrade, trigger an immediate rollback (Section 5).

## 4. Progressive Rollout

After a successful canary phase:

| Step | Traffic to Green | Duration | Gate |
|---|---|---|---|
| 1 | 5% | 15 minutes | Automated metric check |
| 2 | 25% | 15 minutes | Automated metric check |
| 3 | 50% | 15 minutes | Automated metric check |
| 4 | 100% | — | Manual confirmation by deployer |

At each step, the deployment pipeline automatically verifies that error rate and latency remain within tolerance. If any check fails, rollout is paused and the deployer is notified.

The final step (100% cutover) requires the deployer to manually confirm in the deployment dashboard. This prevents unattended full rollouts.

## 5. Rollback Procedure

If a deployment causes degradation at any point:

1. **Immediate rollback:** Click **Rollback** in the deployment dashboard, or run `acme-deploy rollback --service <name>`. This shifts 100% of traffic back to the blue environment within 30 seconds.
2. **Verify rollback:** Confirm that metrics return to baseline within 5 minutes.
3. **Notify:** Post in #deployments and #incidents with the rollback reason.
4. **Investigate:** The deployer opens a post-deployment investigation ticket. Root cause must be identified before re-attempting the deployment.

Rollback is always available for 24 hours after a full cutover. After 24 hours, the blue environment is updated to match green (becoming the new baseline), and rollback to the previous version requires a new deployment.

### Database Migrations and Rollback

Database migrations must be backward-compatible. The previous application version must be able to run against the new database schema. This ensures that a rollback does not require a database rollback (which is risky and slow).

If a migration is not backward-compatible, it must be deployed in two phases:
1. Deploy the migration separately (additive change only — new columns, new tables, no drops).
2. Deploy the application code that uses the new schema.
3. In a subsequent deployment, remove the old columns/tables after confirming no code references them.

## 6. Post-Deployment Verification

After full cutover (100% traffic on green), run the verification suite:

- **Smoke tests:** Automated suite that exercises critical user paths (login, create record, search, export). Must pass within 5 minutes.
- **Synthetic monitoring:** Datadog synthetic checks confirm that key API endpoints respond correctly from multiple geographic locations.
- **Manual spot checks:** The deployer manually verifies 2–3 user-facing flows in production. Document the checks in the deployment log.

If verification fails after full cutover, trigger an immediate rollback.

## 7. Kill Switches

Kill switches allow specific features to be disabled in production without a deployment:

- Kill switches are implemented as feature flags in the configuration service.
- Every new user-facing feature must ship behind a kill switch.
- Kill switches are toggled in the deployment dashboard or via CLI: `acme-config set --flag <name> --value false`.
- The effect is immediate (propagated within 60 seconds via the configuration service).

Kill switches remain in the codebase for 30 days after the feature reaches 100% rollout. After 30 days, the Platform team removes the switch in a cleanup PR.

## 8. Deployment Schedule

| Window | Allowed | Notes |
|---|---|---|
| Monday–Thursday, 9 AM – 3 PM PT | Yes (standard) | No approval required |
| Thursday, 3 PM – Friday EOD | Discouraged | Requires Platform team approval |
| Weekends | Emergency only | Requires VP of Engineering approval |
| During active SEV1/SEV2 | No (unless the deploy is the fix) | Incident commander must approve |

## 9. Contacts

- Deployment issues: #deployments Slack channel
- Platform team: platform-eng@acmecorp.com
- Incident escalation: see the Incident Response Runbook

---

*Version 3.0 — Last revised November 15, 2024*
