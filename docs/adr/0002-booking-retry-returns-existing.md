# 0002. A booking retry by the same patient returns the existing appointment

Status: accepted (2026-10-05)

## Context

The Voice AI Agent retries on timeouts. If `POST /appointments` succeeded but the response was lost, the retry would get 409 `SLOT_UNAVAILABLE` for the patient's own slot, and the agent would wrongly tell the caller the slot was taken.

## Decision

If the active appointment at the requested doctor and time belongs to the same patient, `POST /appointments` returns it with `200` (a new booking returns `201`). A different patient still gets 409 `SLOT_UNAVAILABLE`. No idempotency-key header is used.

## Consequences

- Retries are safe without any client-side bookkeeping.
- The same-patient check must also run after catching the unique-index `IntegrityError`, so two concurrent identical requests from one patient both succeed instead of one failing.
- Two deliberate bookings of the same slot by the same patient are indistinguishable from a retry. This is acceptable because a patient cannot hold overlapping appointments anyway.
