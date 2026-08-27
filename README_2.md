# Q-Transplant — Full Package

## Latest update: video on landing only, spatial 3D restored on the app, organizer + FAQ replacing the bio section

**`index.html` (landing page)** — background is `heart_animation.mp4` only.
No Three.js on this page anymore.

**`app.html` (login + dashboards)** — back to the Three.js spatial
background: a rotating heart with orbiting organs on the role-select,
login, donor, and doctor screens; a live wireframe hospital-network globe
(same spinning-globe treatment as Kisan Vision's hero) on the hospital and
organizer screens. No video on this file — keeps it lightweight since it's
already doing a lot of UI work.

**`heart_animation.mp4` must sit next to `index.html`** (relative path
reference) — `app.html` no longer needs it.

**Landing page content**: the personal "Innovator" bio section is gone.
In its place: an **Organizer** block (name + contact email only, no bio/tags/
portfolio mentions) and a **FAQ** accordion covering the deterministic
rule engine, emergency alert latency, doctor approval gating, and the
quantum-inspired search's honest scope.

---

## `backend.zip` — production backend

A real FastAPI service — not a mockup. Every endpoint below was actually run
end-to-end during development (register → approve → login → profile →
patient → match → stats → audit), and two real bugs were caught and fixed
in the process:

1. **`passlib`'s bcrypt backend is broken against modern `bcrypt` releases**
   (a genuine upstream incompatibility, not specific to this project) — the
   code now calls `bcrypt` directly instead.
2. **Doctor approval had a chicken-and-egg bug**: a pending doctor couldn't
   log in to create their profile, so the organizer could never see them to
   approve. Fixed by capturing license/hospital info atomically at
   registration, so the organizer's approval queue is populated immediately.
3. **Several endpoints were silently returning `{}`** — FastAPI in this
   environment doesn't auto-serialize raw SQLAlchemy objects. Added a
   `to_dict`/`to_dict_list` helper (`app/utils.py`) and applied it across
   every router that returns model data, with a credential-hash exclusion
   list so hashed device tokens never leave the server even in list views.

### What's inside
```
backend/
  app/
    main.py              — FastAPI app, wires every router, CORS, table creation
    config.py             — all settings from environment variables
    database.py            — SQLAlchemy engine/session
    models.py               — full schema: User, DonorProfile, DoctorProfile,
                               HospitalProfile, Patient, TransplantCase,
                               MatchRequest/Result, EmergencyRequest, Device,
                               Document, Notification, OTP, AuditLog
    security.py              — bcrypt hashing, JWT, role-based dependencies,
                                in-memory rate limiter
    utils.py                  — ORM -> dict serialization helper
    routers/
      auth.py                  — register / login / forgot-password OTP
                                  (emails from aravindhjoshua10@gmail.com) /
                                  reset-password
      donors.py, doctors.py, hospitals.py, patients.py  — CRUD scoped to role
      matching.py               — runs the deterministic engine, persists
                                   MatchRequest/MatchResult, audit-logs it
      organizer.py               — doctor approvals, user suspend/reactivate,
                                    hospital verification, live stats, audit log
      devices.py                  — ESP32 device provisioning (token shown once)
      emergency.py                  — WebSocket hub, DB-backed version of the
                                       earlier prototype, same wire format
    services/
      compatibility.py             — deterministic blood-group + organ rules
      hla.py                        — structured, weighted HLA scoring
      urgency.py                     — transparent priority engine
      matching_engine.py              — full pipeline: filter → blood → organ
                                         → HLA → urgency → rank → explain
      quantum/search.py, benchmark.py  — isolated quantum-inspired search +
                                          honest classical-vs-quantum-inspired
                                          benchmark (no speedup claims)
      notifications.py, audit.py, mailer.py
  requirements.txt
  .env.example
```

### Run it
```bash
cd backend
pip install -r requirements.txt --break-system-packages
cp .env.example .env   # fill in ORGANIZER_APP_PASSWORD (Gmail App Password) and JWT_SECRET
uvicorn app.main:app --reload --port 8000
```
Interactive API docs: `http://localhost:8000/docs`

There's no self-registration for the organizer role by design (matches the
original spec — organizer credentials are provisioned, not signed up for).
Seed one directly:
```python
from app.database import SessionLocal
from app.models import User
from app.security import hash_password
db = SessionLocal()
db.add(User(email="you@example.com", hashed_password=hash_password("choose-a-password"), role="organizer", status="active"))
db.commit()
```

### Rule engine, honestly
- `compatibility.py` — pure, deterministic, independently testable. No AI
  model touches blood-group or organ-type logic. Verified: O- is a universal
  donor, AB+ cannot donate to O-, mismatched organ types are rejected.
- `hla.py` — locus-by-locus scoring with configurable weights (HLA-DR
  weighted highest, matching clinical convention), every score shows its
  work rather than returning a bare number.
- `quantum/` — the benchmark was actually run: on pool sizes from 50 to
  3,000, the quantum-inspired heuristic used roughly 0–12% fewer evaluations
  than classical search and did *not* always find the same optimum. That's
  reported as-is — no inflated "quantum speedup" claim, per the original
  spec's explicit instruction not to.

### What's still a stub
- Document upload (`Document` model exists; no file storage endpoint yet —
  wire to S3/local disk + antivirus scan before accepting uploads in prod).
- `TransplantCase` stage transitions have the model and enum but no router
  yet driving CREATED → ... → COMPLETED.
- AI-generated natural-language match explanations (`ai_explain` hook exists
  in `matching_engine.run_match` — plug in a Groq/Gemini/Claude call).

---

## `app.html` — login, role dashboards (earlier drop, still current)
Standalone SPA: role-select → login/register/forgot-password (OTP) → four
dashboards (Donor, Doctor, Hospital, Organizer), persistent 3D background
(rotating heart + orbiting organs; a hospital-network globe on
hospital/organizer views). Demo-mode by default — see the file's inline
comments for which `fetch` calls to point at the real backend above.

## `index.html` — public landing page (earlier drop, still current)
Marketing page: hero, about, workflow, innovator bio, contact, plus the
original client-side emergency-network demo with sound design.

## `esp32_emergency_firmware.ino`
ESP32 firmware — WiFi + WebSocket client targeting
`backend/app/routers/emergency.py`'s `/api/v1/emergency/ws`, OLED live
requirement display, three buttons, three buzzer patterns.

## Deploying for real
1. `backend/` behind Postgres (`DATABASE_URL` in `.env`) and HTTPS/WSS.
2. Serve `index.html` / `app.html` (or their React port) from a static host
   or Vite build, pointed at the deployed backend's origin, with that origin
   added to `ALLOWED_ORIGINS`.
3. Flash `esp32_emergency_firmware.ino` per hospital using a token from
   `POST /api/v1/devices/provision`.
4. Rotate `JWT_SECRET` and the Gmail app password into real secret storage
   (not `.env` in source control) before going live.
