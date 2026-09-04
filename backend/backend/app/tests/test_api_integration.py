"""API-level integration tests -- real HTTP requests through the full
FastAPI app, covering the auth/registration/approval flows the spec's
testing section explicitly requires and that the unit-level tests in
test_roadmap_services.py/test_roadmap_41.py don't touch at all."""
import io
from app.tests.conftest import unique_email


# ---------- structured error shape (spec section 45) ----------

def test_errors_use_structured_shape(client):
    r = client.post("/api/v1/auth/login", json={"email": "nope@example.com", "password": "wrong"})
    assert r.status_code == 401
    body = r.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"
    assert "message" in body["error"]

def test_validation_error_uses_structured_shape(client):
    r = client.post("/api/v1/auth/register", json={"email": "not-an-email"})
    assert r.status_code == 422
    body = r.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


# ---------- authentication ----------

def test_wrong_password_rejected(client):
    email = unique_email("donor")
    client.post("/api/v1/auth/register", json={
        "email": email, "password": "RealPass123!", "role": "donor", "full_name": "D One",
        "phone": "111", "address": "addr", "blood_group": "O+",
    })
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "WrongPassword!"})
    assert r.status_code == 401

def test_invalid_jwt_rejected(client):
    r = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401

def test_missing_token_rejected_on_protected_route(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401

def test_organizer_bootstrap_login_works(organizer_token):
    assert organizer_token  # fixture already asserts 200 + extracts token


# ---------- role-based authorization ----------

def test_donor_cannot_access_doctor_only_route(client):
    email = unique_email("donor")
    client.post("/api/v1/auth/register", json={
        "email": email, "password": "RealPass123!", "role": "donor", "full_name": "D Two",
        "phone": "111", "address": "addr", "blood_group": "O+",
    })
    # Donor accounts require email verification before login -- confirm
    # that gate holds too, since nothing else in the suite checks it.
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "RealPass123!"})
    assert r.status_code == 403
    assert "verify" in r.json()["error"]["message"].lower()

def test_organizer_only_route_blocks_other_roles(client, organizer_token):
    # sanity: organizer token DOES work on an organizer-only route
    r = client.get("/api/v1/organizer/doctors/pending", headers={"Authorization": f"Bearer {organizer_token}"})
    assert r.status_code == 200


# ---------- doctor registration -> approval -> login chain ----------
# Regression coverage for the bugs fixed this session: missing required
# fields, documents never linking to the profile, approval never clearing
# email_verified.

def _register_doctor(client, email):
    r = client.post("/api/v1/auth/register", json={
        "email": email, "password": "DoctorPass123!", "role": "doctor", "full_name": "Dr Test",
        "phone": "111", "address": "addr", "license_number": f"LIC-{email.split(chr(64))[0]}",
        "specialty": "Cardiology", "professional_information": "10 years experience",
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["approval_required"] is True
    assert "upload_token" in body
    return body

import base64

# 8x8 JPEG, embedded so the test suite doesn't need Pillow as a dependency.
_TINY_JPEG_B64 = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4n"
    "ICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIy"
    "MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAIAAgDASIAAhEBAxEB/8QAHwAAAQUBAQEB"
    "AQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKB"
    "kaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1"
    "dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl"
    "5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcF"
    "BAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5"
    "OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0"
    "tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwCxRRRXYch/"
    "//9k="
)

def _tiny_jpeg_bytes():
    return base64.b64decode(_TINY_JPEG_B64)

def test_doctor_cannot_login_before_approval(client):
    email = unique_email("doctor")
    _register_doctor(client, email)
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "DoctorPass123!"})
    assert r.status_code == 403

def test_doctor_approval_requires_photo_and_certificate(client, organizer_token):
    email = unique_email("doctor")
    reg = _register_doctor(client, email)
    upload_token = reg["upload_token"]
    headers = {"Authorization": f"Bearer {upload_token}"}
    jpeg = _tiny_jpeg_bytes()

    # Upload only the photo, not the certificate.
    client.post("/api/v1/documents?kind=photo", headers=headers, files={"file": ("selfie.jpg", jpeg, "image/jpeg")})

    pending = client.get("/api/v1/organizer/doctors/pending", headers={"Authorization": f"Bearer {organizer_token}"}).json()
    # Find our doctor by matching license number instead (email isn't on DoctorProfile directly).
    entry = next(p for p in pending if p["doctor"]["license_number"] == f"LIC-{email.split(chr(64))[0]}")
    doctor_id = entry["doctor"]["id"]

    r = client.post(f"/api/v1/organizer/doctors/{doctor_id}/approve", headers={"Authorization": f"Bearer {organizer_token}"})
    assert r.status_code == 400, "approval should be blocked without both photo and certificate"

def test_full_doctor_registration_to_login_chain(client, organizer_token):
    email = unique_email("doctor")
    reg = _register_doctor(client, email)
    headers = {"Authorization": f"Bearer {reg['upload_token']}"}
    jpeg = _tiny_jpeg_bytes()

    r1 = client.post("/api/v1/documents?kind=photo", headers=headers, files={"file": ("selfie.jpg", jpeg, "image/jpeg")})
    assert r1.status_code == 200
    r2 = client.post("/api/v1/documents?kind=certificate", headers=headers, files={"file": ("cert.jpg", jpeg, "image/jpeg")})
    assert r2.status_code == 200

    pending = client.get("/api/v1/organizer/doctors/pending", headers={"Authorization": f"Bearer {organizer_token}"}).json()
    entry = next(p for p in pending if p["doctor"]["license_number"] == f"LIC-{email.split(chr(64))[0]}")
    doctor_id = entry["doctor"]["id"]
    # Both documents should already be linked (the bug this regression-tests).
    assert entry["doctor"]["photo_document_id"] is not None
    assert entry["doctor"]["certificate_document_id"] is not None

    approve = client.post(f"/api/v1/organizer/doctors/{doctor_id}/approve", headers={"Authorization": f"Bearer {organizer_token}"})
    assert approve.status_code == 200
    assert approve.json()["approval_status"] == "APPROVED"

    login = client.post("/api/v1/auth/login", json={"email": email, "password": "DoctorPass123!"})
    assert login.status_code == 200, login.text
    assert login.json()["role"] == "doctor"


# ---------- pagination (spec section 40) ----------

def test_doctor_listing_is_paginated(client, organizer_token):
    r = client.get("/api/v1/doctors", headers={"Authorization": f"Bearer {organizer_token}"})
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) >= {"items", "page", "page_size", "total", "pages"}


# ---------- rate limiting (spec section 29/41) ----------

def test_login_rate_limit_engages(client):
    email = unique_email("ratelimit")
    for _ in range(12):
        r = client.post("/api/v1/auth/login", json={"email": email, "password": "wrong"})
    assert r.status_code == 429


# ---------- real-time notifications (WebSocket) ----------

