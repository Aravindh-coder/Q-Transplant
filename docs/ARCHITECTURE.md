# Q-Transplant Platform Architecture & System Design

## 1. Overview
Q-Transplant is a high-reliability organ transplant coordination system connecting organ donors, transplant patients, surgical teams, and hospital logistics through cold-chain telemetry and real-time compatibility algorithms.

## 2. Core Subsystems

```
┌────────────────────────────────────────────────────────────────────────┐
│                        IBM Carbon Frontend SPA                         │
│   [Organizer Portal]  [Doctor Portal]  [Hospital/Transport Dashboard]   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ HTTPS / REST API
┌──────────────────────────────────▼─────────────────────────────────────┐
│                          FastAPI Backend Core                          │
│   ┌──────────────┐  ┌───────────────┐  ┌───────────────────────────┐   │
│   │ Auth & RBAC  │  │ Organ Matcher │  │ Cold-Box Telemetry Engine │   │
│   └──────┬───────┘  └───────┬───────┘  └─────────────┬─────────────┘   │
└──────────┼──────────────────┼────────────────────────┼─────────────────┘
           │                  │                        │
┌──────────▼──────────────────▼────────────────────────▼─────────────────┐
│                    SQLAlchemy ORM Data Persistence                      │
│            [SQLite (Dev) / PostgreSQL (Prod Container)]                 │
└────────────────────────────────────────────────────────────────────────┘
                                   ▲
                                   │ WiFi / HTTP Telemetry Payload
┌──────────────────────────────────┴─────────────────────────────────────┐
│                    ESP32 Cold-Box Telemetry Unit                       │
│        [DHT22 Temp/Humidity] [Neo-6M GPS] [LiPo Battery Sensor]        │
└────────────────────────────────────────────────────────────────────────┘
```

## 3. Database Domain Models
1. **Users**: Role-based access (`organizer`, `doctor`, `hospital`, `donor`, `patient`).
2. **Hospitals**: Location, license, contact phone, coordinate bounds.
3. **Doctors**: Medical license, specialization, hospital association.
4. **Donors & Patients**: ABO blood type, HLA locus strings, organ target, urgency index.
5. **Organs**: Ischemia time limits, cold box ID, donor mapping.
6. **Matches**: ABO/HLA compatibility scoring percentage, distance decay.
7. **GPS & Telemetry**: Cold box temperature (2-8°C optimal), humidity, location tracking.
8. **Audit Logs & Approvals**: Complete system audit trail.
