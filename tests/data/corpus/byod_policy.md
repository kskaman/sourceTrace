---
title: "BYOD Policy"
category: "IT"
doc_type: "policy"
last_updated: "2023-08-01"
owner: "IT Operations"
classification: "Internal"
---

# Bring Your Own Device (BYOD) Policy

**Effective Date:** August 1, 2023
**Applies to:** All Acme Corp employees and contractors who wish to use personal devices for work

## 1. Eligibility

Employees and contractors may use personal devices (smartphones, tablets, laptops) to access Acme Corp systems, provided the devices are enrolled in the company's Mobile Device Management (MDM) program.

Enrollment is voluntary. Employees who do not wish to enroll personal devices must use company-issued equipment exclusively.

## 2. MDM Enrollment

Before accessing any company system from a personal device, users must:

1. Install the MDM agent (Jamf for macOS/iOS, Microsoft Intune for Windows/Android) from the IT self-service portal.
2. Complete the enrollment process, which configures security policies on the device.
3. Pass the device posture check: OS version must be within two major versions of current, disk encryption must be enabled, and a screen lock must be active.

Enrollment typically takes 10–15 minutes. IT can assist during office hours or via the #it-help Slack channel.

## 3. Security Requirements for Enrolled Devices

Enrolled personal devices must maintain:

- Full disk encryption (FileVault, BitLocker, or Android encryption).
- A screen lock with a PIN, password, or biometric authentication, activating after no more than 5 minutes of inactivity.
- The MDM agent installed and active at all times.
- Operating system updates applied within 14 days of release.
- No jailbroken or rooted operating systems.

Devices that fall out of compliance are automatically blocked from accessing company systems until the issue is resolved.

## 4. Data Handling

- Company data accessed on personal devices is subject to the same classification and handling rules as data on company-managed devices (see the Data Classification Policy).
- Users must not store Restricted data locally on personal devices. Restricted data should be accessed only through company-managed applications and cloud services.
- Confidential data may be cached locally by approved applications (e.g., email, Slack) but must be encrypted by the application.

## 5. Data Wiping on Separation

When an employee or contractor separates from Acme Corp:

- The MDM profile and all company-managed applications are remotely removed from the personal device.
- Company data within managed applications (email accounts, managed app data, VPN configuration) is wiped.
- Personal data, photos, and non-managed applications are not affected.

Users are notified before the remote wipe is initiated. If the device is lost or stolen, IT may perform a selective wipe without advance notice.

## 6. Privacy

Acme Corp's MDM program has visibility into:

- Device model, OS version, and encryption status.
- Installed managed applications.
- Compliance status (posture checks).

The MDM program does **not** have visibility into:

- Personal email, messages, or photos.
- Browsing history.
- Non-managed applications.
- Device location (location tracking is disabled in the MDM configuration).

## 7. Policy Governance

This policy is administered by IT Operations. Questions should be directed to it-support@acmecorp.com.

---

*Version 1.1 — Last revised August 1, 2023*