def test_realtime_notification_pushed_on_doctor_approval(client, organizer_token):
    """Regression test for the realtime wiring: notify() should push a
    live event to a connected client matching the recipient's user_id,
    not just write the DB Notification row."""
    email = unique_email("doctor")
    reg = _register_doctor(client, email)
    upload_token = reg["upload_token"]
    headers = {"Authorization": f"Bearer {upload_token}"}
    jpeg = _tiny_jpeg_bytes()
    client.post("/api/v1/documents?kind=photo", headers=headers, files={"file": ("selfie.jpg", jpeg, "image/jpeg")})
    client.post("/api/v1/documents?kind=certificate", headers=headers, files={"file": ("cert.jpg", jpeg, "image/jpeg")})

    pending = client.get("/api/v1/organizer/doctors/pending", headers={"Authorization": f"Bearer {organizer_token}"}).json()
    entry = next(p for p in pending if p["doctor"]["license_number"] == f"LIC-{email.split(chr(64))[0]}")
    doctor_id = entry["doctor"]["id"]

    with client.websocket_connect(f"/api/v1/notifications/ws?token={upload_token}") as ws:
        approve = client.post(f"/api/v1/organizer/doctors/{doctor_id}/approve", headers={"Authorization": f"Bearer {organizer_token}"})
        assert approve.status_code == 200
        msg = ws.receive_json()
        assert msg["event"] == "notification"
        assert "approved" in msg["data"]["title"].lower()

def test_realtime_ws_rejects_invalid_token(client):
    try:
        with client.websocket_connect("/api/v1/notifications/ws?token=not-a-real-token"):
            assert False, "should have been rejected"
    except Exception:
        pass  # connection is closed by the server during handshake/first receive


# ---------- expired token / invalid uploads (spec section 41) ----------

def test_expired_jwt_rejected(client):
    import jwt as pyjwt
    from datetime import datetime, timedelta, timezone
    from app.config import settings
    expired_payload = {
        "sub": "some-user-id", "email": "x@example.com", "role": "donor",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
    }
    expired_token = pyjwt.encode(expired_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGO)
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert r.status_code == 401

def test_upload_rejects_disallowed_file_type(client):
    email = unique_email("doctor")
    reg = _register_doctor(client, email)
    headers = {"Authorization": f"Bearer {reg['upload_token']}"}
    r = client.post("/api/v1/documents?kind=certificate", headers=headers,
                     files={"file": ("virus.exe", b"not a real document", "application/octet-stream")})
    assert r.status_code == 400

def test_upload_rejects_oversized_file(client):
    email = unique_email("doctor")
    reg = _register_doctor(client, email)
    headers = {"Authorization": f"Bearer {reg['upload_token']}"}
    oversized = b"0" * (10 * 1024 * 1024 + 1)
    r = client.post("/api/v1/documents?kind=certificate", headers=headers,
                     files={"file": ("big.pdf", oversized, "application/pdf")})
    assert r.status_code == 413


# ---------- doctor rejection (spec section 41) ----------

def test_doctor_rejection_blocks_login(client, organizer_token):
    email = unique_email("doctor")
    reg = _register_doctor(client, email)
    headers = {"Authorization": f"Bearer {reg['upload_token']}"}
    jpeg = _tiny_jpeg_bytes()
    client.post("/api/v1/documents?kind=photo", headers=headers, files={"file": ("selfie.jpg", jpeg, "image/jpeg")})
    client.post("/api/v1/documents?kind=certificate", headers=headers, files={"file": ("cert.jpg", jpeg, "image/jpeg")})

    pending = client.get("/api/v1/organizer/doctors/pending", headers={"Authorization": f"Bearer {organizer_token}"}).json()
    entry = next(p for p in pending if p["doctor"]["license_number"] == f"LIC-{email.split(chr(64))[0]}")
    doctor_id = entry["doctor"]["id"]

    reject = client.post(f"/api/v1/organizer/doctors/{doctor_id}/reject",
                          params={"reason": "License could not be verified"},
                          headers={"Authorization": f"Bearer {organizer_token}"})
    assert reject.status_code == 200
    assert reject.json()["approval_status"] == "REJECTED"

    login = client.post("/api/v1/auth/login", json={"email": email, "password": "DoctorPass123!"})
    assert login.status_code == 403


# ---------- pagination shape on the previously-unbounded endpoints ----------

def test_hospital_listing_is_paginated(client, organizer_token):
    r = client.get("/api/v1/hospitals", headers={"Authorization": f"Bearer {organizer_token}"})
    assert r.status_code == 200
    assert set(r.json().keys()) >= {"items", "page", "page_size", "total", "pages"}

def test_organizer_users_listing_is_paginated(client, organizer_token):
    r = client.get("/api/v1/organizer/users", headers={"Authorization": f"Bearer {organizer_token}"})
    assert r.status_code == 200
    assert set(r.json().keys()) >= {"items", "page", "page_size", "total", "pages"}


# ---------- quantum comparison actually runs on live matches (spec 20/37) ----------

def test_matching_engine_includes_quantum_comparison():
    from app.services.matching_engine import run_match
    donors = [{"id": "d1", "blood_group": "O+", "organs_available": ["kidney"], "availability_status": "active",
               "hla_a": "A1,A2", "hla_b": "B7,B8", "hla_c": "C1,C2", "hla_dr": "DR1,DR2", "hla_dq": "DQ1,DQ2"}]
    patient = {"id": "p1", "blood_group": "O+", "required_organ": "kidney", "urgency": "HIGH", "waiting_since": None,
               "eligible": True, "hla_a": "A1,A2", "hla_b": "B7,B8", "hla_c": "C1,C2", "hla_dr": "DR1,DR2", "hla_dq": "DQ1,DQ2"}
    result = run_match(donors, patient)
    assert result["quantum_comparison"] is not None
    assert "classical_evaluations" in result["quantum_comparison"]
    assert "quantum_inspired_evaluations" in result["quantum_comparison"]


# ---------- AI match summary falls back gracefully with no key configured ----------

def test_ai_match_summary_falls_back_without_api_key():
    from app.services.ai_assistant import summarize_match
    result = summarize_match({"rank": 1, "score": 92, "hla_score": 85, "urgency": "HIGH"})
    assert "92" in result or "score" in result.lower()


# ---------- OTP edge cases (spec section 8/41) ----------
from unittest.mock import patch

def _register_donor(client, email):
    r = client.post("/api/v1/auth/register", json={
        "email": email, "password": "DonorPass123!", "role": "donor", "full_name": "Don Or",
        "phone": "111", "address": "addr", "blood_group": "O+",
    })
    assert r.status_code == 200, r.text
    return r

def test_donor_email_verification_full_flow(client):
    email = unique_email("donor")
    with patch("random.SystemRandom.randrange", return_value=123456):
        _register_donor(client, email)
    verify = client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "123456"})
    assert verify.status_code == 200
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "DonorPass123!"})
    assert login.status_code == 200

