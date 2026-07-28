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
