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
- `/doctor`, `/doctor/profile`, `/doctor/patients`, `/doctor/donors`, `/doctor/matching`, `/doctor/emergency`
- `/donor`, `/donor/profile`, `/donor/status`
- `/hospital`, `/hospital/profile`, `/hospital/doctors`, `/hospital/patients`, `/hospital/matching`, `/hospital/emergency`
- `/organizer`, `/organizer/users`, `/organizer/doctors`, `/organizer/approvals`, `/organizer/hospitals`, `/organizer/donors`, `/organizer/patients`, `/organizer/matches`, `/organizer/emergency`, `/organizer/devices`, `/organizer/audit`

The SPA uses hash routes so it can be served as a static file without a server-side rewrite rule.