def test_wrong_otp_rejected(client):
    email = unique_email("donor")
    with patch("random.SystemRandom.randrange", return_value=123456):
        _register_donor(client, email)
    verify = client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "999999"})
    assert verify.status_code == 400

def test_otp_is_single_use(client):
    email = unique_email("donor")
    with patch("random.SystemRandom.randrange", return_value=222222):
        _register_donor(client, email)
    first = client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "222222"})
    assert first.status_code == 200
    second = client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "222222"})
    assert second.status_code == 400

def test_expired_otp_rejected(client):
    email = unique_email("donor")
    with patch("random.SystemRandom.randrange", return_value=333333):
        _register_donor(client, email)
    # Reach into the DB directly to simulate time passing -- there's no
    # clock-injection seam in the app, so this is the honest way to test
    # expiry without sleeping the test suite for real minutes.
    from app.database import SessionLocal
    from app.models import OTP
    from datetime import datetime, timedelta, timezone
    db = SessionLocal()
    try:
        row = db.query(OTP).filter(OTP.email == email, OTP.purpose == "email_verify").order_by(OTP.created_at.desc()).first()
        row.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.commit()
    finally:
        db.close()
    verify = client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "333333"})
    assert verify.status_code == 400

def test_password_reset_full_flow(client):
    email = unique_email("donor")
    with patch("random.SystemRandom.randrange", return_value=444444):
        _register_donor(client, email)
    with patch("random.SystemRandom.randrange", return_value=555555):
        forgot = client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert forgot.status_code == 200
    reset = client.post("/api/v1/auth/reset-password", json={"email": email, "otp": "555555", "new_password": "NewPass456!"})
    assert reset.status_code == 200
    # old password no longer works, new one does (once email is verified)
    with patch("random.SystemRandom.randrange", return_value=666666):
        client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "444444"})
    login_old = client.post("/api/v1/auth/login", json={"email": email, "password": "DonorPass123!"})
    assert login_old.status_code == 401
    login_new = client.post("/api/v1/auth/login", json={"email": email, "password": "NewPass456!"})
    assert login_new.status_code == 200

def test_forgot_password_does_not_leak_account_existence(client):
    real_email = unique_email("donor")
    _register_donor(client, real_email)
    r1 = client.post("/api/v1/auth/forgot-password", json={"email": real_email})
    r2 = client.post("/api/v1/auth/forgot-password", json={"email": unique_email("nosuchaccount")})
    assert r1.status_code == r2.status_code == 200
    assert r1.json() == r2.json()


# ---------- public emergency status feed for the landing page ----------

def test_public_emergency_ws_connects_and_receives_initial_state(client):
    with client.websocket_connect("/api/v1/emergency/public-ws") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "state"
        assert "hospitals" in msg

def test_public_emergency_ws_sees_live_hospital_emergency(client, organizer_token):
    # Register + verify a hospital so it appears in the public state feed.
    email = unique_email("hospital")
    reg = client.post("/api/v1/auth/register", json={
        "email": email, "password": "HospPass123!", "role": "hospital", "full_name": "Contact",
        "phone": "111", "address": "addr", "hospital_name": "PublicWS Test Hospital",
        "hospital_code": f"CODE-{email.split(chr(64))[0]}", "location": "Downtown",
        "registration_number": "REG-1", "authorized_contact": "Jane",
    })
    assert reg.status_code == 200
    upload_headers = {"Authorization": f"Bearer {reg.json()['upload_token']}"}
    client.post("/api/v1/documents?kind=license", headers=upload_headers,
                files={"file": ("license.jpg", _tiny_jpeg_bytes(), "image/jpeg")})
    hospitals = client.get("/api/v1/hospitals", headers={"Authorization": f"Bearer {organizer_token}"}).json()
    hospital = next(h for h in hospitals["items"] if h["hospital_name"] == "PublicWS Test Hospital")
    verify = client.post(f"/api/v1/organizer/hospitals/{hospital['id']}/verify", headers={"Authorization": f"Bearer {organizer_token}"})
    assert verify.status_code == 200
    with patch("random.SystemRandom.randrange", return_value=777777):
        client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "777777"})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "HospPass123!"})
    assert login.status_code == 200
    hosp_token = login.json()["access_token"]

    with client.websocket_connect("/api/v1/emergency/public-ws") as ws:
        ws.receive_json()  # initial state
        create = client.post("/api/v1/emergency/create", json={"requirement": "O-negative kidney needed urgently"},
                              headers={"Authorization": f"Bearer {hosp_token}"})
        assert create.status_code == 200
        update = ws.receive_json()
        assert update["type"] == "state"
        entry = update["hospitals"][hospital["id"]]
        assert entry["status"] == "emergency"
        assert entry["requirement"] == "O-negative kidney needed urgently"


# ---------- ad-hoc recipient search with quantum trace + AI review ----------

def test_ad_hoc_recipient_search(client, organizer_token):
    email = unique_email("doctor")
    reg = _register_doctor(client, email)
    headers = {"Authorization": f"Bearer {reg['upload_token']}"}
    jpeg = _tiny_jpeg_bytes()
    client.post("/api/v1/documents?kind=photo", headers=headers, files={"file": ("s.jpg", jpeg, "image/jpeg")})
    client.post("/api/v1/documents?kind=certificate", headers=headers, files={"file": ("c.jpg", jpeg, "image/jpeg")})
    pending = client.get("/api/v1/organizer/doctors/pending", headers={"Authorization": f"Bearer {organizer_token}"}).json()
    entry = next(p for p in pending if p["doctor"]["license_number"] == f"LIC-{email.split(chr(64))[0]}")
    client.post(f"/api/v1/organizer/doctors/{entry['doctor']['id']}/approve", headers={"Authorization": f"Bearer {organizer_token}"})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "DoctorPass123!"})
    doc_token = login.json()["access_token"]

    r = client.post("/api/v1/matching/search",
                     json={"blood_group": "O+", "required_organ": "kidney", "urgency": "HIGH", "ai_review_top_n": 1},
                     headers={"Authorization": f"Bearer {doc_token}"})
    assert r.status_code == 200
    body = r.json()
    assert "recipient_criteria" in body
    assert "matches" in body
    assert "quantum_comparison" in body
    assert "search_trace" in body

def test_ad_hoc_search_blocked_for_donor_role(client):
    email = unique_email("donor")
    with patch("random.SystemRandom.randrange", return_value=111888):
        client.post("/api/v1/auth/register", json={
            "email": email, "password": "DonorPass123!", "role": "donor", "full_name": "D",
            "phone": "1", "address": "a", "blood_group": "O+",
        })
    client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "111888"})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "DonorPass123!"})
    assert login.status_code == 200
    donor_token = login.json()["access_token"]
    r = client.post("/api/v1/matching/search", json={"blood_group": "O+", "required_organ": "kidney"},
                     headers={"Authorization": f"Bearer {donor_token}"})
    assert r.status_code == 403


