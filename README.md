# Q-Transplant Platform

Production-grade enterprise organ transplant coordination platform engineered with FastAPI, SQLAlchemy ORM, Alembic migrations, JWT RBAC security, IBM Carbon-inspired enterprise frontend UI, and real-time ESP32 cold-box telemetry tracking.

## System Features
- **FastAPI Async Backend**: Modular architecture with OpenAPI docs at `/api/v1/docs`.
- **RBAC Roles**: Organizer (Admin), Doctor, Hospital, Donor, Patient.
- **SQLAlchemy & Alembic**: Database schema for users, organs, matches, cold boxes, GPS transport, and audit logs.
- **Organ Compatibility Matcher**: ABO blood group compatibility, HLA antigen similarity scoring, and urgency ranking.
- **IBM Carbon UI**: High contrast enterprise aesthetics, live Leaflet map tracker, telemetry gauge, theme engine.
- **ESP32 Telemetry Module**: Cold-chain preservation monitoring (2-8°C threshold alerts).
- **Docker Ready**: Multi-container docker-compose setup.

## Quick Start (Local Development)

### 1. Backend Server
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```
- API Docs: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

### 2. Frontend Application
```bash
cd frontend
npm install
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

### 3. Run Automated PyTest Suite
```bash
pytest backend/tests
```

### 4. Run via Docker Compose
```bash
docker-compose -f infrastructure/docker-compose.yml up --build
```

## Default Credentials
| Role | Email | Password |
|------|-------|----------|
| Organizer (Admin) | `admin@qtransplant.org` | `AdminPass123!` |
| Hospital Authority | `apollo@qtransplant.org` | `HospitalPass123!` |
| Doctor | `doctor@qtransplant.org` | `DoctorPass123!` |
| Organ Donor | `donor@qtransplant.org` | `DonorPass123!` |
| Transplant Patient | `patient@qtransplant.org` | `PatientPass123!` |

## Git Push Instructions for User
To push this code repository to your personal GitHub account:
```bash
git add .
git commit -m "feat: complete Q-Transplant enterprise architecture foundation"
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git branch -M main
git push -u origin main
```
