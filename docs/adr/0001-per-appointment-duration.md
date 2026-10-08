# 0001. Store duration on each appointment

Status: accepted (2026-10-05)

## Context

Slot length comes from `SLOT_DURATION_MINUTES`. If appointments stored only a start time, changing that setting (30 to 20 minutes, say) would leave existing 30-minute bookings misaligned with the new grid and blocking the wrong slots.

## Decision

`appointments` has a `duration_minutes` column, copied from `SLOT_DURATION_MINUTES` when the booking is made. Availability removes every slot that overlaps an active appointment's interval (`date_time` to `date_time + duration_minutes`), not just slots with an equal start.

The partial unique index on `(doctor_id, date_time)` stays as the race guard for identical start times. Overlaps between different start times are caught by the pre-insert interval check.

## Consequences

- One extra column and an interval-overlap query instead of an equality match.
- Changing the slot duration is safe for existing data.
- The overlap check between different start times is not enforced by the database. If this becomes a problem, consider an exclusion constraint on `tstzrange`.