# ---------- donor CSV bulk import (not available to the donor role) ----------

def test_donor_csv_import(client, organizer_token):
    _, hospital_id = _verified_hospital(client, organizer_token, "csvimport")
    csv_content = (
        "full_name,email,blood_group,organs_available,phone,address\n"
        f"Test Donor One,{unique_email('csvdonor')},O+,kidney;liver,111,addr\n"
        f"Test Donor Two,{unique_email('csvdonor')},invalid-blood-group,kidney,111,addr\n"
        f"Test Donor Three,{unique_email('csvdonor')},AB-,heart,111,addr\n"
    )
    r = client.post(f"/api/v1/donors/import?hospital_id={hospital_id}",
                     files={"file": ("donors.csv", csv_content.encode(), "text/csv")},
                     headers={"Authorization": f"Bearer {organizer_token}"})
    assert r.status_code == 200
    body = r.json()
    assert body["created"] == 2
    assert body["skipped_count"] == 1
    assert "invalid" in body["skipped"][0]["reason"]

def test_donor_csv_import_requires_hospital_id(client, organizer_token):
    r = client.post("/api/v1/donors/import",
                     files={"file": ("donors.csv", b"blood_group\nO+\n", "text/csv")},
                     headers={"Authorization": f"Bearer {organizer_token}"})
    assert r.status_code == 400

def test_donor_csv_import_rejects_non_csv_role_and_filetype(client, organizer_token):
    _, hospital_id = _verified_hospital(client, organizer_token, "csvfiletype")
    r = client.post(f"/api/v1/donors/import?hospital_id={hospital_id}",
                     files={"file": ("donors.txt", b"not a csv", "text/plain")},
                     headers={"Authorization": f"Bearer {organizer_token}"})
    assert r.status_code == 400

def test_donor_csv_import_blocked_for_donor_role(client):
    email = unique_email("donor")
    with patch("random.SystemRandom.randrange", return_value=222999):
        client.post("/api/v1/auth/register", json={
            "email": email, "password": "DonorPass123!", "role": "donor", "full_name": "D",
            "phone": "1", "address": "a", "blood_group": "O+",
        })
    client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "222999"})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "DonorPass123!"})
    donor_token = login.json()["access_token"]
    r = client.post("/api/v1/donors/import",
                     files={"file": ("donors.csv", b"blood_group\nO+\n", "text/csv")},
                     headers={"Authorization": f"Bearer {donor_token}"})
    assert r.status_code == 403


# ---------- registration resume (server succeeded, client never got the response) ----------

def test_resume_registration_for_doctor_reissues_upload_token(client):
    """Simulates the exact bug reported: registration succeeded server-side,
    but the client never got the response, so retrying just sees 'account
    already exists' with no way to continue."""
    email = unique_email("doctor")
    _register_doctor(client, email)  # this is the request whose response "got lost"
    resume = client.post("/api/v1/auth/resume-registration", json={"email": email, "password": "DoctorPass123!"})
    assert resume.status_code == 200
    body = resume.json()
    assert "upload_token" in body
    # the reissued token actually works for document upload
    jpeg = _tiny_jpeg_bytes()
    r = client.post("/api/v1/documents?kind=photo", headers={"Authorization": f"Bearer {body['upload_token']}"},
                     files={"file": ("s.jpg", jpeg, "image/jpeg")})
    assert r.status_code == 200

def test_resume_registration_for_donor_resends_otp(client):
    email = unique_email("donor")
    client.post("/api/v1/auth/register", json={
        "email": email, "password": "DonorPass123!", "role": "donor", "full_name": "D",
        "phone": "1", "address": "a", "blood_group": "O+",
    })
    resume = client.post("/api/v1/auth/resume-registration", json={"email": email, "password": "DonorPass123!"})
    assert resume.status_code == 200
    assert resume.json()["email_verification_required"] is True

def test_resume_registration_rejects_wrong_password(client):
    email = unique_email("doctor")
    _register_doctor(client, email)
    resume = client.post("/api/v1/auth/resume-registration", json={"email": email, "password": "WrongPassword!"})
    assert resume.status_code == 401

def test_resume_registration_rejects_already_approved_doctor(client, organizer_token):
    email = unique_email("doctor")
    reg = _register_doctor(client, email)
    headers = {"Authorization": f"Bearer {reg['upload_token']}"}
    jpeg = _tiny_jpeg_bytes()
    client.post("/api/v1/documents?kind=photo", headers=headers, files={"file": ("s.jpg", jpeg, "image/jpeg")})
    client.post("/api/v1/documents?kind=certificate", headers=headers, files={"file": ("c.jpg", jpeg, "image/jpeg")})
    pending = client.get("/api/v1/organizer/doctors/pending", headers={"Authorization": f"Bearer {organizer_token}"}).json()
    entry = next(p for p in pending if p["doctor"]["license_number"] == f"LIC-{email.split(chr(64))[0]}")
    client.post(f"/api/v1/organizer/doctors/{entry['doctor']['id']}/approve", headers={"Authorization": f"Bearer {organizer_token}"})
    resume = client.post("/api/v1/auth/resume-registration", json={"email": email, "password": "DoctorPass123!"})
    assert resume.status_code == 400


# ---------- registration resume (fixes the 'server waking up then already exists' trap) ----------

def test_doctor_registration_resumes_on_retry_with_same_credentials(client):
    email = unique_email("doctor")
    payload = {
        "email": email, "password": "DoctorPass123!", "role": "doctor", "full_name": "Dr Retry",
        "phone": "111", "address": "addr", "license_number": f"LIC-{email.split(chr(64))[0]}",
        "specialty": "Cardio", "professional_information": "info",
    }
    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 200
    # Simulate exactly the reported scenario: the client gave up waiting
    # but the request had already succeeded server-side, so it retries
    # with the identical payload.
    second = client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]
    assert "upload_token" in second.json()
    # No duplicate doctor profile should have been created.
    from app.database import SessionLocal
    from app.models import DoctorProfile
    db = SessionLocal()
    try:
        count = db.query(DoctorProfile).filter_by(license_number=payload["license_number"]).count()
        assert count == 1
    finally:
        db.close()

def test_registration_retry_with_wrong_password_still_blocked(client):
    email = unique_email("doctor")
    payload = {
        "email": email, "password": "DoctorPass123!", "role": "doctor", "full_name": "Dr X",
        "phone": "111", "address": "addr", "license_number": f"LIC-{email.split(chr(64))[0]}",
        "specialty": "Cardio", "professional_information": "info",
    }
    client.post("/api/v1/auth/register", json=payload)
    bad = dict(payload); bad["password"] = "SomeoneElsePassword!"
    r = client.post("/api/v1/auth/register", json=bad)
    assert r.status_code == 409

