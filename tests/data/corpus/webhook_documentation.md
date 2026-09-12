---
title: "Webhook Documentation"
category: "Product"
doc_type: "guide"
last_updated: "2024-10-01"
owner: "Engineering"
classification: "Public"
---

# Webhook Documentation

**Last Updated:** October 1, 2024

Webhooks allow your application to receive real-time notifications when events occur in Acme Corp. Instead of polling the API, register a webhook endpoint and Acme Corp will push events to you as they happen.

## 1. Supported Events

| Event | Trigger |
|---|---|
| `record.created` | A new record is created |
| `record.updated` | A record's content, tags, or metadata is modified |
| `record.deleted` | A record is soft-deleted |
| `record.restored` | A previously deleted record is restored |
| `user.invited` | A new user invitation is sent |
| `user.removed` | A user is removed from the account |
| `user.role_changed` | A user's role is updated |
| `export.completed` | A bulk data export finishes processing |

Subscribe to specific events when registering a webhook, or use `*` to receive all events (not recommended for high-volume accounts).

## 2. Payload Structure

Every webhook delivery is an HTTP `POST` with a JSON body:

```json
{
  "id": "evt_m3n4o5p6",
  "type": "record.updated",
  "created_at": "2025-01-15T10:40:00Z",
  "account_id": "acct_a1b2c3",
  "data": {
    "record_id": "rec_x7y8z9",
    "changes": ["content", "tags"],
    "updated_by": "user_d4e5f6"
  }
}
```

The `data` field varies by event type. Each event type's schema is documented in the API Reference Guide under the Webhooks section.

## 3. Signature Verification

Every delivery includes an `X-Acme-Signature` header containing an HMAC-SHA256 signature of the raw request body, computed using your webhook secret:

```
X-Acme-Signature: sha256=a1b2c3d4e5f6...
```

To verify:

1. Read the raw request body (before JSON parsing).
2. Compute HMAC-SHA256 of the body using your webhook secret as the key.
3. Compare the computed signature to the value in `X-Acme-Signature` using a constant-time comparison function.
4. Reject the request if the signatures do not match.

Never skip signature verification in production. Without it, any party that knows your endpoint URL can send forged events.

## 4. Retry Behavior

If your endpoint does not respond with a `2xx` status code within 10 seconds, the delivery is retried with exponential backoff:

| Attempt | Delay After Previous Attempt |
|---|---|
| 1 (initial) | Immediate |
| 2 | 10 seconds |
| 3 | 30 seconds |
| 4 | 90 seconds |
| 5 | 270 seconds (~4.5 min) |
| 6 (final) | 810 seconds (~13.5 min) |

After 6 failed attempts (approximately 20 minutes total), the delivery is marked as failed. If a webhook accumulates 50 consecutive failed deliveries, it is automatically disabled and an email notification is sent to the account owner.

## 5. Idempotency

Your endpoint may receive the same event more than once (due to retries or rare internal duplication). Use the `id` field in the payload to deduplicate. If you have already processed an event with a given ID, return `200 OK` without reprocessing.

## 6. Managing Webhooks

- **Register:** `POST /v2/webhooks` (see the API Reference Guide).
- **List:** `GET /v2/webhooks` — returns all active webhooks.
- **Delete:** `DELETE /v2/webhooks/{webhook_id}` — removes the subscription and cancels pending deliveries.
- **Delivery log:** Available in the admin console under **Settings > API > Webhooks > Delivery Log**. Each entry shows the event, delivery status, HTTP response code, latency, and retry history.

## 7. Best Practices

- Respond quickly. Process the event asynchronously (queue it) and return `200 OK` within 1–2 seconds. Long-running processing during the request risks timeouts.
- Use signature verification. Always.
- Implement idempotency. Retries are normal.
- Monitor your delivery log. A rising failure rate usually means your endpoint is unhealthy.
- Use HTTPS. Webhook URLs must use `https://`. Plain HTTP endpoints are rejected at registration.

---

*Questions about webhooks: api-support@acmecorp.com or the API Reference Guide.*
