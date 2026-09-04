# Q-Transplant architecture

## Backend
The FastAPI application is intentionally split into configuration, database, models, security, routers and services. `main.py` is an application composition root only: it creates the app, middleware, schema bootstrap and mounts routers.

### Services
- `services/matching/` — deterministic blood/HLA/organ/urgency/ranking/engine pipeline.
- `services/quantum/` — isolated classical and quantum-inspired search, simulator, optimizer and benchmarks.
- `services/ai_assistant.py` — non-authoritative assistance; it cannot override deterministic medical gates.
- `services/emergency_state.py` — validated emergency state machine.
- `services/device_protocol.py` — authenticated ESP32 event envelope.
- `services/realtime.py` — WebSocket event bus.
- `services/notification_service.py` and `services/notifications.py` — notification persistence/dispatch.
- `services/mailer.py` — organizer SMTP sender using environment-only credentials.
- `services/audit.py` — audit trail.

### API
All application APIs are versioned under `/api/v1`. REST is used for CRUD; WebSocket is reserved for live events.

## Frontend
`app.html` remains the visual application/SPA and `index.html` remains the public landing page. The frontend is responsible for presentation, navigation, form/UX validation, API calls, uploads, OTP UI, match visualization, notifications and emergency controls. Medical compatibility/ranking remains backend-authoritative.

## Route contract
- `/`, `/login`, `/register/doctor`, `/register/donor`, `/register/hospital`
- `/doctor`, `/doctor/profile`, `/doctor/patients`, `/doctor/donors`, `/doctor/matching`, `/doctor/search`, `/doctor/import`, `/doctor/emergency`
- `/donor`, `/donor/profile`, `/donor/documents`, `/donor/status`
- `/hospital`, `/hospital/profile`, `/hospital/doctors`, `/hospital/patients`, `/hospital/matching`, `/hospital/search`, `/hospital/import`, `/hospital/emergency`
- `/organizer`, `/organizer/users`, `/organizer/doctors`, `/organizer/approvals`, `/organizer/hospitals`, `/organizer/donors`, `/organizer/patients`, `/organizer/matches`, `/organizer/search`, `/organizer/import`, `/organizer/emergency`, `/organizer/devices`, `/organizer/audit`

The SPA uses hash routes so it can be served as a static file without a server-side rewrite rule.

## Donor verification and hospital association
A donor's own identity (name, phone, address, date of birth, gender) is never exposed to a requesting hospital/doctor -- not through `/donors/search`, `/matching/search`, or `/matching/run/{patient_id}`. Every donor registers through a hospital; that hospital's contact details (name, phone, address, authorized contact) are what a search/match result shows instead, in an `associated_hospital` object.

An organizer must verify a donor before they appear in search or matching results at all. Verification requires two things on file first:
1. `hospital_id` -- a link to an organizer-verified hospital (`GET /hospitals/directory` gives any authenticated role, donor included, a minimal id/name/location list to pick from).
2. `medical_document_id` -- a document uploaded via `POST /documents?kind=medical_document` (or `medical_report`/`medical_certificate`), reviewable by the organizer at `GET /organizer/donors/{id}/review` before calling `POST /organizer/donors/{id}/verify`.

Bulk CSV import (`POST /donors/import`) requires the same `hospital_id` for the whole batch and still leaves every imported donor at `verification_status=pending` -- an organizer must verify each one before they're searchable, same as an individually-registered donor. `seed_donors.py` bypasses this by writing directly to the database with `verification_status="verified"` already set, since it's a local dev/demo seeding script, not something that goes through the API.

Hospital verification has an equivalent gate: `POST /organizer/hospitals/{id}/verify` requires a `license_document_id` on file (uploaded via the `upload_token` issued at registration, `kind=license`) before it succeeds.

## Deployment
Render (see `render.yaml`) runs this as a single web service: FastAPI mounts `public/` as static files at `/` (`app.py`'s `PUBLIC_DIR` resolves to the repo root regardless of working directory), so the API and frontend are served from one origin with no CORS configuration needed for normal use. `Dockerfile` exists for local parity and portability to any other container platform; it is not what Render's native Python buildpack path uses, but running `docker build . && docker run` locally reproduces the same environment.