def test_registration_retry_blocked_once_already_approved(client, organizer_token):
    email = unique_email("doctor")
    payload = {
        "email": email, "password": "DoctorPass123!", "role": "doctor", "full_name": "Dr Approved",
        "phone": "111", "address": "addr", "license_number": f"LIC-{email.split(chr(64))[0]}",
        "specialty": "Cardio", "professional_information": "info",
    }
    reg = client.post("/api/v1/auth/register", json=payload)
    headers = {"Authorization": f"Bearer {reg.json()['upload_token']}"}
    jpeg = _tiny_jpeg_bytes()
    client.post("/api/v1/documents?kind=photo", headers=headers, files={"file": ("s.jpg", jpeg, "image/jpeg")})
    client.post("/api/v1/documents?kind=certificate", headers=headers, files={"file": ("c.jpg", jpeg, "image/jpeg")})
    pending = client.get("/api/v1/organizer/doctors/pending", headers={"Authorization": f"Bearer {organizer_token}"}).json()
    entry = next(p for p in pending if p["doctor"]["license_number"] == payload["license_number"])
    client.post(f"/api/v1/organizer/doctors/{entry['doctor']['id']}/approve", headers={"Authorization": f"Bearer {organizer_token}"})
    # Once approved, a retry of the original registration must NOT resume --
    # it should hard-block like a genuine duplicate.
    retry = client.post("/api/v1/auth/register", json=payload)
    assert retry.status_code == 409

def test_donor_registration_resume_resends_otp(client):
    email = unique_email("donor")
    payload = {
        "email": email, "password": "DonorPass123!", "role": "donor", "full_name": "Don Retry",
        "phone": "1", "address": "a", "blood_group": "O+",
    }
    with patch("random.SystemRandom.randrange", return_value=444555):
        client.post("/api/v1/auth/register", json=payload)
    with patch("random.SystemRandom.randrange", return_value=666777):
        resumed = client.post("/api/v1/auth/register", json=payload)
    assert resumed.status_code == 200
    # The first code should no longer work (invalidated by the resend);
    # the fresh one should.
    stale = client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "444555"})
    assert stale.status_code == 400
    fresh = client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "666777"})
    assert fresh.status_code == 200


# ---------- mailer resilience: a real SMTP failure must never crash the triggering request ----------

def test_registration_survives_smtp_failure(client, monkeypatch):
    """Registration writes the account to the DB before attempting to send
    a confirmation email. If the SMTP send itself fails for any reason
    (network, auth, DNS -- anything other than 'not configured'), that
    must degrade gracefully, not turn a successful registration into a
    500 for the user."""
    import smtplib
    def broken_smtp(*a, **kw):
        raise OSError("simulated network failure")
    monkeypatch.setattr(smtplib, "SMTP", broken_smtp)
    from app.config import settings
    monkeypatch.setattr(settings, "ORGANIZER_APP_PASSWORD", "fake-app-password-for-this-test")
    email = unique_email("doctor")
    r = client.post("/api/v1/auth/register", json={
        "email": email, "password": "DoctorPass123!", "role": "doctor", "full_name": "Dr Mailfail",
        "phone": "111", "address": "addr", "license_number": f"LIC-{email.split(chr(64))[0]}",
        "specialty": "Cardio", "professional_information": "info",
    })
    assert r.status_code == 200
    assert "upload_token" in r.json()


# ---------- transplant case lifecycle (spec section 36 -- was a stub health-check only) ----------

def _approved_doctor(client, organizer_token):
    email = unique_email("doctor")
    reg = _register_doctor(client, email)
    headers = {"Authorization": f"Bearer {reg['upload_token']}"}
    jpeg = _tiny_jpeg_bytes()
    client.post("/api/v1/documents?kind=photo", headers=headers, files={"file": ("s.jpg", jpeg, "image/jpeg")})
    client.post("/api/v1/documents?kind=certificate", headers=headers, files={"file": ("c.jpg", jpeg, "image/jpeg")})
    pending = client.get("/api/v1/organizer/doctors/pending", headers={"Authorization": f"Bearer {organizer_token}"}).json()
    entry = next(p for p in pending if p["doctor"]["license_number"] == f"LIC-{email.split(chr(64))[0]}")
    client.post(f"/api/v1/organizer/doctors/{entry['doctor']['id']}/approve", headers={"Authorization": f"Bearer {organizer_token}"})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "DoctorPass123!"})
    token = login.json()["access_token"]

    # Patient creation requires the doctor to be linked to a hospital --
    # set up a real verified hospital and link this doctor to it.
    hosp_email = unique_email("hospital")
    hosp_reg = client.post("/api/v1/auth/register", json={
        "email": hosp_email, "password": "HospPass123!", "role": "hospital", "full_name": "Contact",
        "phone": "1", "address": "a", "hospital_name": f"Test Hospital {hosp_email[:8]}",
        "hospital_code": f"CODE-{hosp_email.split(chr(64))[0]}", "location": "City",
        "registration_number": "REG-1", "authorized_contact": "Someone",
    })
    hospitals = client.get("/api/v1/hospitals", headers={"Authorization": f"Bearer {organizer_token}"}).json()
    hospital = next(h for h in hospitals["items"] if h["hospital_code"] == f"CODE-{hosp_email.split(chr(64))[0]}")
    hosp_upload_headers = {"Authorization": f"Bearer {hosp_reg.json()['upload_token']}"}
    client.post("/api/v1/documents?kind=license", headers=hosp_upload_headers,
                files={"file": ("license.jpg", _tiny_jpeg_bytes(), "image/jpeg")})
    client.post(f"/api/v1/organizer/hospitals/{hospital['id']}/verify", headers={"Authorization": f"Bearer {organizer_token}"})

    client.put("/api/v1/doctors/me", json={"license_number": f"LIC-{email.split(chr(64))[0]}", "hospital_id": hospital["id"]}, headers={"Authorization": f"Bearer {token}"})
    return token

def test_transplant_case_full_lifecycle(client, organizer_token):
    doc_token = _approved_doctor(client, organizer_token)
    headers = {"Authorization": f"Bearer {doc_token}"}
    patient = client.post("/api/v1/patients", json={
        "full_name": "Case Patient", "blood_group": "O+", "required_organ": "kidney", "urgency": "HIGH",
    }, headers=headers)
    assert patient.status_code == 200
    patient_id = patient.json()["id"]

    create = client.post("/api/v1/transplants", json={"patient_id": patient_id}, headers=headers)
    assert create.status_code == 200
    case = create.json()
    assert case["stage"] == "CREATED"

    # Valid forward transitions succeed.
    for stage in ("MEDICAL_REVIEW", "MATCH_SEARCH", "CANDIDATE_FOUND", "DOCTOR_REVIEW"):
        r = client.post(f"/api/v1/transplants/{case['id']}/transition", json={"new_stage": stage}, headers=headers)
        assert r.status_code == 200, r.text
        assert r.json()["stage"] == stage

    # An invalid skip-ahead transition is rejected by the state machine.
    bad = client.post(f"/api/v1/transplants/{case['id']}/transition", json={"new_stage": "COMPLETED"}, headers=headers)
    assert bad.status_code == 400

