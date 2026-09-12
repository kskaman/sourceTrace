---
title: "Laptop Security Requirements"
category: "IT"
doc_type: "policy"
last_updated: "2024-01-15"
owner: "IT Operations"
classification: "Internal"
---

# Laptop Security Requirements

**Effective Date:** January 15, 2024
**Applies to:** All Acme Corp-issued laptops and workstations

## 1. Full Disk Encryption

All company-issued laptops must have full disk encryption enabled:

- **macOS:** FileVault 2. IT enables this during device provisioning. Do not disable FileVault.
- **Windows:** BitLocker with TPM. IT enables this during device provisioning. Do not disable BitLocker.
- **Linux:** LUKS encryption on the root partition. Configured during IT provisioning.

Recovery keys are escrowed in the company's device management system. If you forget your disk encryption password, contact IT for recovery.

## 2. Screen Lock

Devices must lock automatically after 5 minutes of inactivity. The screen lock must require the user's password, PIN, or biometric authentication to unlock.

Do not disable the screen lock or extend the timeout. Manually lock your device (Cmd+Ctrl+Q on macOS, Win+L on Windows) when stepping away from your desk.

## 3. Endpoint Agent

The company's endpoint detection and response (EDR) agent must be installed and active at all times. The EDR agent:

- Monitors for malware, ransomware, and suspicious process activity.
- Reports device posture to the VPN and MDM systems.
- Is required for VPN connection and access to internal systems.

If the EDR agent is stopped, quarantined, or uninstalled, the device is automatically blocked from the corporate network. Contact IT to resolve agent issues.

## 4. Software Updates

Automatic OS and application updates must be enabled. Critical security updates are pushed by IT and must be installed within 48 hours of delivery. A restart may be required; IT will notify you if a forced restart is scheduled.

## 5. Loss or Theft Reporting

If your laptop is lost or stolen:

1. Report the loss immediately to IT at it-support@acmecorp.com and by calling the IT emergency line at ext. 9911.
2. IT will remotely lock and, if necessary, remotely wipe the device.
3. File a report with local law enforcement if the device was stolen.
4. Notify your manager.

Time is critical. Reporting within 1 hour of discovery enables IT to lock the device before credentials or data may be compromised.

## 6. Prohibited Modifications

Users must not:

- Disable or circumvent any security feature (encryption, EDR, screen lock, firewall).
- Install operating systems not provisioned by IT.
- Connect the laptop to unauthorized networks without VPN protection.
- Physically open the device casing or modify hardware.

## 7. Policy Governance

This document is maintained by IT Operations. Questions should be directed to it-support@acmecorp.com.

---

*Version 2.0 — Last revised January 15, 2024*
