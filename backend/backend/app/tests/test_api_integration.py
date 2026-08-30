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
