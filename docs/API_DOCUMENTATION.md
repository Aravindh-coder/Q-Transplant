# Q-Transplant REST API Specification

OpenAPI documentation is auto-generated and interactively available at `/api/v1/docs`.

## Key Endpoints Summary

### Authentication (`/api/v1/auth`)
- `POST /register`: Register user account (returns 201 Created).
- `POST /login`: Authenticate and acquire JWT access and refresh tokens.
- `POST /refresh`: Issue new access token using refresh token.
- `GET /me`: Retrieve authenticated user profile.

### User Management (`/api/v1/users`)
- `GET /pending-approvals`: Retrieve non-approved accounts (Organizer only).
- `POST /approve`: Approve or reject account registration request.

### Organ Registry & Matches (`/api/v1/organs`, `/api/v1/matches`)
- `POST /organs/`: Register harvested organ offer.
- `POST /matches/compute/{organ_id}`: Compute ABO/HLA compatibility ranking.
- `POST /matches/{match_id}/approve`: Approve transplant match for dispatch.

### ESP32 Telemetry (`/api/v1/telemetry`)
- `POST /telemetry/push`: Push cold box sensor reading (Called by ESP32 hardware).
- `GET /telemetry/{cold_box_id}/latest`: Fetch current temp, battery, and location.
