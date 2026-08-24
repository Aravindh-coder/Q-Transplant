# Q-TRANSPLANT — Master Build Prompt

Use this as a complete specification to build, extend, or explain the Q-Transplant platform — an AI/IoT-powered national organ transplant coordination system.

---

## 1. Vision

Build a real-time, quantum-search-inspired platform that connects hospitals, doctors, and physical organ transport hardware into a single coordination network — so that when a patient urgently needs an organ, the system finds the best-matching donor across the entire hospital network in seconds, not phone calls, and tracks the organ's journey from donor hospital to recipient in real time.

**Core promise:** emergency raised → best-match donor found → live ETA shown → organ tracked in transit → handoff acknowledged. End to end, automated, auditable.

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy ORM, Alembic migrations, Pydantic v2, JWT auth (python-jose), bcrypt password hashing |
| Database | SQLite (dev) / swappable to Postgres via `DATABASE_URL` |
| Frontend | Vanilla JS (ES modules) + Vite, no framework — hand-rolled SPA router, Carbon-Design-inspired CSS classes (`bx--*`) |
| Hardware | ESP32 DevKit, Arduino/PlatformIO firmware, SSD1306 OLED, HTTPClient + ArduinoJson |
| Infra | Docker + docker-compose, Kubernetes manifests, Nginx reverse proxy |
| Real-time | Polling-based state sync (`/emergency/current-state`) — WebSocket router (`ws.py`) also present for push-based updates |

---

## 3. User Roles

1. **Organizer / Admin** — national-level oversight: GIS Command Center, blockchain audit trail, federated learning dashboard, full hospital network visibility
2. **Hospital** — manages its own ICU bed count, blood inventory, patient/organ records, raises emergencies, confirms donor availability
3. **Doctor** — registers donors (individually or via bulk CSV), searches the donor pool against a specific patient's medical profile, manages transplant workflows
4. **Cold-box hardware (ESP32)** — non-human "actor": a physical device on the organ transport container with three buttons (Emergency / Donor Available / Acknowledge), an OLED status display, LEDs, and a buzzer for audible alerts. Streams telemetry (temp/humidity/battery/GPS) every 4 seconds.

---

## 4. Core Modules

### 4.1 Emergency & Quantum Match Pipeline (`/api/v1/emergency`)
A single global state machine (`IDLE → SEARCHING → DONOR_MATCHED → ACKNOWLEDGED → IDLE`) that any hospital or ESP32 device can drive.

- `POST /dispatch` — ESP32 or hardware-simulated emergency trigger. Payload: `hospital_name, organ_type, blood_type, hla_type, patient_age, cold_box_id`
- `POST /` — same as above but from a web form (`EmergencyOut` pydantic model)
- `POST /donor-available` — another hospital confirms it has a matching organ. Triggers:
  - Hospital directory lookup (real lat/lng per hospital name, fuzzy-matched)
  - Haversine distance calculation between requesting and donor hospital
  - ETA estimate (green-corridor ambulance avg. speed ~45–50 km/h)
  - Auto-generated hospital "photo" (initials avatar) for both hospitals
- `POST /acknowledge` — hospital crew confirms handoff; stops the siren, resets state
- `POST /reset` — manual reset to IDLE
- `GET /current-state` — polled by the frontend every ~2s to drive UI + sound triggers
- `GET /`, `GET /{event_id}` — historical emergency event log

**Hospital directory** (`HOSPITAL_DIRECTORY` in `emergency.py`): static dict of real hospital names → `{city, lat, lng, phone, color}`, used for both the emergency ETA calc and the DB seed list — keep these two lists in sync when adding hospitals.

### 4.2 Donor Search — Grover's-Algorithm-Styled Matching (`/api/v1/donor-search`)
Separate from the emergency pipeline — this is the doctor-facing bulk search tool.

- In-memory donor pool (swap to a DB table for production persistence)
- `POST /seed-demo?count=1000` — generate synthetic donors for demo/testing
- `POST /upload-csv` — doctors upload real donor records; flexible column-name matching (`donor_name`/`name`, `blood_type`/`blood_group`, etc.) so real-world hospital exports work without reformatting
- `GET /pool-stats` — pool size + breakdown by organ type / blood type
- `DELETE /pool` — clear pool (demo reset)
- `POST /search` — the core matcher:
  - Filters by organ type match
  - Scores: **40% HLA similarity + 25% urgency + 20% ischemia-time decay + 15% distance**, zeroed out entirely if ABO-incompatible
  - Returns ranked top-N plus **Grover's algorithm metadata**: `grover_iterations = round((π/4)·√N)`, `quantum_ops = √N`, `classical_ops = N`, `speedup_factor` — used to drive the frontend's live search animation pacing, framing the search as a quantum-inspired amplitude-amplification process even though the actual scoring is classical (this is a deliberate visualization/narrative choice for the hackathon framing — be upfront about this if asked how "quantum" it really is)

### 4.3 GIS National Command Center (`/api/v1/gis`)
Live map of the hospital network: hospital nodes with ICU bed availability, ambulance/transport tracking, active matches. Backed by real `Hospital`, `ICUOccupancy`, `BloodInventory` DB tables — **not** the in-memory `HOSPITAL_DIRECTORY` (keep this distinction in mind: emergency ETA lookups and GIS map data are two separate sources that happen to overlap in hospital names).

### 4.4 Quantum Organ Matching Engine (`services/quantum_matching.py`)
A more detailed per-organ matching computation (separate from the bulk donor-search scorer) used by the `matching` dashboard tab — compares a specific organ record against a specific patient with a fuller compatibility breakdown.

