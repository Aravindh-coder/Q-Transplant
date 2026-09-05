# Q-Transplant architecture

## Project status

Q-Transplant is a **research/demo prototype**, not a clinically deployed
organ allocation system. It is a decision-support tool: the matching
engine produces compatibility scores, rankings, and explanations. Every
final clinical decision — whether a specific transplant proceeds —
remains with the authorized transplant medical team, never the software.
Donor and patient data in the seeded demo dataset is entirely simulated
(see `seed_donors.py`, `generate_sample_donor_dataset.py`); no real
patient data is used anywhere in this repository. A real deployment would
additionally require authorized data integration with actual hospital
systems, clinical validation, regulatory compliance review, and
institutional approval — none of which this repository provides on its
own.

## Backend

FastAPI, split into configuration (`config.py`), database (`database.py`),
models (`models.py`), security (`security.py`), routers (`routers/`), and
services (`services/`). `main.py` is a composition root: it builds the
app, wires middleware, runs schema bootstrap, and mounts every router.

### Services
- `services/matching_engine.py` — the live, canonical deterministic
  blood/organ/HLA/urgency scoring and ranking pipeline. This is what
  `/api/v1/matching/*` actually calls.
- `services/matching/` — a thin delegating shim over the above, kept so
  the file layout matches the originally-proposed `blood.py / hla.py /
  organ.py / urgency.py / ranking.py / engine.py` structure without
  maintaining two independent implementations of medical scoring logic.
- `services/quantum/` — classical vs. quantum-inspired candidate search,
  a step-traced variant for visualization, a simulator, an optimizer, and
  benchmarks. **This runs on ordinary classical hardware.** It is a
  quantum-*inspired* heuristic (amplitude-amplification-style weighted
  sampling), not real quantum hardware, and the code/UI never claims a
  measured quantum speedup — every comparison result explicitly states
  the classical evaluation count alongside the quantum-inspired one and
  whether it actually found the same top candidate, including when it
  didn't.