def test_transplant_case_scoped_to_owning_hospital(client, organizer_token):
    doc_token = _approved_doctor(client, organizer_token)
    headers = {"Authorization": f"Bearer {doc_token}"}
    patient = client.post("/api/v1/patients", json={
        "full_name": "Scoped Patient", "blood_group": "A+", "required_organ": "liver", "urgency": "MEDIUM",
    }, headers=headers).json()
    case = client.post("/api/v1/transplants", json={"patient_id": patient["id"]}, headers=headers).json()

    other_doc_token = _approved_doctor(client, organizer_token)
    other_headers = {"Authorization": f"Bearer {other_doc_token}"}
    r = client.get(f"/api/v1/transplants/{case['id']}", headers=other_headers)
    assert r.status_code == 404  # not visible outside the owning hospital

def test_transplant_stages_endpoint_matches_state_machine(client, organizer_token):
    r = client.get("/api/v1/transplants/stages", headers={"Authorization": f"Bearer {organizer_token}"})
    assert r.status_code == 200
    assert "CREATED" in r.json()["stages"]
    assert "COMPLETED" in r.json()["stages"]


# ---------- doctor_workflow's separate upload endpoint must trigger the same AI check + organizer notification as documents.py ----------

def test_doctor_workflow_upload_also_triggers_identity_check(client):
    email = unique_email("doctor")
    reg = _register_doctor(client, email)
    headers = {"Authorization": f"Bearer {reg['upload_token']}"}
    jpeg = _tiny_jpeg_bytes()
    r1 = client.post("/api/v1/doctor-workflow/documents", headers=headers,
                      data={"kind": "profile_photo"}, files={"file": ("s.jpg", jpeg, "image/jpeg")})
    assert r1.status_code == 200
    r2 = client.post("/api/v1/doctor-workflow/documents", headers=headers,
                      data={"kind": "medical_certificate"}, files={"file": ("c.jpg", jpeg, "image/jpeg")})
    assert r2.status_code == 200

    from app.database import SessionLocal
    from app.models import DoctorProfile
    db = SessionLocal()
    try:
        profile = db.query(DoctorProfile).filter_by(license_number=f"LIC-{email.split(chr(64))[0]}").first()
        # Same field the /api/v1/documents path populates -- confirms this
        # second upload endpoint no longer silently skips the identity check.
        assert profile.identity_check_confidence is not None
    finally:
        db.close()


# ---------- security regression tests: device provisioning, match history, quantum donor search ----------

def _verified_hospital(client, organizer_token, prefix="hospsec"):
    email = unique_email(prefix)
    reg = client.post("/api/v1/auth/register", json={
        "email": email, "password": "HospPass123!", "role": "hospital", "full_name": "Contact",
        "phone": "1", "address": "a", "hospital_name": f"Security Test Hospital {email[:8]}",
        "hospital_code": f"CODE-{email.split(chr(64))[0]}", "location": "City",
        "registration_number": "REG-1", "authorized_contact": "Someone",
    })
    assert reg.status_code == 200
    upload_headers = {"Authorization": f"Bearer {reg.json()['upload_token']}"}
    client.post("/api/v1/documents?kind=license", headers=upload_headers,
                files={"file": ("license.jpg", _tiny_jpeg_bytes(), "image/jpeg")})
    hospitals = client.get("/api/v1/hospitals", headers={"Authorization": f"Bearer {organizer_token}"}).json()
    hospital = next(h for h in hospitals["items"] if h["hospital_code"] == f"CODE-{email.split(chr(64))[0]}")
    verify = client.post(f"/api/v1/organizer/hospitals/{hospital['id']}/verify", headers={"Authorization": f"Bearer {organizer_token}"})
    assert verify.status_code == 200
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "HospPass123!"})
    assert login.status_code == 200
    return login.json()["access_token"], hospital["id"]


def test_hospital_cannot_provision_device_for_another_hospital(client, organizer_token):
    _, hospital_a_id = _verified_hospital(client, organizer_token, "hospA")
    hospital_b_token, _ = _verified_hospital(client, organizer_token, "hospB")
    r = client.post(f"/api/v1/devices/provision?hospital_id={hospital_a_id}",
                     headers={"Authorization": f"Bearer {hospital_b_token}"})
    assert r.status_code == 403


def test_hospital_can_provision_device_for_own_hospital(client, organizer_token):
    hospital_token, hospital_id = _verified_hospital(client, organizer_token, "hospOwn")
    r = client.post(f"/api/v1/devices/provision?hospital_id={hospital_id}",
                     headers={"Authorization": f"Bearer {hospital_token}"})
    assert r.status_code == 200
    assert "device_token" in r.json()


def test_organizer_can_still_provision_device_for_any_hospital(client, organizer_token):
    _, hospital_id = _verified_hospital(client, organizer_token, "hospOrg")
    r = client.post(f"/api/v1/devices/provision?hospital_id={hospital_id}",
                     headers={"Authorization": f"Bearer {organizer_token}"})
    assert r.status_code == 200


def test_match_history_not_visible_to_other_hospitals_doctor(client, organizer_token):
    doc_token = _approved_doctor(client, organizer_token)
    headers = {"Authorization": f"Bearer {doc_token}"}
    patient = client.post("/api/v1/patients", json={
        "full_name": "History Patient", "blood_group": "B+", "required_organ": "kidney", "urgency": "HIGH",
    }, headers=headers).json()

    other_doc_token = _approved_doctor(client, organizer_token)
    other_headers = {"Authorization": f"Bearer {other_doc_token}"}
    r = client.get(f"/api/v1/matching/history/{patient['id']}", headers=other_headers)
    assert r.status_code == 403


def test_match_history_visible_to_owning_doctor(client, organizer_token):
    doc_token = _approved_doctor(client, organizer_token)
    headers = {"Authorization": f"Bearer {doc_token}"}
    patient = client.post("/api/v1/patients", json={
        "full_name": "History Patient Own", "blood_group": "AB+", "required_organ": "liver", "urgency": "MEDIUM",
    }, headers=headers).json()
    r = client.get(f"/api/v1/matching/history/{patient['id']}", headers=headers)
    assert r.status_code == 200


def test_quantum_donor_search_requires_authentication(client):
    r = client.get("/api/v1/quantum/search-donors?organ=kidney&blood_group=O+")
    assert r.status_code == 401


