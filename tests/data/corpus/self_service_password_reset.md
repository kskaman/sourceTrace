---
title: "Self-Service Password Reset"
category: "IT"
doc_type: "guide"
last_updated: "2024-06-01"
owner: "IT Operations"
classification: "Internal"
---

# Self-Service Password Reset

**Last Updated:** June 1, 2024
**Applies to:** All Acme Corp employees and contractors with an @acmecorp.com account

## 1. When to Use This Guide

Use the self-service password reset process when:

- Your password has expired (passwords expire every 90 days per the IT Security Policy, Section 4.2.1).
- You have forgotten your password.
- You suspect your password has been compromised.

If you are locked out of your account entirely (cannot complete MFA), contact IT at it-support@acmecorp.com or ext. 9911 for identity-verified account recovery.

## 2. Reset Steps

1. Navigate to **sso.acmecorp.com/reset** from any device with internet access.
2. Enter your Acme Corp email address (@acmecorp.com).
3. Complete the MFA verification. You will be prompted to verify your identity using one of your enrolled MFA methods:
   - Tap your hardware security key.
   - Enter a 6-digit code from your authenticator app.
   - Approve the push notification on Okta Verify.
4. Create a new password that meets the following requirements:
   - Minimum **12 characters**.
   - At least one uppercase letter, one lowercase letter, one number, and one special character.
   - Cannot match any of your **last 10 passwords**.
   - Cannot contain your name or username.
5. Click **Reset Password**. You will be signed out of all active sessions.
6. Sign in with your new password on each device and application.

## 3. After Resetting

- All active sessions (laptop, phone, VPN, browser) are terminated. You will need to sign in again on each device.
- Your new password takes effect immediately. There is no delay.
- If you use a password manager, update the stored entry now.

## 4. Troubleshooting

| Issue | Resolution |
|---|---|
| MFA prompt does not appear | Ensure your device has internet connectivity. Try a different browser. |
| "Password does not meet requirements" | Check the requirements in Step 4. The most common cause is reusing a recent password. |
| Reset link expired | Links expire after 15 minutes. Request a new one from the reset page. |
| Account locked after multiple failed attempts | Wait 30 minutes for the lockout to expire, or contact IT for an immediate unlock. |

## 5. Support

For issues not resolved by this guide, contact IT at it-support@acmecorp.com or Slack #it-help.
