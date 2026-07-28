# Q-Transplant Deployment Guide

## Prerequisites
- Docker & Docker Compose installed
- Node.js 20+
- Python 3.11+

## Local Development

### 1. Clone Repository
```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Q-transplant
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your SMTP credentials and secrets
```

### 3. Start Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
PYTHONPATH=. ./backend/venv/bin/uvicorn backend.app.main:app --reload --port 8000
```

### 4. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 5. Access Points
| Service | URL |
|---------|-----|
| Frontend Application | http://localhost:5173 |
| Backend API Docs | http://localhost:8000/api/v1/docs |
| Backend Health | http://localhost:8000/health |

## Docker Production Deployment
```bash
cd infrastructure
docker-compose up --build -d
```

## Kubernetes Deployment
```bash
kubectl apply -f infrastructure/k8s/postgres-statefulset.yaml
kubectl apply -f infrastructure/k8s/backend-deployment.yaml
kubectl apply -f infrastructure/k8s/frontend-deployment.yaml
```

## Running Tests
```bash
PYTHONPATH=. ./backend/venv/bin/pytest backend/tests -v
```

## Default Login Credentials
| Role | Email | Password |
|------|-------|----------|
| Organizer | admin@qtransplant.org | AdminPass123! |
| Hospital | apollo@qtransplant.org | HospitalPass123! |
| Doctor | doctor@qtransplant.org | DoctorPass123! |
| Donor | donor@qtransplant.org | DonorPass123! |
| Patient | patient@qtransplant.org | PatientPass123! |

## ESP32 Telemetry Setup
1. Flash the PlatformIO firmware to your ESP32 board.
2. Update `WIFI_SSID`, `WIFI_PASS`, and `BACKEND_HOST` in `firmware/esp32_organ_box/include/config.h`.
3. Connect DHT22 on GPIO4 and Neo-6M GPS on GPIO16/17.
4. Power on — the device will connect and start sending telemetry to `/api/v1/telemetry/push`.