### 4.5 Supporting modules present in the repo
- **Blockchain Audit** (`audit.py`) — tamper-evident event log
- **AI Risk Prediction** — flags transplant risk factors
- **Digital Twin Transport** — simulated transport modeling
- **Federated Learning** — cross-hospital model training without sharing raw patient data
- **Multi-Agent System** — coordinating agents across the network
- **Autonomous AI Coordinator** — orchestration layer
- **Live Transport Tracking** — real-time cold-box GPS
- **Slime Mould vs Q-SMA / Synthetic Data Lab** — research/comparison tooling

> If any of these are placeholder/UI-only, say so explicitly rather than presenting them as fully wired — check each router's actual implementation depth before claiming functionality in a demo or pitch.

---

## 5. Data Models (`backend/app/models/domain.py`)

Key tables: `User` (role-based: organizer/hospital/doctor), `Hospital` (name, license, city, state, address, lat/lng, contact), `ICUOccupancy` (total/occupied beds, ventilators), `BloodInventory` (per hospital, per blood type, units), `Patient`, `Organ`, `OperationTheatre`, plus emergency/audit event tables.

**Seeding**: `seed_initial_data()` runs on every startup — creates the organizer admin + one default hospital (Apollo) if the DB is fresh. `seed_additional_hospitals()` runs on *every* startup regardless of DB state, checks by hospital name, and inserts any missing hospitals from `EXTRA_HOSPITALS` — this is what lets you expand the network without wiping existing data.

---

## 6. Frontend Structure (`frontend/src/`)

- `app.js` — SPA router; dispatches on `data-tab` attributes, calls `renderX()` + `attachXEvents()` pairs per page
- `pages/Landing.js` — public emergency dashboard; polls `/emergency/current-state`, drives siren/sound state transitions, renders the SEARCHING/DONOR_MATCHED/ACKNOWLEDGED cards
- `pages/QuantumMatchView.js` — per-organ/per-patient detailed match compute
- `pages/DonorSearchView.js` — CSV upload, demo pool seeding, patient search form, live Grover's-style animated grid, ranked results table
- `services/sound.js` — Web Audio API sound design (see §7)
- `components/Sidebar.js` — role-gated nav (organizer sees the full COMMAND & AI SUITE; hospital/doctor see a subset)

**Dev server**: Vite, proxies `/api` to the backend — check `vite.config.js` for the target port and make sure it matches whatever port you actually run uvicorn on (**this bit people every time — mismatched ports here look like a broken backend when it's just a proxy misconfiguration**).

---

## 7. Sound Design (mirrored across web + firmware)

Both `frontend/src/services/sound.js` (Web Audio API oscillators) and `firmware/esp32_organ_box/src/main.cpp` / `firmware/q_transplant_esp32.ino` (`tone()`/`noTone()`) implement the same three cues so the physical box and the dashboard feel like the same event:

1. **Ambulance siren** (`SEARCHING` state) — real pitch-sweeping hi-lo wail, ~0.85s per cycle, loops continuously until state changes. Requires a **passive buzzer** on hardware for a true pitch sweep (active buzzers only get the on/off rhythm, not the pitch change).
2. **Donor-found chime** (`DONOR_MATCHED` state) — ~3 second sequence: rising 4-note arpeggio → two confirmation dings → sustained resolving pad chord
3. **Happy acknowledge jingle** (`ACKNOWLEDGED` state) — short 4-note upbeat run-up, deliberately distinct from the donor-found chime so the two events are audibly different

---

## 8. Hardware / Firmware

Two firmware implementations exist in the repo — **know which one you're actually flashing**:
- `firmware/q_transplant_esp32.ino` — plain Arduino sketch
- `firmware/esp32_organ_box/` — PlatformIO project (`src/main.cpp` + `include/config.h`) — this is the one VS Code's PlatformIO extension will build/flash by default if that's your workflow

Both must stay in sync feature-wise (button behavior, sound cues, endpoint calls) since they represent the same physical device — pick one as canonical for production and treat the other as a reference/backup.

**Critical setup checklist** (this is where most "it's not working" issues come from):
1. ESP32 and the machine running the backend must be on the **same Wi-Fi network** (same SSID as `WIFI_SSID`)
2. `BACKEND_HOST` must be the backend machine's **actual LAN IP** (`hostname -I` / `ipconfig`), never `localhost`/`127.0.0.1`
3. Backend must run with **`--host 0.0.0.0`**, not just `--port`, or it will refuse connections from other devices on the network
4. The Donor button must call **both** `/emergency/donor-available` (drives the dashboard's live match card) — not just `/organs/` (inventory only) — missing this call is a real bug that silently breaks the hardware-to-dashboard flow

---

## 9. Non-functional / framing notes to keep honest

- The "quantum" framing (Grover's algorithm, amplitude amplification) is a **narrative/visualization layer over classical scoring** — be upfront about this distinction when explaining the system to judges, hospitals, or collaborators, rather than implying real quantum hardware is involved.
- Several sidebar modules (federated learning, multi-agent system, digital twin) may be UI scaffolding without full backend implementation — verify each one's actual depth before claiming it in a pitch.
- Distance/ETA calculations use haversine (straight-line) distance with an assumed average speed, not real routing/traffic data — accurate enough for a demo, not for production dispatch.

---

## 10. How to extend this spec

When adding a new feature, decide up front:
- Does it belong in the **emergency pipeline** (real-time, single active event) or the **donor search pipeline** (bulk, per-search)? They're intentionally separate state models — don't conflate them.
- Does it need a DB table, or is in-memory state acceptable for a hackathon demo? (Donor pool and emergency state are currently in-memory — fine for a single-process demo, will not survive a restart or scale beyond one server process.)
- Does it need a matching change in **both** firmware implementations, or just the web app?