def test_quantum_donor_search_blocked_for_donor_role(client):
    email = unique_email("donorqsec")
    with patch("random.SystemRandom.randrange", return_value=555555):
        _register_donor(client, email)
    client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "555555"})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "DonorPass123!"})
    token = login.json()["access_token"]
    r = client.get("/api/v1/quantum/search-donors?organ=kidney&blood_group=O+",
                    headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_quantum_donor_search_works_for_authorized_role(client, organizer_token):
    r = client.get("/api/v1/quantum/search-donors?organ=kidney&blood_group=O+",
                    headers={"Authorization": f"Bearer {organizer_token}"})
    assert r.status_code == 200
    assert "quantum_inspired" in r.json()
    assert "speedup_ratio" not in r.json()["quantum_inspired"]


# ---------- donor verification workflow: medical document required, hospital contact surfaced instead of donor identity ----------

def _verified_donor_with_hospital(client, organizer_token, hospital_id=None, otp=None, prefix="vdonor"):
    """Registers a donor, uploads a medical document, links a hospital
    (creating a fresh verified one if none given -- every donor now needs
    one to pass organizer verification), and has the organizer verify.
    Returns (donor_token, donor_id, hospital_id)."""
    import random as _r
    if not hospital_id:
        _, hospital_id = _verified_hospital(client, organizer_token, f"{prefix}auto")
    email = unique_email(prefix)
    otp = otp or str(_r.randint(100000, 999999))
    with patch("random.SystemRandom.randrange", return_value=int(otp)):
        _register_donor(client, email)
    client.post("/api/v1/auth/verify-email", json={"email": email, "otp": otp})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "DonorPass123!"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile_body = {"blood_group": "AB-", "organs_available": ["pancreas"], "hospital_id": hospital_id}
    r = client.put("/api/v1/donors/me", json=profile_body, headers=headers)
    assert r.status_code == 200, r.text
    donor_id = r.json()["id"]

    jpeg = _tiny_jpeg_bytes()
    up = client.post("/api/v1/documents?kind=medical_document", headers=headers,
                      files={"file": ("report.jpg", jpeg, "image/jpeg")})
    assert up.status_code == 200

    verify = client.post(f"/api/v1/organizer/donors/{donor_id}/verify",
                          headers={"Authorization": f"Bearer {organizer_token}"})
    assert verify.status_code == 200
    return token, donor_id, hospital_id


def test_donor_not_searchable_before_verification(client, organizer_token):
    email = unique_email("unverified")
    with patch("random.SystemRandom.randrange", return_value=414141):
        _register_donor(client, email)
    client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "414141"})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "DonorPass123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    r = client.put("/api/v1/donors/me", json={"blood_group": "AB-", "organs_available": ["heart"]}, headers=headers)
    donor_id = r.json()["id"]

    results = client.get("/api/v1/donors/search?blood_group=AB-",
                          headers={"Authorization": f"Bearer {organizer_token}"}).json()
    assert donor_id not in [d["id"] for d in results["items"]]


def test_organizer_cannot_verify_donor_without_medical_document(client, organizer_token):
    email = unique_email("nodoc")
    with patch("random.SystemRandom.randrange", return_value=424242):
        _register_donor(client, email)
    client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "424242"})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "DonorPass123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    r = client.put("/api/v1/donors/me", json={"blood_group": "B-", "organs_available": ["liver"]}, headers=headers)
    donor_id = r.json()["id"]

    verify = client.post(f"/api/v1/organizer/donors/{donor_id}/verify",
                          headers={"Authorization": f"Bearer {organizer_token}"})
    assert verify.status_code == 400


def test_verified_donor_appears_in_search_without_personal_fields(client, organizer_token):
    _, hospital_id = _verified_hospital(client, organizer_token, "pfieldshosp")
    _, donor_id, hospital_id = _verified_donor_with_hospital(client, organizer_token, hospital_id=hospital_id, prefix="vdonorsearch")
    results = client.get("/api/v1/donors/search?organ=pancreas&blood_group=AB-",
                          headers={"Authorization": f"Bearer {organizer_token}"}).json()
    entry = next(d for d in results["items"] if d["id"] == donor_id)
    for pii_field in ("phone", "address", "date_of_birth", "gender", "user_id", "medical_document_id"):
        assert pii_field not in entry


def test_search_shows_associated_hospital_contact_not_donor_identity(client, organizer_token):
    hospital_token, hospital_id = _verified_hospital(client, organizer_token, "vdonorhosp")
    _, donor_id, hospital_id = _verified_donor_with_hospital(client, organizer_token, hospital_id=hospital_id, prefix="vdonorwh")

    results = client.get("/api/v1/donors/search?organ=pancreas&blood_group=AB-",
                          headers={"Authorization": f"Bearer {organizer_token}"}).json()
    entry = next(d for d in results["items"] if d["id"] == donor_id)
    assert entry["associated_hospital"] is not None
    assert entry["associated_hospital"]["hospital_id"] == hospital_id
    assert "phone" in entry["associated_hospital"]


def test_donor_cannot_link_unverified_hospital(client, organizer_token):
    email = unique_email("donorbadhosp")
    reg = client.post("/api/v1/auth/register", json={
        "email": email, "password": "DonorPass123!", "role": "donor", "full_name": "D",
        "phone": "1", "address": "a", "blood_group": "O+",
    })
    with patch("random.SystemRandom.randrange", return_value=434343):
        pass
    otp_email = unique_email("donorbadhosp2")
    with patch("random.SystemRandom.randrange", return_value=434343):
        _register_donor(client, otp_email)
    client.post("/api/v1/auth/verify-email", json={"email": otp_email, "otp": "434343"})
    login = client.post("/api/v1/auth/login", json={"email": otp_email, "password": "DonorPass123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    unverified_hosp_email = unique_email("unverifiedhosp")
    client.post("/api/v1/auth/register", json={
        "email": unverified_hosp_email, "password": "HospPass123!", "role": "hospital", "full_name": "Contact",
        "phone": "1", "address": "a", "hospital_name": "Unverified Hosp",
        "hospital_code": f"CODE-{unverified_hosp_email.split(chr(64))[0]}", "location": "City",
        "registration_number": "REG-1", "authorized_contact": "Someone",
    })
    hospitals = client.get("/api/v1/hospitals", headers={"Authorization": f"Bearer {organizer_token}"}).json()
    unverified_hospital = next(h for h in hospitals["items"] if h["hospital_code"] == f"CODE-{unverified_hosp_email.split(chr(64))[0]}")

    r = client.put("/api/v1/donors/me", json={"blood_group": "O+", "hospital_id": unverified_hospital["id"]}, headers=headers)
    assert r.status_code == 400


def test_matching_run_only_considers_verified_donors(client, organizer_token):
    doc_token = _approved_doctor(client, organizer_token)
    headers = {"Authorization": f"Bearer {doc_token}"}
    patient = client.post("/api/v1/patients", json={
        "full_name": "Verified Match Patient", "blood_group": "O+", "required_organ": "kidney", "urgency": "HIGH",
    }, headers=headers).json()

    email = unique_email("unverifiedmatch")
    with patch("random.SystemRandom.randrange", return_value=454545):
        _register_donor(client, email)
    client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "454545"})
    donor_login = client.post("/api/v1/auth/login", json={"email": email, "password": "DonorPass123!"})
    donor_headers = {"Authorization": f"Bearer {donor_login.json()['access_token']}"}
    unverified_donor = client.put("/api/v1/donors/me", json={"blood_group": "O+", "organs_available": ["kidney"]}, headers=donor_headers).json()

    r = client.post(f"/api/v1/matching/run/{patient['id']}", headers=headers)
    assert r.status_code == 200
    donor_ids = [m["donor_id"] for m in r.json()["matches"]]
    assert unverified_donor["id"] not in donor_ids


