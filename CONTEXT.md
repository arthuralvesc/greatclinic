# CONTEXT

Domain glossary and settled decisions for the GreatClinic scheduling backend. Technical conventions live in `CLAUDE.md`; this file holds the language and the business decisions.

## Glossary

- **Patient**: a person identified by their **phone** (E.164, unique). Phone is the primary lookup key.
- **Doctor**: a practitioner with a unique CRM and exactly one **Specialty**.
- **Specialty**: a medical field, such as Cardiology.
- **Schedule window**: a recurring working-hour template for a doctor on a weekday (`day_of_week`, 0 = Sunday), in clinic local time. A doctor may have several non-overlapping windows per weekday, for example to model lunch.
- **Slot**: a bookable interval generated from schedule windows, `SLOT_DURATION_MINUTES` long. The slot grid is the only set of valid booking start times.
- **Appointment**: a patient's booking with a doctor at a UTC `date_time`. It stores its own `duration_minutes`.
- **Active appointment**: status `PENDING` or `CONFIRMED`. Only active appointments block slots.
- **Minimum notice**: the smallest gap between now and a booking (`MIN_BOOKING_NOTICE_MINUTES`).
- **Booking horizon**: the furthest-out booking allowed (`MAX_BOOKING_ADVANCE_DAYS`, default 90).
- **Caller**: the person on the voice call. The Voice AI Agent identifies them by phone.

## Settled decisions

### Booking
- Appointments are created as `CONFIRMED`. A confirmation-link flow (`PENDING` until the patient confirms) is planned for later.
- `dateTime` must equal a generated slot start. Anything else returns 422 `INVALID_SLOT`, covering misaligned times, windows that don't fit, and days with no schedule. There is no separate `OUTSIDE_WORKING_HOURS` code.
- `duration_minutes` is stored per appointment, so changing `SLOT_DURATION_MINUTES` later doesn't corrupt existing bookings. Availability subtracts real intervals. The partial unique index on `(doctor_id, date_time)` stays as the race guard.
- Bookings beyond `MAX_BOOKING_ADVANCE_DAYS` return 422 `BEYOND_BOOKING_HORIZON`.
- A patient may not hold overlapping active appointments, even with different doctors: 409 `PATIENT_TIME_CONFLICT`.
- A patient may have at most 5 active future appointments (configurable): 422 `BOOKING_LIMIT_REACHED`.

### Retry safety
- If the active appointment at that doctor and time already belongs to the same patient, `POST /appointments` returns it with 200. No idempotency-key header is used. A different patient gets 409 `SLOT_UNAVAILABLE`.

### Cancellation
- The request carries `patientId`. A mismatch returns 404 `APPOINTMENT_NOT_FOUND`, so the existence of other patients' appointments isn't revealed.
- A future appointment can be cancelled at any time, with no cancellation notice.
- A past appointment returns 422 `APPOINTMENT_IN_PAST`. Already cancelled or completed appointments return 422 as before.

### Scope
- Holidays and doctor time off are out of scope for v1.
- Rescheduling is not offered. The agent cancels, then books.

### Patients
- Registration: malformed phone, future or implausible (>120 years) `birthDate`, and blank name return 400 `VALIDATION_ERROR`. A duplicate phone returns 409 `PHONE_ALREADY_REGISTERED` and a duplicate email returns 409 `EMAIL_ALREADY_REGISTERED`. If both clash, the phone code wins.
- Any valid E.164 number is accepted. `BR` is only the default region when the input has no `+`.
- Lookup with an unparseable phone returns 400 `INVALID_PHONE`. "Always 200" applies only to well-formed phones.

### Reads
- `GET /patients/{patientId}/appointments` defaults to upcoming active appointments (`PENDING`/`CONFIRMED`, `date_time >= now`), ascending. An explicit `status` returns all matching appointments, past included. Each item includes `doctor: { id, name, specialty }`. Capped at 50, no pagination in v1.
- Unknown `patientId` or `doctorId` returns 404 `PATIENT_NOT_FOUND` / `DOCTOR_NOT_FOUND`, on booking and on available-slots.
- Available-slots for a known doctor with no schedule that day, a past date, or a date beyond the horizon returns 200 with `availableSlots: []`.

### Observability
- Structured JSON logs: request ID, method, route template (never the raw URL, since `?phone=` is in the query string), status, error code, latency. Request and response bodies are never logged. UUIDs are logged in full. Any phone in an application log line is masked.
- `X-Request-ID` is accepted if present (short validated string), otherwise generated. It is echoed in the response header and added to error bodies as `requestId`.

### Seed and tests
- `scripts/seed.py` is deterministic and idempotent (upsert by CRM or name, fixed UUIDs): 3 specialties, 6 doctors, windows 09–12 and 14–18 on weekdays, one doctor also working Saturday mornings. For local development and demos only.
- E2E tests do not use the seed. They build data with factories inside rolled-back transactions.

## ADRs
- `docs/adr/0001-per-appointment-duration.md`
- `docs/adr/0002-booking-retry-returns-existing.md`
- `docs/adr/0003-no-holidays-in-v1.md`

## Open items
None. `CLAUDE.md` reflects all decisions above.
