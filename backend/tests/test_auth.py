from backend.app.core.email import EmailService


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_user_registration_and_login(client):
    reg_payload = {
        "email": "doctor_test@qtransplant.org",
        "password": "SecurePassword123!",
        "full_name": "Dr. Alan Grant",
        "role": "doctor",
        "license_number": "MED-TEST-101",
        "specialization": "Cardiology",
        "department": "Surgery",
        "phone": "080-1234-5678"
    }

    # Register User
    res = client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code == 201
    user_data = res.json()
    assert user_data["email"] == "doctor_test@qtransplant.org"

    # Login User
    login_payload = {
        "email": "doctor_test@qtransplant.org",
        "password": "SecurePassword123!"
    }
    res_login = client.post("/api/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    tokens = res_login.json()
    assert "access_token" in tokens
    assert tokens["role"] == "doctor"


def test_doctor_camera_registration(client):
    camera_base64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP"
    data = {
        "email": "doc_camera@qtransplant.org",
        "password": "DoctorCameraPass1!",
        "full_name": "Dr. Camera Snap",
        "phone": "080-9999-8888",
        "license_number": "MED-CAM-500",
        "specialization": "Transplant Surgery",
        "department": "Surgery",
        "camera_image_base64": camera_base64
    }

    res = client.post("/api/v1/auth/register-doctor-camera", data=data)
    assert res.status_code == 201
    out = res.json()
    assert out["email"] == "doc_camera@qtransplant.org"
    assert out["is_approved"] is False


def test_forgot_and_reset_password_flow(client):
    # 1. Register a test user
    client.post("/api/v1/auth/register", json={
        "email": "reset_user@qtransplant.org",
        "password": "OldPassword123!",
        "full_name": "Reset User",
        "role": "patient"
    })

    # 2. Request forgot password
    res_forgot = client.post("/api/v1/auth/forgot-password", data={"email": "reset_user@qtransplant.org"})
    assert res_forgot.status_code == 200
    forgot_data = res_forgot.json()
    assert "token" in forgot_data
    token = forgot_data["token"]

    # 3. Reset password
    res_reset = client.post("/api/v1/auth/reset-password", data={
        "token": token,
        "new_password": "NewUpdatedPassword123!"
    })
    assert res_reset.status_code == 200

    # 4. Verify login with new password
    res_login = client.post("/api/v1/auth/login", json={
        "email": "reset_user@qtransplant.org",
        "password": "NewUpdatedPassword123!"
    })
    assert res_login.status_code == 200


def test_one_click_quick_approve_endpoint(client):
    # 1. Register doctor
    reg_res = client.post("/api/v1/auth/register", json={
        "email": "doc_oneclick@qtransplant.org",
        "password": "DoctorPass123!",
        "full_name": "Dr. One Click",
        "role": "doctor"
    })
    user_id = reg_res.json()["id"]

    # 2. Generate valid quick approval token
    token = EmailService.generate_quick_approval_token(user_id)

    # 3. GET /quick-approve
    res_approve = client.get(f"/api/v1/users/quick-approve?user_id={user_id}&approve=true&token={token}")
    assert res_approve.status_code == 200
    assert "Doctor Registration APPROVED" in res_approve.text

    # 4. Verify user is now approved in database
    res_login = client.post("/api/v1/auth/login", json={
        "email": "doc_oneclick@qtransplant.org",
        "password": "DoctorPass123!"
    })
    assert res_login.json()["is_approved"] is True
