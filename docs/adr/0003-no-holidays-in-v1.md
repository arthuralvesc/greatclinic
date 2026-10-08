# 0003. No holidays or doctor time off in v1

Status: accepted (2026-10-05)

## Context

Availability is generated from weekly `doctor_schedules` templates. Holidays, vacations and one-off absences would need an exceptions table and an extra subtraction step in slot generation.

## Decision

v1 has no holiday or time-off model. Rescheduling is also out of scope: the agent cancels and then books.

## Consequences

- Slot generation stays a pure function of the weekly template, existing bookings, and the notice and horizon rules.
- Staff must cancel affected appointments by hand when a doctor is absent.
- A future `schedule_exceptions` table can be added without changing the API, because exceptions only remove slots from the existing output.
