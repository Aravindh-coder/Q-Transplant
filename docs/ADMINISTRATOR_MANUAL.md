# Q-Transplant Administrator Manual

## Overview
Q-Transplant is an enterprise-grade organ transplant coordination platform.
As Organizer (Administrator), you hold the highest privilege level in the system.

## Organizer Credentials (Default)
- **Email**: admin@qtransplant.org
- **Password**: AdminPass123!

## Core Responsibilities

### 1. User Approval Workflow
All Doctor, Hospital, Donor, and Patient accounts require Organizer approval before activation.

**Steps**:
1. Log in as Organizer.
2. Navigate to **User Approvals** in the sidebar.
3. Review the registration details of each pending user.
4. Click **Approve** or **Reject** with a reason comment.
5. The system automatically sends the decision email to the registrant.

### 2. Organ Match Oversight
1. Navigate to **Organ Registry**.
2. Select an available donated organ.
3. Click **Compute Quantum Matches** to trigger multi-factor compatibility algorithm.
4. Review ranked match candidates sorted by Quantum Confidence Score.
5. Approve the best match to dispatch.

### 3. Audit Logs
- Navigate to **Audit Logs** in the sidebar.
- View timestamped records of all platform actions.
- Export to CSV via the Export Report button.

### 4. Export Reports
- CSV Organ Registry: `GET /api/v1/reports/export/organs`
- CSV Audit Trail: `GET /api/v1/reports/export/audit`

## API Quick Reference
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/login` | POST | Admin sign in |
| `/api/v1/users/pending-approvals` | GET | List pending registrations |
| `/api/v1/users/approve` | POST | Approve or reject user |
| `/api/v1/matches/compute/{organ_id}` | POST | Run quantum match engine |
| `/api/v1/audit/logs` | GET | Retrieve audit trail |
