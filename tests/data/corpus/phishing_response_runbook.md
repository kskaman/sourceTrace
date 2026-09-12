---
title: "Phishing Response Runbook"
category: "IT"
doc_type: "runbook"
last_updated: "2024-07-01"
owner: "Information Security"
classification: "Internal"
---

# Phishing Response Runbook

**Effective Date:** July 1, 2024
**Applies to:** All Acme Corp employees

## 1. Recognizing Phishing

Common indicators of a phishing attempt:

- Sender address does not match the displayed name or the expected domain.
- Urgent or threatening language ("your account will be locked," "immediate action required").
- Links that do not match the expected destination (hover to check before clicking).
- Unexpected attachments, especially .zip, .exe, .docm, or .html files.
- Requests for credentials, financial information, or sensitive data via email.

When in doubt, do not click links or open attachments. Proceed to Section 2.

## 2. Reporting

If you receive a suspected phishing email:

1. **Do not click** any links or open any attachments in the message.
2. **Do not reply** to the sender.
3. **Report it** using one of the following methods:
   - Click the "Report Phishing" button in your email client (Outlook or Gmail plugin).
   - Forward the email as an attachment to phishing@acmecorp.com.
   - Post in the #security-incidents Slack channel if the email is time-sensitive or appears to target multiple employees.

The Information Security team triages all phishing reports within 2 hours during business hours and within 4 hours outside business hours.

## 3. If You Clicked a Link or Opened an Attachment

If you clicked a link or opened an attachment before recognizing the phishing attempt:

1. **Disconnect from the network** immediately (disconnect Wi-Fi, unplug Ethernet). Do not shut down the computer — forensic data may be needed.
2. **Call the IT emergency line** at ext. 9911 and describe what happened.
3. **Change your password** from a different, known-safe device.
4. **Do not attempt to investigate** the link or attachment yourself.

IT will assess the impact and guide next steps, which may include a device scan, credential rotation, or device re-imaging.

## 4. Containment (InfoSec Actions)

Upon receiving a confirmed phishing report, the Information Security team:

1. Analyzes the email headers, sender domain, and payload (link or attachment).
2. Checks email logs for other recipients of the same campaign.
3. Blocks the sender domain and any malicious URLs at the email gateway and web proxy.
4. Notifies all recipients who received the phishing email via the #security-incidents Slack channel with guidance.
5. If credentials were compromised, forces a password reset for affected accounts and revokes active sessions.
6. If malware was delivered, isolates affected devices and initiates the incident response process per the Incident Response Runbook.

## 5. Escalation

Phishing incidents are escalated per the severity classification in the Incident Response Runbook:

| Scenario | Severity |
|---|---|
| Phishing reported, no one clicked | SEV4 (Low) |
| One person clicked, no credential entry | SEV3 (Medium) |
| Credentials entered on phishing site | SEV2 (High) |
| Malware executed, lateral movement detected | SEV1 (Critical) |

## 6. Post-Incident

After containment:

- Affected employees receive targeted phishing awareness follow-up within 5 business days.
- The phishing campaign details are added to the security awareness training materials.
- If the incident reaches SEV2 or above, a postmortem is conducted per the Incident Response Runbook.

## 7. Policy Governance

This runbook is maintained by the Information Security team. Questions should be directed to security@acmecorp.com.

---

*Version 1.1 — Last revised July 1, 2024*
