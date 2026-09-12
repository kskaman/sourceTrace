---
title: "ePrivacy Directive Summary — Electronic Communications Privacy"
category: "Compliance"
doc_type: "reference"
last_updated: "2024-09-01"
owner: "Legal"
classification: "Internal"
kb: "regulatory"
---

# ePrivacy Directive — Summary of Key Requirements

**Source Regulation:** Directive 2002/58/EC of the European Parliament and of the Council, as amended by Directive 2009/136/EC (the "ePrivacy Directive" or "Cookie Directive")
**Status:** In force. A proposed ePrivacy Regulation has been under negotiation since 2017 and, if adopted, would replace the Directive. Until the Regulation is finalized, the Directive remains the applicable law, as implemented by each EU member state.
**Scope:** Applies to the processing of personal data in connection with the provision of publicly available electronic communications services in the EU.
**Maintained by:** Acme Corp Legal Department for internal reference

---

## 1. Relationship to GDPR

The ePrivacy Directive is lex specialis to the GDPR — it provides specific rules for electronic communications that supplement and, where applicable, override the more general GDPR provisions. Key interactions:

- Where the ePrivacy Directive addresses a specific matter (cookies, direct marketing, traffic data), its rules apply instead of the GDPR's general rules.
- Where the ePrivacy Directive does not address a matter, the GDPR applies as the general framework.
- The definition of "consent" under the ePrivacy Directive is aligned with the GDPR definition (Article 4(11) and Article 7): freely given, specific, informed, and unambiguous.
- Enforcement of the ePrivacy Directive is typically handled by the same national data protection authorities (DPAs) that enforce the GDPR, though some member states designate a separate telecommunications authority.

---

## 2. Cookie Consent Rules (Article 5(3))

### The Consent Requirement

The storage of information, or the gaining of access to information already stored, in the terminal equipment of a subscriber or user (i.e., setting cookies or accessing cookies) is **only allowed on condition that** the subscriber or user:

1. Has been provided with **clear and comprehensive information** about the purposes of the processing, in accordance with the GDPR; AND
2. Has **given their consent** to the storage or access.

This is an **opt-in** requirement: consent must be obtained **before** cookies are stored on the user's device. Pre-checked boxes, implied consent (e.g., "by continuing to browse this site you agree"), and consent buried in terms and conditions do not meet the standard.

### Exceptions to the Consent Requirement

Consent is **not required** for cookies that are:

- **Strictly necessary** for the provision of a service explicitly requested by the user. Examples:
  - Session cookies for maintaining a user's login state.
  - Shopping cart cookies on an e-commerce site.
  - Load-balancing cookies.
  - Security cookies (CSRF tokens).
  - Cookies that remember a user's cookie consent choice.

- **Technically necessary** for carrying out the transmission of a communication over an electronic communications network.

All other cookies — including analytics cookies, functional/preference cookies, and marketing/advertising cookies — require prior consent.

### Granularity of Consent

EDPB and national DPA guidance (notably the French CNIL and the German DSK) has established that:

- Consent must be **granular**: users must be able to consent to individual categories of cookies rather than being forced to accept all or none.
- A "cookie wall" (blocking access to the site unless all cookies are accepted) is generally not considered freely given consent, unless a genuine alternative means of accessing the service is available.
- The user must be able to **withdraw consent** as easily as they gave it.
- Consent must be **renewed** at appropriate intervals. The CNIL recommends renewing consent every **13 months**.

### Information Requirements

Before consent is obtained, the user must be informed of:

- The identity of the party setting each cookie (first-party vs. third-party).
- The purpose of each cookie or category of cookies.
- The duration (session vs. persistent, and specific expiry).
- Whether the data is shared with third parties and, if so, which ones.

This information is typically provided in a cookie policy, accessible from the consent banner.

---

## 3. Confidentiality of Communications (Article 5(1))

Member states must ensure the confidentiality of electronic communications and related traffic data. Specifically:

- Listening to, tapping, storing, or otherwise intercepting or surveilling communications and related traffic data by persons other than users is prohibited, without the consent of the users concerned.
- This does not prevent technical storage that is necessary for the conveyance of a communication (e.g., email servers temporarily storing messages in transit).

Exceptions: lawful interception authorized by national law in accordance with Article 15(1), which allows member states to restrict the scope of confidentiality for national security, defense, public security, or the prevention, investigation, detection, and prosecution of criminal offenses.

---

## 4. Direct Marketing (Article 13)

### Electronic Marketing Requires Prior Consent

The use of electronic communications systems for direct marketing purposes (email, SMS, automated calling machines, push notifications) requires the **prior consent** of the subscriber or user.

### Soft Opt-In Exception

A narrower consent requirement applies when:

1. The sender obtained the contact details in the context of a sale of a product or service.
2. The marketing relates to the sender's own similar products or services.
3. The recipient was clearly given the opportunity to object (opt out) at the time of data collection and in each subsequent message.
4. The recipient has not objected.

Under the soft opt-in, explicit prior consent is not required, but an easy opt-out must be provided in every message.

### Identification and Opt-Out

Every direct marketing communication must:

- Clearly identify the sender.
- Provide a valid opt-out mechanism (e.g., unsubscribe link in email).
- Include the sender's contact information.

Marketing messages that disguise or conceal the identity of the sender, or that do not provide an opt-out mechanism, are prohibited.

---

## 5. Traffic Data and Location Data (Articles 6 and 9)

- **Traffic data** (data processed for the conveyance of a communication: source, destination, date, time, duration, type of communication) must be erased or anonymized when no longer needed for the transmission, unless retained for billing purposes or with user consent for marketing or value-added services.
- **Location data** (data indicating the geographic position of a user's device) may only be processed with the user's consent for value-added services, and the user must be able to withdraw consent at any time.

---

## 6. National Implementation Variations

Because the ePrivacy Directive is a directive (not a regulation), it is implemented through national law in each EU member state. This leads to variations:

| Member State | Key Variation |
|---|---|
| France (CNIL) | Cookie consent must be renewed every 13 months. Cookie walls are prohibited unless a genuine free alternative exists. |
| Germany (TTDSG) | The Telecommunications-Telemedia Data Protection Act transposes Article 5(3). Strict consent requirement for all non-essential cookies. |
| Italy (Garante) | Scroll-based consent (treating scrolling as consent) is not valid. Consent must be an affirmative action. |
| Spain (AEPD) | Analytics cookies require consent; no exception for "anonymous" analytics. |
| Netherlands (AP) | Analytics cookies that are privacy-friendly (first-party, no cross-site tracking, aggregated) may be placed without consent under a regulatory exception. |

**Operational note:** Acme Corp serves customers across multiple EU member states. The cookie consent implementation should comply with the strictest national interpretation to avoid maintaining per-country logic. The CNIL's 13-month renewal requirement is a good baseline.

---

## 7. Enforcement and Penalties

Enforcement is handled by national DPAs or designated telecommunications authorities. Penalties vary by member state, as the Directive sets no specific fine amounts. In practice:

- The CNIL (France) has imposed fines of up to €150 million for cookie consent violations (e.g., the 2022 Google/Facebook decisions).
- The GDPR's fine framework (up to €20 million or 4% of global turnover) may apply to consent-related violations where the GDPR's consent rules are engaged alongside the ePrivacy Directive.

---

*This summary was prepared by the Acme Corp Legal Department for internal reference. Last revised September 1, 2024. For questions, contact legal@acmecorp.com.*