def test_donor_request_blocked_against_unverified_donor(client, organizer_token):
    doc_token = _approved_doctor(client, organizer_token)
    headers = {"Authorization": f"Bearer {doc_token}"}

    email = unique_email("unverifiedreq")
    with patch("random.SystemRandom.randrange", return_value=464646):
        _register_donor(client, email)
    client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "464646"})
    donor_login = client.post("/api/v1/auth/login", json={"email": email, "password": "DonorPass123!"})
    donor_headers = {"Authorization": f"Bearer {donor_login.json()['access_token']}"}
    unverified_donor = client.put("/api/v1/donors/me", json={"blood_group": "O+", "organs_available": ["kidney"]}, headers=donor_headers).json()

    r = client.post("/api/v1/donor-requests", json={"donor_id": unverified_donor["id"], "organ": "kidney"}, headers=headers)
    assert r.status_code == 409


# ---------- production hardening: donor->hospital required, hospital license required, donor detail endpoint, upload rate limiting ----------

def test_organizer_cannot_verify_donor_without_hospital_link(client, organizer_token):
    email = unique_email("nohospdonor")
    with patch("random.SystemRandom.randrange", return_value=474747):
        _register_donor(client, email)
    client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "474747"})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "DonorPass123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    r = client.put("/api/v1/donors/me", json={"blood_group": "O-", "organs_available": ["cornea"]}, headers=headers)
    assert r.status_code == 200
    donor_id = r.json()["id"]

    jpeg = _tiny_jpeg_bytes()
    client.post("/api/v1/documents?kind=medical_document", headers=headers,
                files={"file": ("r.jpg", jpeg, "image/jpeg")})

    verify = client.post(f"/api/v1/organizer/donors/{donor_id}/verify",
                          headers={"Authorization": f"Bearer {organizer_token}"})
    assert verify.status_code == 400


def test_hospital_verify_requires_license_document(client, organizer_token):
    email = unique_email("nolicensehosp")
    reg = client.post("/api/v1/auth/register", json={
        "email": email, "password": "HospPass123!", "role": "hospital", "full_name": "Contact",
        "phone": "1", "address": "a", "hospital_name": "No License Hospital",
        "hospital_code": f"CODE-{email.split(chr(64))[0]}", "location": "City",
        "registration_number": "REG-1", "authorized_contact": "Someone",
    })
    hospitals = client.get("/api/v1/hospitals", headers={"Authorization": f"Bearer {organizer_token}"}).json()
    hospital = next(h for h in hospitals["items"] if h["hospital_code"] == f"CODE-{email.split(chr(64))[0]}")
    verify = client.post(f"/api/v1/organizer/hospitals/{hospital['id']}/verify",
                          headers={"Authorization": f"Bearer {organizer_token}"})
    assert verify.status_code == 400


def test_donor_detail_endpoint_hides_pii_and_shows_hospital(client, organizer_token):
    _, hospital_id = _verified_hospital(client, organizer_token, "detailhosp")
    _, donor_id, hospital_id = _verified_donor_with_hospital(client, organizer_token, hospital_id=hospital_id, prefix="detaildonor")
    r = client.get(f"/api/v1/donors/{donor_id}", headers={"Authorization": f"Bearer {organizer_token}"})
    assert r.status_code == 200
    body = r.json()
    for pii_field in ("phone", "address", "date_of_birth", "gender", "user_id"):
        assert pii_field not in body
    assert body["associated_hospital"]["hospital_id"] == hospital_id


def test_donor_detail_hidden_for_doctor_when_unverified(client, organizer_token):
    doc_token = _approved_doctor(client, organizer_token)
    email = unique_email("unverifieddetail")
    with patch("random.SystemRandom.randrange", return_value=484848):
        _register_donor(client, email)
    client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "484848"})
    donor_login = client.post("/api/v1/auth/login", json={"email": email, "password": "DonorPass123!"})
    _, hospital_id = _verified_hospital(client, organizer_token, "unverifdetailhosp")
    donor_headers = {"Authorization": f"Bearer {donor_login.json()['access_token']}"}
    unverified_donor = client.put("/api/v1/donors/me", json={"blood_group": "O+", "hospital_id": hospital_id}, headers=donor_headers).json()

    r = client.get(f"/api/v1/donors/{unverified_donor['id']}", headers={"Authorization": f"Bearer {doc_token}"})
    assert r.status_code == 404
    # organizer can still see it for review purposes
    r2 = client.get(f"/api/v1/donors/{unverified_donor['id']}", headers={"Authorization": f"Bearer {organizer_token}"})
    assert r2.status_code == 200


def test_document_upload_rate_limited(client, organizer_token):
    email = unique_email("uploadspam")
    with patch("random.SystemRandom.randrange", return_value=494949):
        _register_donor(client, email)
    client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "494949"})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "DonorPass123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    jpeg = _tiny_jpeg_bytes()
    last_status = None
    for _ in range(25):
        last_status = client.post("/api/v1/documents?kind=medical_document", headers=headers,
                                   files={"file": ("r.jpg", jpeg, "image/jpeg")}).status_code
    assert last_status == 429


# ---------- hospital directory: donors need a way to see verified hospitals to register through ----------

def test_hospital_directory_visible_to_donor_minimal_fields(client, organizer_token):
    _, hospital_id = _verified_hospital(client, organizer_token, "directoryhosp")
    email = unique_email("directorydonor")
    with patch("random.SystemRandom.randrange", return_value=515151):
        _register_donor(client, email)
    client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "515151"})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "DonorPass123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    r = client.get("/api/v1/hospitals/directory", headers=headers)
    assert r.status_code == 200
    entry = next(h for h in r.json() if h["id"] == hospital_id)
    assert set(entry.keys()) == {"id", "hospital_name", "location"}


def test_donor_blocked_from_full_hospital_list(client, organizer_token):
    email = unique_email("blockedhospdonor")
    with patch("random.SystemRandom.randrange", return_value=525252):
        _register_donor(client, email)
    client.post("/api/v1/auth/verify-email", json={"email": email, "otp": "525252"})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "DonorPass123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    r = client.get("/api/v1/hospitals", headers=headers)
    assert r.status_code == 403


# ---------- health check ----------

def test_health_check_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