- `services/ai_assistant.py` — non-authoritative assistance (plain-
  language summaries, risk flags, a structured "confirmed facts vs. data
  gaps" clinical review). Never re-scores or re-ranks; it can only
  rephrase or flag what the deterministic engine already decided.
- `services/identity_verification.py` — AI-assisted (Groq or Anthropic)
  comparison of a doctor's live registration selfie against their
  submitted certificate photo, surfaced to the organizer as one input
  into manual approval, never an automatic accept/reject.
- `services/case_workflow.py` — the validated transplant-case stage
  machine (`CREATED → MEDICAL_REVIEW → MATCH_SEARCH → CANDIDATE_FOUND →
  DOCTOR_REVIEW → HOSPITAL_COORDINATION → APPROVED_FOR_PROCEDURE →
  PROCEDURE_SCHEDULED → COMPLETED`, plus `CANCELLED`/`ON_HOLD`/`REJECTED`).
  Both `/api/v1/transplants` and hospital_workflow's case endpoints route
  through this same validator, so an invalid stage skip is rejected no
  matter which endpoint is used.
- `services/emergency_state.py` — the validated emergency-request state
  machine used by `routers/emergency.py`.
- `services/realtime.py` — the authenticated, per-user WebSocket event
  bus for live notifications (`/api/v1/notifications/ws`), separate from
  the ESP32 device protocol below.
- `services/object_storage.py` — S3-compatible document storage (falls
  back to local disk if unconfigured — see README_DEPLOYMENT.md for why
  that matters on an ephemeral host like Render).
- `services/notifications.py` — notification persistence, live push, and
  email dispatch.
- `services/mailer.py` — SMTP sender using environment-only credentials;
  every failure mode (not just missing config) degrades gracefully rather
  than crashing whatever request triggered it.
- `services/audit.py` — the audit trail every sensitive action writes to.
- `services/observability.py` — structured application logging with a
  built-in credential/PHI redaction list.

### API
Versioned under `/api/v1`. REST for CRUD; WebSocket for live events
(`/api/v1/notifications/ws` for authenticated per-user push,
`/api/v1/emergency/ws` for the authenticated ESP32 device protocol,
`/api/v1/emergency/public-ws` for the public, read-only landing-page
emergency status feed — which only ever exposes hospital name, status,
and the requirement text, never patient or donor identity).

## Authorized HLA access architecture

**The problem this addresses:** a hospital or doctor should never be able
to browse a complete HLA database, another hospital's full patient list,
or unrestricted donor records. HLA typing is treated as restricted
clinical data throughout this system.

**How it actually works, verified in code (not just documented intent):**

```
Hospital / Doctor
      |
Authorized, role-checked request
(POST /api/v1/matching/run/{patient_id}, POST /api/v1/matching/search)
      |
Backend loads only the caller's OWN hospital's patient
(ownership is re-checked server-side on every request -- never trusted
 from the frontend)
      |
Matching engine internally compares against the donor pool
      |
Response contains a compatibility SCORE + pass/fail flags + an aggregate
matched/total marker COUNT -- never the underlying raw donor or
recipient allele lists
      |
Doctor/hospital reviews ranked, explainable results
      |
Final clinical decision: authorized transplant team, never the software
```

Concretely:
- `evaluate_candidate()` (the function every match result flows through)
  only attaches raw per-locus allele detail (`hla_details`) when a caller
  explicitly opts in with `include_hla_detail=True`. Neither
  `/api/v1/matching/run/{patient_id}` nor `/api/v1/matching/search` do
  this — both return `hla_score` (a number) and `hla_matched_markers` /
  `hla_total_markers` (counts), never the alleles themselves.
- Raw allele-level detail for one specific, named donor/patient pair is
  available **only** through `POST /api/v1/hla/compare/{donor_id}/{patient_id}`,
  which re-checks that the requesting doctor/hospital actually owns that
  patient's hospital record before returning anything, and every access
  is written to the audit log as `SENSITIVE_HLA_DETAIL_ACCESSED`.
  (`POST /api/v1/hla/compare` with typed-in profiles is a different,
  unrestricted case — the caller already possesses both profiles since
  they typed them in; nothing is disclosed there that the caller didn't
  already have.)
- `GET /api/v1/donors/search` and `GET /api/v1/donors` never return
  `hla_a`/`hla_b`/`hla_c`/`hla_dr`/`hla_dq` or `medical_information` at
  all — browsing the donor pool surfaces blood group, organs, and
  availability status only.
- `GET /api/v1/matching/history/{patient_id}` re-checks hospital
  ownership the same way `/run/{patient_id}` does, instead of returning
  any patient's history to any authenticated doctor/hospital.

## Role-based access control

Existing roles, unchanged: `donor`, `doctor`, `hospital`, `organizer`.
One role added this pass: `auditor` — read-only access to
`/api/v1/organizer/audit-log`, nothing else. Auditor accounts are never
self-registered (`/api/v1/auth/register` only ever accepts
donor/doctor/hospital); only an organizer can create one, via
`POST /api/v1/organizer/auditors` — the organizer creating it *is* the
approval, since it grants visibility into every sensitive action across
every hospital in the system.

A `TRANSPORT_OPERATOR` role was considered but **not added**: this
codebase has no GPS/temperature/transport-tracking subsystem to gate
access to (the ESP32 integration here is an emergency-alert device
protocol — button press, LED, buzzer, OLED, acknowledgement — not a
transport telemetry system). Adding a role with nothing real to restrict
would be exactly the kind of unnecessary privilege the access-control
review this document responds to explicitly warns against. If GPS/cold-
chain transport tracking is added later, this is the natural place to
introduce that role with real endpoints to gate.

Every role's actual permissions are enforced via `require_role(...)`
dependencies and explicit ownership lookups **on the backend**, in every
router. The frontend hides/shows UI based on role for usability, but
never a request is ever trusted based on what the frontend would or
wouldn't construct — every test in `test_api_integration.py` that checks
authorization does so by sending the request directly, bypassing the UI
entirely, and confirming the backend rejects it on its own.

## Data ownership model

```
Hospital
  |
DoctorProfile / HospitalProfile (linked via hospital_id)
  |
Patient (hospital_id, doctor_id -- who submitted/owns this recipient)
  |
TransplantCase, MatchRequest, MatchResult (linked to that patient)
```

Donor records are a shared national-style pool (not owned by a single
hospital, matching how real organ-donor registries work) — any
authorized doctor/hospital/organizer can search the active donor pool by
blood group/organ, but never sees a donor's raw HLA typing or medical
notes while browsing (see above). Patients (recipients), transplant
cases, and match history are hospital-owned and access-checked against
that ownership on every request.

## Audit logging

Every sensitive action writes to `AuditLog` (`services/audit.py`):
`user_id`, `action`, `target`, `meta`, timestamp. Includes login/failed
login, registration, document uploads, doctor approval/rejection,
hospital verification, ad-hoc and patient-linked match searches,
`SENSITIVE_HLA_DETAIL_ACCESSED`, match history access, transplant case
creation/transitions, CSV donor imports, and auditor account creation.
Auditors can read this trail; they cannot modify anything.

## Frontend

`app.html` is the authenticated SPA (all four original roles plus
auditor where applicable); `index.html` is the public landing page,
including a live (but read-only, unauthenticated) emergency status feed.
The donor-browsing table in the doctor/hospital/organizer portals no
longer displays an HLA column — raw typing was never meant to be
browsable, and the UI now says so explicitly rather than silently
showing blank fields.

## Route contract (current)

- Public: `/`, `/app.html`, `/donor.html`
- Auth: `/api/v1/auth/*` (register, login, verify-email, forgot/reset-password)
- Donors: `/api/v1/donors/*` (profile, search, CSV import — not available
  to the donor role itself)
- Patients: `/api/v1/patients/*`
- Matching: `/api/v1/matching/run/{patient_id}`, `/api/v1/matching/search`,
  `/api/v1/matching/history/{patient_id}`, `/api/v1/matching/workflow`
- HLA: `/api/v1/hla/compare`, `/api/v1/hla/compare/{donor_id}/{patient_id}`
- Transplant cases: `/api/v1/transplants/*`
- Documents: `/api/v1/documents/*`
- Emergency: `/api/v1/emergency/*` (create/list REST, `/ws` for ESP32,
  `/public-ws` for the public landing-page feed)
- Devices: `/api/v1/devices/*`
- Notifications: `/api/v1/notifications/*` (REST + `/ws`)
- Organizer/admin: `/api/v1/organizer/*` (users, doctors, hospitals,
  transplant cases, emergencies, matching requests, audit-log, auditors)
- Quantum research module: `/api/v1/quantum/*` (isolated benchmarks —
  never on the path a real match result depends on for its ranking)

The SPA uses hash routing so it can be served as a static file with no
server-side rewrite rule required.
